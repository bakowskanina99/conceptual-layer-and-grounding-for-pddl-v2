"""Unified per-object log row (compiler_pipeline_spec.md, "Unified per-object
log schema"). One row per object per variant per goal -- Sections 8.1-8.3's
three pairwise comparisons (A vs C, B vs C, C vs D) are all filters/group-bys
over this one table, not three separately-collected datasets.
"""

from __future__ import annotations

LOG_FIELDS = [
    "object_id", "variant", "goal",
    "agent_reported_object_id",  # near-always "obj_001" -- diagnostic only, never an identifier
    "agent_proposed_type",
    "reasoner_type",           # B/C/D only; null for A
    "reasoner_types",          # full list for ambiguous_grounding, else single-element or empty
    "type_agreement",          # B/C/D only
    "grounding_status",        # B/C/D: resolved / ambiguous_grounding / reasoner_inconsistent / no_type_inferred
    "agent_included",
    "agent_reason",
    "shacl_status",            # C/D only: admitted / pending / excluded / null (B has no Stage 3)
    "agent_shacl_agreement",   # C/D only
    "stage1b_applicable",      # real-data goals only (G3_real/G4_real)
    "stage1b_source_is_vegan",
    "derived_vegan_attribute_match",
    "reference_type",
    "reference_properties",
    "final_type_correct",
    "parse_failures",          # list of {"property": ..., "raw_value": ...} from Stage 0
    "json_parse_failure",      # boolean -- NO attempt (1st or any retry) ever produced usable JSON
    "first_attempt_valid_json",  # true iff the FIRST Ollama call alone produced usable JSON with
                                  # no fallback cleanup needed -- NEVER true just because some later
                                  # retry attempt happened to parse cleanly
    "ollama_attempts_used",      # how many Ollama calls were actually made for this object (1-3)
    "ollama_succeeded_on_attempt",  # which attempt number's response was ultimately used, or null if all failed
    "elapsed_seconds",         # of the attempt actually used, not summed across retries
    "raw_prompt_text",
    "raw_response_text",
]


def build_log_row(**kwargs) -> dict:
    """Builds one row with every field in LOG_FIELDS present (None where not
    applicable to this variant/stage) -- so a downstream aggregation never
    silently drops a row for lacking a key, and a missing/renamed field is
    caught immediately as a KeyError rather than a silently-empty column."""
    row = {field: None for field in LOG_FIELDS}
    unknown_keys = set(kwargs) - set(LOG_FIELDS)
    if unknown_keys:
        raise KeyError(f"build_log_row got unknown field(s) not in LOG_FIELDS: {unknown_keys}")
    row.update(kwargs)
    return row
