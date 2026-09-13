"""Phase 2 smoke test: full chain (agent call -> JSON -> compiler -> PDDL ->
Fast Downward) on 5 objects, across all four variants, for goal G3_real.

5 objects (3 grocery + 2 non-grocery, per the user's own fallback instruction
since none were specified): obj_001 (Fruit, vegan), obj_002 (DairyProduct,
non-vegan), obj_011 (PackagedFood, vegan), obj_024 (HouseholdItem),
obj_029 (ClothingItem).

Produces, under runs/smoke_test/:
  raw/                  raw prompt + raw response, per object per variant
  results.jsonl         incremental per-object log
  pddl/<variant>/       compiled domain.pddl + problem.pddl per variant
  pddl/<variant>/fd/    Fast Downward run output (stdout/stderr/sas_plan)
  summary.txt           the checkpoint deliverables, human-readable
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

GOAL_NAME = "G3_real"
OBJECT_IDS = ["obj_001", "obj_002", "obj_011", "obj_024", "obj_029"]
VARIANTS = ["A", "B", "C", "D"]

RUN_DIR = config.RUNS_DIR / "smoke_test"
RAW_DIR = RUN_DIR / "raw"
PDDL_DIR = RUN_DIR / "pddl"
RESULTS_PATH = RUN_DIR / "results.jsonl"
SUMMARY_PATH = RUN_DIR / "summary.txt"


def load_reference_labels() -> dict:
    with open(config.REFERENCE_LABELS_PATH, "r", encoding="utf-8") as f:
        rows = json.load(f)
    return {row["object_id"]: row for row in rows}


def run_variant(variant: str) -> None:
    """Runs ONE variant's 5 objects and appends its summary -- deliberately
    scoped to one variant per invocation (not all 4) so a crash surfaces
    within ~5 calls (~8-12 minutes) instead of after all 20, and so results
    already written for earlier variants are never at risk from a later
    variant's failure. results.jsonl and summary.txt are both append-only
    across invocations."""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    reference_labels = load_reference_labels()

    reasoner_ttl = {"B": config.WELL_FORMED_TTL, "C": config.WELL_FORMED_TTL, "D": config.WEAKENED_TTL}
    reasoners = {variant: OwlClassifier(reasoner_ttl[variant])} if variant in reasoner_ttl else {}

    print(f"=== Variant {variant} (goal={GOAL_NAME}) ===", flush=True)
    processed = []
    with IncrementalJsonlWriter(RESULTS_PATH) as writer:
        for object_id in OBJECT_IDS:
            print(f"  {object_id} ...", end=" ", flush=True)
            result = process_object(object_id, variant, GOAL_NAME, reference_labels, reasoners, writer, raw_dir=RAW_DIR)
            processed.append(result)
            status = "DROPPED (JSON parse failure)" if result.get("dropped") else result.get("grounding_status", "ok")
            print(status, flush=True)

    group_dir = PDDL_DIR / variant
    group_result = compile_and_plan_group(variant, GOAL_NAME, processed, group_dir)

    summary_lines = [f"--- Variant {variant} ---", f"domain_size (Definition 5.3): {group_result['domain_size']}"]
    if group_result["fd_result"] is None:
        summary_lines.append("Fast Downward: NOT RUN (no admitted/pending objects compiled into a problem)")
    else:
        fd = group_result["fd_result"]
        summary_lines.append(
            f"Fast Downward: success={fd['success']} elapsed={fd['elapsed_seconds']:.3f}s "
            f"expanded_states={fd['expanded_states']} returncode={fd['returncode']}"
        )
        if not fd["success"]:
            summary_lines.append(f"  stdout (tail): {fd['stdout'][-500:]}")
            summary_lines.append(f"  stderr (tail): {fd['stderr'][-500:]}")
    summary_lines.append("")

    with open(SUMMARY_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print("\n".join(summary_lines))
    print(f"Raw prompts/responses: {RAW_DIR}")
    print(f"Per-object log: {RESULTS_PATH}")
    print(f"Compiled PDDL: {group_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in VARIANTS:
        print(f"Usage: python {sys.argv[0]} <variant>  where variant is one of {VARIANTS}")
        sys.exit(1)
    run_variant(sys.argv[1])
