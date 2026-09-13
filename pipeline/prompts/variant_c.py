"""Variant C -- conceptual system + goal-dependent restriction (main proposed
mechanism). Prompt text verbatim from agent_prompts_ABCD.md, "Variant C". The
{LIST_OF_TYPES_IN_D_G} / {LIST_OF_REQUIRED_FEATURE_VALUES} /
{LIST_OF_THRESHOLDS_OR_NONE} placeholders are filled from goals.py's D(G)/
Phi(G)/R(G) computation for the current goal -- the spec does not prescribe
an exact list-rendering format, only that these be "filled programmatically
per goal" (agent_prompts_ABCD.md, "Practical notes"), so a plain,
human-readable rendering is used."""

from pipeline.prompts.ontology_json import WELL_FORMED_ONTOLOGY_JSON
from pipeline.prompts.shared_schema import WORKED_EXAMPLE, shared_output_schema_block

_TEMPLATE = """You are a shopping assistant agent operating with a formal conceptual system that
defines every category of item that can exist in this hypermarket, and the
properties and requirements associated with each category. If a category is not
listed below, it does not exist in this system — do not invent new categories.

Your task is: {goal}

CONCEPTUAL SYSTEM (identical structure to Variant B):

{ontology_json}

ACTIVE DOMAIN FOR THIS TASK — you have additionally been told which types are
relevant to your current goal, and what requirements your goal places on their
properties:

  Relevant types for this goal (D(G)): {dg_types}
  Required property values for this goal (Phi(G)): {phi}
  Threshold constraints for this goal (R(G), if any): {r}

For each of the {n} photographs:

1. Determine the object's most specific type, exactly as in Variant B.
2. If the determined type is NOT in the active domain list above (and is not a
   subtype of one of those types), set "included_in_description": false with
   "reason_if_excluded": "type outside goal-relevant domain", and only report
   "proposed_type" — you do not need to report its properties in this case. This
   saves you work: do not describe objects you have already determined are outside
   the active domain.
3. If the determined type IS in the active domain, but its own type contract
   already fixes a property to a value that contradicts a required value in Phi(G)
   above (for example, the type's contract fixes "is_vegan": false, but Phi(G)
   requires "is_vegan": true), set "included_in_description": false with
   "reason_if_excluded": "type contract contradicts goal requirement" — this is a
   different, more specific reason than step 2, and matters for how these results
   are analysed, so do not merge the two reasons.
4. For objects that remain (type is in the active domain and not contract-excluded),
   report ONLY the properties needed to check Phi(G) and R(G), plus the minimal
   properties needed to justify the type assignment itself. Do not exhaustively
   report every property listed in the conceptual system for that type — this
   variant is specifically testing whether goal-aware restriction produces a
   smaller, still-correct description, so exhaustive reporting defeats the point of
   this condition.

Output your answer as a single JSON object with this exact structure:

{schema_block}

Here is a worked example for a single, unrelated photo, showing the expected level
of detail (do not copy these values — this is a format example only):

{worked_example}

Note that in this variant an excluded object's example entry would look like:
{{ "object_id": "obj_002", "proposed_type": "meat_product", "properties": {{}},
"included_in_description": false, "reason_if_excluded": "type contract contradicts
goal requirement" }}

Now process the {n} photographs provided and return only the JSON object."""


def _format_phi(phi: dict) -> str:
    if not phi:
        return "(none)"
    return ", ".join(f"{k} = {v}" for k, v in phi.items())


def _format_r(r: dict) -> str:
    if not r:
        return "(none)"
    parts = []
    for k, v in r.items():
        op, threshold = v
        parts.append(f"{k} {op} {threshold}")
    return ", ".join(parts)


def build_prompt_with_ontology(
    shopping_goal_plain_language: str,
    n: int,
    active_domain_types: set[str],
    phi: dict,
    r: dict,
    ontology_json: str,
) -> str:
    """Shared by Variant C (well-formed ontology) and Variant D (weakened
    ontology) -- agent_prompts_ABCD.md is explicit that D's prompt is
    "IDENTICAL to Variant C's prompt in every instruction and every
    sentence... the only difference is the content of the CONCEPTUAL SYSTEM
    block". Keeping ONE template function for both, parameterized only by
    which ontology text is substituted, is what makes that guarantee
    structural rather than a matter of two files staying in sync by hand."""
    return _TEMPLATE.format(
        goal=shopping_goal_plain_language,
        n=n,
        ontology_json=ontology_json,
        dg_types=", ".join(sorted(active_domain_types)),
        phi=_format_phi(phi),
        r=_format_r(r),
        schema_block=shared_output_schema_block(),
        worked_example=WORKED_EXAMPLE,
    )


def build_prompt(
    shopping_goal_plain_language: str,
    n: int,
    active_domain_types: set[str],
    phi: dict,
    r: dict,
) -> str:
    return build_prompt_with_ontology(
        shopping_goal_plain_language, n, active_domain_types, phi, r, WELL_FORMED_ONTOLOGY_JSON
    )
