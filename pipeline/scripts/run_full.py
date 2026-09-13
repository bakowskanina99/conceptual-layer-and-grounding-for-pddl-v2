"""Phase 4 full run: all 32 objects, one (variant, goal) chunk per invocation
(user's chosen batching -- 12 chunks total, ~1hr each, checkpointed).

Usage: python scripts/run_full.py <variant> <goal>
  variant: A | B | C | D
  goal: G2_real | G3_real | G4_real

Produces, under runs/full_run/ (append-only/accumulating across all 12 chunks):
  raw/                        raw prompt + per-attempt response+metadata, per object per variant per goal
  results.jsonl               incremental per-object log (one row per object per variant per goal)
  pddl/<variant>_<goal>/      compiled domain.pddl + problem.pddl for this chunk
  pddl/<variant>_<goal>/fd/   Fast Downward run output
  summary.txt                 per-chunk summary, appended after each chunk
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import config
from pipeline.compilers.compiler_formal.owl_classify import OwlClassifier
from pipeline.logging_.incremental_writer import IncrementalJsonlWriter
from pipeline.orchestrate import compile_and_plan_group, process_object

VARIANTS = ["A", "B", "C", "D"]
GOALS = ["G2_real", "G3_real", "G4_real"]

RUN_DIR = config.RUNS_DIR / "full_run"
RAW_DIR = RUN_DIR / "raw"
PDDL_DIR = RUN_DIR / "pddl"
RESULTS_PATH = RUN_DIR / "results.jsonl"
SUMMARY_PATH = RUN_DIR / "summary.txt"


def load_reference_labels() -> dict:
    with open(config.REFERENCE_LABELS_PATH, "r", encoding="utf-8") as f:
        rows = json.load(f)
    return {row["object_id"]: row for row in rows}


def all_object_ids() -> list[str]:
    return sorted(load_reference_labels().keys(), key=lambda s: int(s.split("_")[1]))


def run_chunk(variant: str, goal: str) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    reference_labels = load_reference_labels()
    object_ids = all_object_ids()

    reasoner_ttl = {"B": config.WELL_FORMED_TTL, "C": config.WELL_FORMED_TTL, "D": config.WEAKENED_TTL}
    reasoners = {variant: OwlClassifier(reasoner_ttl[variant])} if variant in reasoner_ttl else {}

    print(f"=== Chunk: variant={variant} goal={goal} ({len(object_ids)} objects) ===", flush=True)
    processed = []
    with IncrementalJsonlWriter(RESULTS_PATH) as writer:
        for object_id in object_ids:
            print(f"  {object_id} ...", end=" ", flush=True)
            result = process_object(object_id, variant, goal, reference_labels, reasoners, writer, raw_dir=RAW_DIR)
            processed.append(result)
            status = "DROPPED (JSON parse failure)" if result.get("dropped") else result.get("grounding_status", "ok")
            print(status, flush=True)

    group_dir = PDDL_DIR / f"{variant}_{goal}"
    group_result = compile_and_plan_group(variant, goal, processed, group_dir)

    n_dropped = sum(1 for p in processed if p.get("dropped"))
    summary_lines = [
        f"--- variant={variant} goal={goal} ---",
        f"objects processed: {len(processed)}, dropped (JSON parse failure): {n_dropped}",
        f"domain_size (Definition 5.3): {group_result['domain_size']}",
    ]
    if group_result["fd_result"] is None:
        summary_lines.append("Fast Downward: NOT RUN (no admitted/pending objects compiled into a problem)")
    else:
        fd = group_result["fd_result"]
        summary_lines.append(
            f"Fast Downward: success={fd['success']} elapsed={fd['elapsed_seconds']:.3f}s "
            f"expanded_states={fd['expanded_states']} returncode={fd['returncode']}"
        )
    summary_lines.append("")

    with open(SUMMARY_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print("\n".join(summary_lines))
    print(f"Raw prompts/responses: {RAW_DIR}")
    print(f"Per-object log: {RESULTS_PATH}")
    print(f"Compiled PDDL: {group_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in VARIANTS or sys.argv[2] not in GOALS:
        print(f"Usage: python {sys.argv[0]} <variant: {VARIANTS}> <goal: {GOALS}>")
        sys.exit(1)
    run_chunk(sys.argv[1], sys.argv[2])
