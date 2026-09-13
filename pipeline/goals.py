"""Real-data goal specifications (formal_artifacts_owl_pddl_v2.md, Part A3)
and D(G) computation (Definitions 4.1-4.5), against WELL_FORMED_HIERARCHY.

G4_real's R(G) uses calories<=55 (not nutriscoreMatch>=60) and Phi(G3_real)/
Phi(G4_real) are phrased against vegan_attribute_match. This deliberately does
NOT produce type-level exclusion of DairyProduct/MeatProduct for the real
goals -- a deliberately accepted, reported asymmetry with the symbolic
walkthrough, not a bug.
"""

from __future__ import annotations

from pipeline import config
from pipeline.hierarchy import descendants_inclusive, required_cumulative

GOALS = {
    "G1_real": {"target_types": {"StoreItem"}, "phi": {}, "r": {}},
    "G2_real": {"target_types": {"GroceryItem"}, "phi": {}, "r": {}},
    "G3_real": {"target_types": {"GroceryItem"}, "phi": {"vegan_attribute_match": 100}, "r": {}},
    "G4_real": {
        "target_types": {"GroceryItem"},
        "phi": {"vegan_attribute_match": 100},
        "r": {"calories": ("<=", config.G4_REAL_CALORIE_THRESHOLD)},
    },
}

# Same wording used verbatim across all four variants' {SHOPPING_GOAL_IN_PLAIN_LANGUAGE}
# slot (agent_prompts_ABCD.md) -- consistency across variants is part of the
# experimental design, so this text is defined once, here, not per-variant.
PLAIN_LANGUAGE_GOAL_TEXT = {
    "G2_real": "Buy the grocery items needed for the household -- ignore anything that isn't a grocery item.",
    "G3_real": "Buy only the vegan grocery items needed for the household -- ignore anything that does not help complete this specific goal.",
    "G4_real": "Buy only vegan grocery items that are also low-calorie (suitable for a light diet) -- ignore anything that does not help complete this specific goal.",
}

# G2_real has no SHACL shape at all (Phi=R=empty -- type-level filtering only,
# already resolved by OWL classification, per formal_artifacts_owl_pddl_v2.md Part B).
GOAL_SHAPE_NAMES = {
    "G3_real": "G3RealGoalShape",
    "G4_real": "G4RealGoalShape",
}


def relevant_domain(hierarchy: dict, target_types: set[str]) -> set[str]:
    """D_rel(G) -- Definition 4.2: union of down-sets of the target types."""
    result: set[str] = set()
    for t_g in target_types:
        result |= descendants_inclusive(hierarchy, t_g)
    return result


def phi_consistent_with_contract(phi: dict, k_plus: dict) -> bool:
    """Phi(G) ~ K(t) -- Definition 4.3. K-(t) is empty for every type in this
    hierarchy (no owl:complementOf restrictions in Part A), so only the K+/K+
    conflict case applies here."""
    for f, v in phi.items():
        if f in k_plus and k_plus[f] != v:
            return False
    return True


def admissible_domain(hierarchy: dict, target_types: set[str], phi: dict) -> set[str]:
    """D_adm(G) -- Definition 4.4."""
    rel = relevant_domain(hierarchy, target_types)
    return {t for t in rel if phi_consistent_with_contract(phi, required_cumulative(hierarchy, t))}


def active_domain(hierarchy: dict, goal_name: str) -> set[str]:
    """D(G) -- Definition 4.5."""
    g = GOALS[goal_name]
    return admissible_domain(hierarchy, g["target_types"], g["phi"])
