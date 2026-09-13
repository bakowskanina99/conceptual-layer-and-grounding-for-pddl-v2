"""Stage 1 (+1b) orchestrator: agent JSON object -> everything OwlClassifier
needs, plus the log fields the unified per-object log requires.

compiler_pipeline_spec.md's Stage 1 pseudocode builds raw RDF triples by hand;
here the actual OWL assertion is owlready2's job (owl_classify.py), so this
module's role is the surrounding bookkeeping: Stage 0 coercion, Stage 1b
veganAttributeMatch synthesis, and keeping the agent's self-reported type
aside (never asserted as the individual's type -- Definition 3.6 requires
grounding to be COMPUTED by the reasoner, not read off what the agent said,
so Stage 2's agreement diagnostic stays a genuine, independent check).
"""

from __future__ import annotations

from pipeline.compilers.coercion import coerce_object_properties
from pipeline.compilers.compiler_formal import vegan_attribute_synthesis
from pipeline.feature_domains import FEATURE_DOMAINS


def prepare_individual(agent_object: dict, goal_name: str, feature_domain_table: dict = FEATURE_DOMAINS) -> dict:
    """agent_object: one entry from the shared output schema's "objects" list
    (object_id, proposed_type, properties, included_in_description,
    reason_if_excluded). goal_name: current goal, e.g. "G3_real" (needed for
    Stage 1b's applicability check).

    Deliberately does NOT return a usable "object_id":
    with one object per Ollama call, every prompt's own "labelled
    obj_001 through obj_{n}" text collapses to literally "obj_001" for n=1,
    so the agent's self-reported object_id is "obj_001" almost every call,
    regardless of which real object it was shown. The TRUE object_id is
    already known by the caller (it chose which photo to send) and must be
    threaded through explicitly rather than read back from here -- every
    caller in orchestrate.py already does this correctly (Stage 2/3 identify
    the individual by the caller's own object_id, never this dict's).
    `agent_reported_object_id` is kept, clearly named, for audit/diagnostic
    logging only -- never as an identifier.
    """
    agent_claimed_type = agent_object.get("proposed_type")
    raw_properties = agent_object.get("properties", {}) or {}

    coerced_properties, parse_failures = coerce_object_properties(raw_properties, feature_domain_table)

    stage1b_log = vegan_attribute_synthesis.compute(coerced_properties, goal_name)
    extra_properties = {}
    if stage1b_log["derived_vegan_attribute_match"] is not None:
        extra_properties["vegan_attribute_match"] = stage1b_log["derived_vegan_attribute_match"]

    return {
        "agent_reported_object_id": agent_object.get("object_id"),  # diagnostic only, see docstring
        "agent_claimed_type": agent_claimed_type,
        "coerced_properties": coerced_properties,
        "extra_properties": extra_properties,
        "parse_failures": parse_failures,
        "stage1b_log": stage1b_log,
        "agent_included": agent_object.get("included_in_description"),
        "agent_reason": agent_object.get("reason_if_excluded"),
    }
