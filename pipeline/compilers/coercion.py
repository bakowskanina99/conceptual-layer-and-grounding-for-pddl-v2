"""Stage 0 (all variants): value coercion, per compiler_pipeline_spec.md.

Normalises every `properties` value in the agent's JSON against the feature's
declared domain (Definition 3.1: Boolean / numeric / categorical), since an 8B
model will not consistently emit `true` vs `"true"` vs `"yes"`.
"""

from __future__ import annotations

from pipeline.feature_domains import FEATURE_DOMAINS


def coerce(feature_name: str, raw_value, feature_domain_table: dict = FEATURE_DOMAINS):
    """Returns the coerced value, or None for explicit absence / parse failure
    (Definition 3.2 -- never coerced to a default). Callers that need to tell
    "agent said unknown" apart from "agent's answer didn't parse" must check
    `raw_value == "unknown"` themselves before calling this (see `coerce_object_properties`)."""
    domain = feature_domain_table.get(feature_name, "categorical")  # unseen features default categorical
    if raw_value == "unknown":
        return None
    if domain == "boolean":
        return str(raw_value).strip().lower() in {"true", "yes", "1"}
    if domain == "numeric":
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return None
    return str(raw_value).strip().lower()


def coerce_object_properties(raw_properties: dict, feature_domain_table: dict = FEATURE_DOMAINS) -> tuple[dict, list[dict]]:
    """Coerces every property in one object's `properties` dict (as given by
    the agent JSON, minus any "_note"/"_"-prefixed commentary keys -- those
    are agent commentary, never compiled features, per compiler_pipeline_spec.md's
    Compiler-N notes, which apply identically here).

    Returns (coerced_properties, parse_failures) where parse_failures is a list
    of {"property": name, "raw_value": ...} entries for every value that hit
    the None-on-parse-failure branch specifically (NOT genuine "unknown"
    responses) -- these are two different failure modes (model didn't know vs.
    model answered in an unparsable format) and must be logged separately,
    per the spec's explicit instruction.
    """
    coerced = {}
    parse_failures = []

    for prop, raw_value in raw_properties.items():
        if prop.startswith("_"):
            continue
        value = coerce(prop, raw_value, feature_domain_table)
        coerced[prop] = value
        if value is None and raw_value != "unknown":
            parse_failures.append({"property": prop, "raw_value": raw_value})

    return coerced, parse_failures
