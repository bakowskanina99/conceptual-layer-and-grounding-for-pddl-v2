"""Fast Downward subprocess wrapper (built from source,
self-contained, no build toolchain needed on PATH at run time).

Follows experimental_design_v2.md's protocol: a fixed satisficing alias
(lama-first), recording wall-clock time and expanded states. Never raises on
planner failure -- "If Variant A's agent-generated PDDL fails to compile or
fails to produce a valid plan at all for some goals... report this as a
result, not a discarded run" (experimental_design_v2.md) -- generalized here
to any variant, since an unusable domain is informative regardless of which
variant produced it.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

from pipeline import config


def run_fast_downward(
    domain_path,
    problem_path,
    workdir,
    alias: str = config.FAST_DOWNWARD_ALIAS,
    timeout: int = 120,
) -> dict:
    if config.FAST_DOWNWARD_ENTRY_POINT is None or not Path(config.FAST_DOWNWARD_ENTRY_POINT).exists():
        raise RuntimeError(
            f"Fast Downward entry point not found: {config.FAST_DOWNWARD_ENTRY_POINT}. "
            "Build it from source and point config.FAST_DOWNWARD_ENTRY_POINT at the driver."
        )

    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    sas_plan = workdir / "sas_plan"
    if sas_plan.exists():
        sas_plan.unlink()

    # domain/problem paths must be absolute: the subprocess runs with
    # cwd=workdir, so a relative path would resolve against the WRONG
    # directory (caught empirically -- FD's translator reported "No such
    # file" for a path that existed relative to the caller's cwd).
    domain_path = Path(domain_path).resolve()
    problem_path = Path(problem_path).resolve()

    cmd = [sys.executable, str(config.FAST_DOWNWARD_ENTRY_POINT), "--alias", alias, str(domain_path), str(problem_path)]

    start = time.time()
    timed_out = False
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout)
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        returncode = None
    elapsed = time.time() - start

    plan_found = sas_plan.exists()
    plan_text = sas_plan.read_text(encoding="utf-8") if plan_found else None

    return {
        "success": plan_found and not timed_out,
        "timed_out": timed_out,
        "returncode": returncode,
        "elapsed_seconds": elapsed,
        "plan_text": plan_text,
        "expanded_states": _extract_expanded_states(stdout),
        "stdout": stdout,
        "stderr": stderr,
        "cmd": cmd,
    }


def _extract_expanded_states(stdout: str) -> int | None:
    m = re.search(r"Expanded (\d+) state", stdout)
    return int(m.group(1)) if m else None
