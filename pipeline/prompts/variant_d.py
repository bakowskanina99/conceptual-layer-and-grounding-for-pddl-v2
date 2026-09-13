"""Variant D -- weakened conceptual system (ablation, Assumption 3.1
violated). agent_prompts_ABCD.md is explicit: "IDENTICAL to Variant C's
prompt in every instruction and every sentence... the only difference is the
content of the CONCEPTUAL SYSTEM block, which uses the WEAKENED ontology...
Do not alter any wording besides this substitution." Reuses variant_c's exact
template via build_prompt_with_ontology so this guarantee is structural.

Also per the spec: "The agent is never told the ontology is weakened, and
never told this is an ablation" -- build_prompt takes exactly the same
arguments as variant_c.build_prompt, computed the same way by the caller
(the D(G)/Phi(G)/R(G) shown to the agent are still computed against the
well-formed hierarchy's goal semantics -- only the CONCEPTUAL SYSTEM listing
itself is weakened, nothing about how the active domain was derived)."""

from pipeline.prompts.ontology_json import WEAKENED_ONTOLOGY_JSON
from pipeline.prompts.variant_c import build_prompt_with_ontology


def build_prompt(
    shopping_goal_plain_language: str,
    n: int,
    active_domain_types: set[str],
    phi: dict,
    r: dict,
) -> str:
    return build_prompt_with_ontology(
        shopping_goal_plain_language, n, active_domain_types, phi, r, WEAKENED_ONTOLOGY_JSON
    )
