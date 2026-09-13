"""Phase 3: validates reference_labels.json against the ontology BEFORE the
full run, per the user's brief: "every reference_type must exactly match a
type name in formal_artifacts_owl_pddl_v2.md's ontology (case-sensitive),
and flag any row where it doesn't, rather than silently failing later."

The authoritative type-name set is `hierarchy.WELL_FORMED_HIERARCHY`'s keys
-- mirrored verbatim from Part A of formal_artifacts_owl_pddl_v2.md (see
hierarchy.py's own docstring), so this check is against the same names the
OWL ontology and the agent-facing JSON both use, not a separately
maintained list that could drift.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.hierarchy import WELL_FORMED_HIERARCHY


def valid_type_names() -> set[str]:
    return set(WELL_FORMED_HIERARCHY.keys())


def validate_reference_labels(reference_labels_path: Path) -> dict:
    """Returns a report dict:
      {
        "total_rows": int,
        "valid_rows": [object_id, ...],
        "invalid_rows": [{"object_id", "reference_type", "reason"}, ...],
        "property_key_warnings": [{"object_id", "unknown_property"}, ...],  # informational only, not blocking
      }
    Never silently skips a row -- every row in the file is checked and
    accounted for in either valid_rows or invalid_rows (len(valid)+len(invalid)
    == total_rows is asserted, so a row can't fall through unclassified).
    """
    with open(reference_labels_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    valid_types = valid_type_names()
    known_features = set()
    for info in WELL_FORMED_HIERARCHY.values():
        known_features |= set(info["own_features"])

    valid_rows = []
    invalid_rows = []
    property_key_warnings = []

    for row in rows:
        object_id = row.get("object_id")
        reference_type = row.get("reference_type")

        if reference_type is None:
            invalid_rows.append({"object_id": object_id, "reference_type": reference_type, "reason": "missing reference_type field"})
        elif reference_type not in valid_types:
            # Case-insensitive near-match, purely to make the report actionable
            # (e.g. "dairyproduct" vs "DairyProduct") -- does NOT count as a pass;
            # the check itself remains exact and case-sensitive per the brief.
            near_matches = [t for t in valid_types if t.lower() == reference_type.lower()]
            reason = "no case-sensitive match in ontology"
            if near_matches:
                reason += f" (case-insensitive match exists: {near_matches})"
            invalid_rows.append({"object_id": object_id, "reference_type": reference_type, "reason": reason})
        else:
            valid_rows.append(object_id)

        # Informational only (not part of the pass/fail gate the user specified):
        # flag reference_properties keys that don't correspond to any declared
        # feature name in the ontology, since a silent typo here would otherwise
        # just be ignored by every downstream consumer of this file.
        for prop_key in (row.get("reference_properties") or {}).keys():
            if prop_key not in known_features and prop_key not in ("veganAttributeMatch", "nutriscoreMatch"):
                property_key_warnings.append({"object_id": object_id, "unknown_property": prop_key})

    assert len(valid_rows) + len(invalid_rows) == len(rows), (
        f"row-accounting mismatch: {len(valid_rows)} valid + {len(invalid_rows)} invalid != {len(rows)} total "
        "-- a row fell through unclassified, which must never happen"
    )

    return {
        "total_rows": len(rows),
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "property_key_warnings": property_key_warnings,
    }
