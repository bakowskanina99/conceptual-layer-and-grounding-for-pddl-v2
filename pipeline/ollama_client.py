"""Ollama client: one call per object, qwen3-vl:8b,
num_ctx>=8192 (user's brief -- a smaller context window caused silent
failures in a prior pipeline when a full ontology JSON was embedded),
deterministic decoding (temperature=0, fixed seed -- adopted for
reproducibility and to make the Variant-B goal-invariance check meaningful).

Captures the raw request (image bytes redacted, everything else intact) and
raw response text for every call -- checkpoints require raw evidence, not a
paraphrase of what the model said.
"""

from __future__ import annotations

import base64
import json
import re
import time

import requests

from pipeline import config


def _encode_image(image_path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def call_agent(
    prompt_text: str,
    image_path,
    model: str = config.MODEL_NAME,
    num_ctx: int = config.NUM_CTX,
    temperature: float = config.TEMPERATURE,
    seed: int = config.SEED,
    timeout: int = 300,
) -> dict:
    """One Ollama call, one object, one image. Returns the raw request
    (image redacted to a length marker, not omitted, so context-size
    reasoning about a specific call is still possible from the log) and raw
    response text -- callers own JSON-parsing (see `extract_json`)."""
    image_b64 = _encode_image(image_path)
    payload = {
        "model": model,
        "prompt": prompt_text,
        "images": [image_b64],
        "stream": False,
        "options": {
            "num_ctx": num_ctx,
            "temperature": temperature,
            "seed": seed,
        },
    }

    start = time.time()
    resp = requests.post(f"{config.OLLAMA_HOST}/api/generate", json=payload, timeout=timeout)
    resp.raise_for_status()
    elapsed = time.time() - start
    data = resp.json()
    raw_response_text = data.get("response", "")

    logged_request = dict(payload)
    logged_request["images"] = [f"<base64 image, {len(image_b64)} chars, redacted from log>"]

    return {
        "raw_request": logged_request,
        "raw_prompt_text": prompt_text,
        "raw_response_text": raw_response_text,
        "elapsed_seconds": elapsed,
        "ollama_metadata": {k: v for k, v in data.items() if k != "response"},
    }


def extract_json(raw_text: str) -> tuple[dict | None, bool]:
    """Returns (parsed_json_or_None, first_attempt_valid). Models sometimes
    wrap JSON in markdown fences or add stray whitespace/prose despite
    explicit instructions not to -- a fallback extraction is attempted, but
    `first_attempt_valid` tracks whether the RAW response parsed with no
    cleanup at all, since that is the reliability statistic
    agent_prompts_ABCD.md's "Practical notes" asks for ("first-attempt valid
    JSON" rate), given Qwen3-VL-8B's documented schema-adherence issues."""
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text), True
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0)), False
        except json.JSONDecodeError:
            pass
    return None, False
