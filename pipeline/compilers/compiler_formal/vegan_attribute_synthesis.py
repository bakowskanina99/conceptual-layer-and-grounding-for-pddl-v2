"""Stage 1b: `veganAttributeMatch` synthesis (real-data goals only).

See compiler_pipeline_spec.md ("Stage 1b -- `veganAttributeMatch` synthesis from
the agent's `is_vegan`"). Summary: `G3RealGoalShape`/`G4RealGoalShape` need
`store:veganAttributeMatch`, but the agent is never asked for it directly -- it
is not in the agent-facing ontology JSON, because an 8B VLM cannot plausibly
estimate an OFF-internal ingredient-database match score from a photograph.
Instead this module derives it deterministically from the agent's own
(already-requested) `is_vegan` property, immediately after Stage 0 coercion and
before the RDF individual is handed to the reasoner.

The synthesized value is an ADDITIONAL triple, asserted alongside
`store:isVegan` (which stays asserted too) -- not a replacement for it.
"""

from __future__ import annotations

# G2_real has an empty Phi(G)/R(G) (formal_artifacts_owl_pddl_v2.md, Part A3) --
# nothing to synthesize for it. Only G3_real/G4_real's goal shapes reference
# veganAttributeMatch at all.
REAL_DATA_GOALS_USING_VEGAN_ATTRIBUTE_MATCH = {"G3_real", "G4_real"}


def synthesize_vegan_attribute_match(coerced_is_vegan: bool | None) -> int | None:
    """coerced_is_vegan is Stage 0's output for the "is_vegan" property: True /
    False / None. None covers both an explicit agent "unknown" and an
    unparsable response -- Stage 0 already collapses those two cases, and this
    function must not try to re-distinguish them.

    Returns the value to assert as store:veganAttributeMatch, or None to leave
    it unasserted entirely (open-world "pending", Definition 3.2 -- never
    coerced to a default of 0 or 100).
    """
    if coerced_is_vegan is True:
        return 100
    if coerced_is_vegan is False:
        return 0
    return None


def compute(coerced_properties: dict, goal_name: str) -> dict:
    """Given an object's Stage-0-coerced properties dict (property_name ->
    coerced value, e.g. {"is_vegan": True, "calories": 52.0, ...}) and the
    current goal name, return the Stage 1b log fields for this object.

    Always returns the same three keys, even when synthesis does not apply,
    so every object's per-row log carries this pair (unified log schema's
    `derived_vegan_attribute_match` column) -- a G3RealGoalShape/G4RealGoalShape
    admission decision must be traceable back to the exact agent statement it
    came from, not just the derived number.

    Does NOT applies when:
    - goal_name is not one of the real-data goals that reference
      veganAttributeMatch (G2_real has no Phi(G)/R(G) to check at all), or
    - the object's own reported properties never included "is_vegan" in the
      first place (e.g. HouseholdItem/ClothingItem/ElectronicsItem -- is_vegan
      is only in GroceryItem's feat(t), Definition 3.5).
    """
    applicable = (
        goal_name in REAL_DATA_GOALS_USING_VEGAN_ATTRIBUTE_MATCH
        and "is_vegan" in coerced_properties
    )

    if not applicable:
        return {
            "stage1b_applicable": False,
            "stage1b_source_is_vegan": coerced_properties.get("is_vegan"),
            "derived_vegan_attribute_match": None,
        }

    coerced_is_vegan = coerced_properties["is_vegan"]
    derived = synthesize_vegan_attribute_match(coerced_is_vegan)

    return {
        "stage1b_applicable": True,
        "stage1b_source_is_vegan": coerced_is_vegan,
        "derived_vegan_attribute_match": derived,
    }
