"""Phase 5: raw aggregate numbers for the three pairwise comparisons (A vs C,
B vs C, C vs D), per compiler_pipeline_spec.md's "Aggregate metrics"
section. Results only -- no narrative interpretation (user's brief).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import config
from pipeline.goals import GOALS as GOAL_DEFS
from pipeline.goals import relevant_domain
from pipeline.hierarchy import WELL_FORMED_HIERARCHY
from pipeline.hierarchy import ancestors_inclusive as hier_ancestors_inclusive

RUN_DIR = config.RUNS_DIR / "full_run"
RESULTS_PATH = RUN_DIR / "results.jsonl"
PDDL_DIR = RUN_DIR / "pddl"

VARIANTS = ["A", "B", "C", "D"]
GOALS = ["G2_real", "G3_real", "G4_real"]


def load_rows() -> list[dict]:
    return [json.loads(l) for l in open(RESULTS_PATH, encoding="utf-8")]


def fd_stats(variant: str, goal: str) -> dict:
    fd_dir = PDDL_DIR / f"{variant}_{goal}" / "fd"
    sas_plan = fd_dir / "sas_plan"
    if not sas_plan.exists():
        return {"success": False, "elapsed_seconds": None, "expanded_states": None, "plan_objects": None}
    plan_text = sas_plan.read_text(encoding="utf-8")
    n_actions = sum(1 for line in plan_text.splitlines() if line.strip().startswith("("))
    return {"success": True, "plan_actions": n_actions}


_DOMAIN_SIZE_CACHE: dict[tuple[str, str], int] = {}


def domain_size_for(rows: list[dict], variant: str, goal: str) -> int | None:
    """Uses the ACTUAL tested pipeline functions (compile_domain_structure /
    compile_naive) -- NOT a regex re-parse of the .pddl text. A first version
    of this function re-derived domain_size by regexing domain.pddl and
    produced 63 for A/G2_real where every other independent check (the run
    itself, D17's fix verification, the user's own arithmetic for D) agrees
    on 62/23/etc. -- caught before being reported, not after. Domain size for
    B/C/D depends only on the type hierarchy and goal (no per-object data),
    so it's recomputed directly; for A it depends on which objects were
    actually included, so it's recomputed from the saved raw responses."""
    key = (variant, goal)
    if key in _DOMAIN_SIZE_CACHE:
        return _DOMAIN_SIZE_CACHE[key]

    if variant != "A":
        from pipeline.compilers.compiler_formal.pddl_compile import compile_domain_structure
        from pipeline.goals import active_domain
        from pipeline.hierarchy import WEAKENED_HIERARCHY, WELL_FORMED_HIERARCHY

        hierarchy = WEAKENED_HIERARCHY if variant == "D" else WELL_FORMED_HIERARCHY
        active = set(hierarchy) if variant == "B" else active_domain(hierarchy, goal)
        size = compile_domain_structure(hierarchy, active)["size"]
    else:
        from pipeline.compilers.compiler_naive import compile_naive

        agent_objects = []
        for r in rows_for(rows, variant, goal):
            if r["json_parse_failure"]:
                continue
            agent_objects.append(json.loads(r["raw_response_text"])["objects"][0])
        size = compile_naive(agent_objects)["domain_size"]

    _DOMAIN_SIZE_CACHE[key] = size
    return size


def rows_for(rows: list[dict], variant: str, goal: str) -> list[dict]:
    return [r for r in rows if r["variant"] == variant and r["goal"] == goal]


def classify_type_match(reasoner_type: str | None, reference_type: str | None) -> str | None:
    """Definition 3.4's "undetermined" case, applied to the accuracy metric:
    a reasoner_type that is a strict ANCESTOR of reference_type is not wrong
    -- it is exactly what happens when a required distinguishing feature was
    never observed/reported (e.g. Variant C's Step 4 deliberately minimal
    reporting), so classification correctly stops at a less-specific-but-not-
    incorrect type. Conflating this with a genuine sibling/unrelated
    misclassification (e.g. Fruit reported for a true Vegetable) understates
    the frame's accuracy and overstates its error rate -- caught directly
    from the data (DairyProduct->GroceryItem->StoreItem for obj_002 as goals
    narrow, vs. a stable Fruit/Vegetable confusion for obj_012)."""
    if reasoner_type is None or reference_type is None:
        return None  # ungroundable (ambiguous/inconsistent) or missing reference -- not applicable here
    if reasoner_type == reference_type:
        return "exact_match"
    if reference_type not in WELL_FORMED_HIERARCHY:
        return "genuine_misclassification"  # defensive; Phase 3 already validated every reference_type
    ancestors_of_ref = set(hier_ancestors_inclusive(WELL_FORMED_HIERARCHY, reference_type)) - {reference_type}
    return "ancestor_fallback" if reasoner_type in ancestors_of_ref else "genuine_misclassification"


def accuracy_breakdown(rows_subset: list[dict], variant: str) -> dict:
    """Four mutually exclusive, exhaustive categories over non-parse-failure
    rows: exact_match, ancestor_fallback (Definition 3.4 undetermined, NOT an
    error), genuine_misclassification (a real wrong answer), and ungroundable
    (ambiguous_grounding/reasoner_inconsistent -- already reported separately
    as amb_rate/inconsistent_rate, included here too so the four buckets sum
    to the full denominator with nothing silently dropped). Variant A has no
    formal hierarchy at all, so the ancestor-fallback distinction does not
    apply to it -- only exact_match (case/underscore-insensitive) vs.
    everything else is reported for A, unchanged from before."""
    non_failed = [r for r in rows_subset if not r["json_parse_failure"]]
    n = len(non_failed)
    if n == 0:
        return {"n": 0}

    if variant == "A":
        exact = sum(
            1 for r in non_failed
            if r.get("agent_proposed_type") and r.get("reference_type")
            and re.sub(r"[\s_]+", "", r["agent_proposed_type"]).lower() == re.sub(r"[\s_]+", "", r["reference_type"]).lower()
        )
        return {"n": n, "exact_match_rate": exact / n, "exact_match_n": exact,
                "ancestor_fallback_rate": None, "genuine_misclassification_rate": (n - exact) / n,
                "genuine_misclassification_n": n - exact, "ungroundable_rate": None}

    counts = Counter(classify_type_match(r.get("reasoner_type"), r.get("reference_type")) for r in non_failed)
    ungroundable = sum(1 for r in non_failed if r.get("grounding_status") in ("ambiguous_grounding", "reasoner_inconsistent", "no_type_inferred"))
    exact_n = counts.get("exact_match", 0)
    anc_n = counts.get("ancestor_fallback", 0)
    mis_n = counts.get("genuine_misclassification", 0)
    # classify_type_match returns None for ungroundable rows (no reasoner_type) --
    # confirm the four buckets exhaust n with nothing double-counted or dropped.
    assert exact_n + anc_n + mis_n + ungroundable == n, (
        f"accuracy_breakdown row-accounting mismatch: {exact_n}+{anc_n}+{mis_n}+{ungroundable} != {n}"
    )
    return {
        "n": n,
        "exact_match_rate": exact_n / n, "exact_match_n": exact_n,
        "ancestor_fallback_rate": anc_n / n, "ancestor_fallback_n": anc_n,
        "genuine_misclassification_rate": mis_n / n, "genuine_misclassification_n": mis_n,
        "ungroundable_rate": ungroundable / n, "ungroundable_n": ungroundable,
    }


def grounding_rates(rows_subset: list[dict]) -> dict:
    non_failed = [r for r in rows_subset if not r["json_parse_failure"]]
    n = len(non_failed)
    if n == 0:
        return {"n": 0, "ambiguous_rate": None, "inconsistent_rate": None, "resolved_rate": None}
    amb = sum(1 for r in non_failed if r.get("grounding_status") == "ambiguous_grounding")
    inc = sum(1 for r in non_failed if r.get("grounding_status") == "reasoner_inconsistent")
    res = sum(1 for r in non_failed if r.get("grounding_status") == "resolved")
    return {"n": n, "ambiguous_rate": amb / n, "ambiguous_n": amb,
            "inconsistent_rate": inc / n, "inconsistent_n": inc,
            "resolved_rate": res / n, "resolved_n": res}


def shacl_agreement_rate(rows_subset: list[dict], goal: str) -> dict:
    """SCOPED to objects whose reasoner_type is within D_rel(G) (the goal's
    relevant domain, Definition 4.2) -- found directly from the data (not a
    hypothesis): all 9 non-grocery objects (obj_024-032) disagreed in EVERY
    goal, 100% of the time, with zero variation -- not a coincidence but a
    structural, deterministic consequence of comparing two different
    questions. `agent_shacl_agreement` compares the agent's COMBINED
    relevance+admissibility decision (`included_in_description`, false for
    these objects because they are OUTSIDE D_rel(G) per the prompt's own
    Step 2) against SHACL's admissibility-ONLY verdict (vacuously "admitted"
    for these objects, since G3RealGoalShape/G4RealGoalShape's sh:targetClass
    is GroceryItem and never even targets a HouseholdItem/ClothingItem/
    ElectronicsItem individual at all -- and for G2_real, the D18 vacuous-
    admission fix applies to every resolved object regardless of relevance).
    These are two different questions (Lemma 4.1 is about admissibility, not
    relevance) that will ALWAYS disagree for out-of-scope objects by
    construction, contributing a constant, uninformative "wrong" to the
    denominator. Excluded here, and the exclusion count is reported
    explicitly (not silently shrinking the denominator without a trace)."""
    rel_domain = relevant_domain(WELL_FORMED_HIERARCHY, GOAL_DEFS[goal]["target_types"])
    checked = [r for r in rows_subset if r.get("agent_shacl_agreement") is not None]
    in_scope = [r for r in checked if r.get("reasoner_type") in rel_domain]
    out_of_scope = [r for r in checked if r.get("reasoner_type") not in rel_domain]
    agree = [r for r in in_scope if r["agent_shacl_agreement"] is True]
    n = len(in_scope)
    return {
        "rate": len(agree) / n if n else None, "agree_n": len(agree), "n": n,
        "excluded_out_of_scope_n": len(out_of_scope),
    }


def print_overview_table(rows: list[dict], variants: list[str]) -> None:
    header = f"{'variant':8}{'goal':10}{'domain_size':13}{'exact_match':14}{'amb_rate':16}{'inconsist_rate':16}{'FD_actions':10}"
    print(header)
    print("-" * len(header))
    for v in variants:
        for g in GOALS:
            subset = rows_for(rows, v, g)
            ds = domain_size_for(rows, v, g)
            acc = accuracy_breakdown(subset, v)
            gr = grounding_rates(subset)
            fd = fd_stats(v, g)
            exact_str = f"{acc['exact_match_rate']:.3f} ({acc['exact_match_n']}/{acc['n']})" if acc.get("exact_match_rate") is not None else "n/a"
            amb_str = f"{gr['ambiguous_rate']:.3f} ({gr['ambiguous_n']}/{gr['n']})" if gr["ambiguous_rate"] is not None else "n/a"
            inc_str = f"{gr['inconsistent_rate']:.3f} ({gr['inconsistent_n']}/{gr['n']})" if gr["inconsistent_rate"] is not None else "n/a"
            fd_str = str(fd.get("plan_actions", "N/A")) if fd["success"] else "NOT RUN"
            print(f"{v:8}{g:10}{str(ds):13}{exact_str:14}{amb_str:16}{inc_str:16}{fd_str:10}")


def print_accuracy_breakdown_table(rows: list[dict], variants: list[str]) -> None:
    header = f"{'variant':8}{'goal':10}{'exact_match':16}{'ancestor_fallback':20}{'genuine_misclass':18}{'ungroundable':14}"
    print(header)
    print("-" * len(header))
    for v in variants:
        for g in GOALS:
            subset = rows_for(rows, v, g)
            acc = accuracy_breakdown(subset, v)
            if acc.get("n", 0) == 0:
                print(f"{v:8}{g:10}(no non-parse-failure rows)")
                continue

            def fmt(rate_key, n_key):
                rate, n = acc.get(rate_key), acc.get(n_key)
                return f"{rate:.3f} ({n}/{acc['n']})" if rate is not None else "n/a"

            print(f"{v:8}{g:10}{fmt('exact_match_rate','exact_match_n'):16}"
                  f"{fmt('ancestor_fallback_rate','ancestor_fallback_n'):20}"
                  f"{fmt('genuine_misclassification_rate','genuine_misclassification_n'):18}"
                  f"{fmt('ungroundable_rate','ungroundable_n'):14}")


def print_shacl_agreement_table(rows: list[dict], variants: list[str]) -> None:
    header = f"{'variant':8}{'goal':10}{'shacl_agree_scoped':22}{'excluded_out_of_scope':22}"
    print(header)
    print("-" * len(header))
    for v in variants:
        if v not in ("C", "D"):
            continue
        for g in GOALS:
            subset = rows_for(rows, v, g)
            s = shacl_agreement_rate(subset, g)
            rate_str = f"{s['rate']:.3f} ({s['agree_n']}/{s['n']})" if s["rate"] is not None else "n/a"
            print(f"{v:8}{g:10}{rate_str:22}{s['excluded_out_of_scope_n']:<22}")


def main() -> None:
    rows = load_rows()
    print(f"Total rows: {len(rows)}\n")

    print("=" * 100)
    print("OVERVIEW -- all 12 (variant, goal) combinations (exact_match only; see breakdown below)")
    print("=" * 100)
    print_overview_table(rows, VARIANTS)

    print()
    print("=" * 100)
    print("ACCURACY BREAKDOWN -- exact_match / ancestor_fallback (Def. 3.4 undetermined, NOT an error) /")
    print("genuine_misclassification / ungroundable -- four categories, exhaustive, verified to sum to n")
    print("=" * 100)
    print_accuracy_breakdown_table(rows, VARIANTS)

    print()
    print("=" * 100)
    print("SHACL AGREEMENT, SCOPED to D_rel(G) -- excludes objects structurally outside the goal's relevant")
    print("domain (comparing agent relevance+admissibility vs. SHACL admissibility-only is not a fair test")
    print("for them -- see shacl_agreement_rate() docstring). C/D only (B has no Stage 3).")
    print("=" * 100)
    print_shacl_agreement_table(rows, VARIANTS)

    print()
    print("=" * 100)
    print("8.1 A vs C (headline)")
    print("=" * 100)
    print_overview_table(rows, ["A", "C"])
    print()
    print_accuracy_breakdown_table(rows, ["A", "C"])

    print()
    print("=" * 100)
    print("8.2 B vs C")
    print("=" * 100)
    print_overview_table(rows, ["B", "C"])
    print()
    print_accuracy_breakdown_table(rows, ["B", "C"])

    print()
    print("=" * 100)
    print("8.3 C vs D (ambiguous-grounding / reasoner-inconsistent rates -- headline ablation stat)")
    print("=" * 100)
    print_overview_table(rows, ["C", "D"])
    print()
    print_accuracy_breakdown_table(rows, ["C", "D"])

    print()
    print("=" * 100)
    print("Parse-failure (dropped) counts, per variant+goal")
    print("=" * 100)
    for v in VARIANTS:
        for g in GOALS:
            subset = rows_for(rows, v, g)
            dropped = sum(1 for r in subset if r["json_parse_failure"])
            print(f"  {v} {g}: {dropped}/{len(subset)} dropped")


if __name__ == "__main__":
    main()
