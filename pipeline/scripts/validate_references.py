"""Phase 3 entry point: validates reference_labels.json against the ontology
before the full run. Prints a full report; exits non-zero if any row fails
the case-sensitive reference_type check, per the user's brief ("flag any row
where it doesn't, rather than silently failing later")."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import config
from pipeline.logging_.reference_validation import validate_reference_labels, valid_type_names


def main() -> None:
    report = validate_reference_labels(config.REFERENCE_LABELS_PATH)

    print(f"Valid ontology type names ({len(valid_type_names())}): {sorted(valid_type_names())}")
    print()
    print(f"Total rows checked: {report['total_rows']}")
    print(f"Valid (exact case-sensitive match): {len(report['valid_rows'])}")
    print(f"Invalid: {len(report['invalid_rows'])}")
    print()

    if report["invalid_rows"]:
        print("=== INVALID ROWS ===")
        for r in report["invalid_rows"]:
            print(f"  {r['object_id']}: reference_type={r['reference_type']!r} -- {r['reason']}")
        print()

    if report["property_key_warnings"]:
        print("=== property_key warnings (informational only, not part of the pass/fail gate) ===")
        for w in report["property_key_warnings"]:
            print(f"  {w['object_id']}: unrecognized property key {w['unknown_property']!r}")
        print()

    print(f"Accounting check: {len(report['valid_rows'])} valid + {len(report['invalid_rows'])} invalid == {report['total_rows']} total -> "
          f"{'OK' if len(report['valid_rows']) + len(report['invalid_rows']) == report['total_rows'] else 'MISMATCH (BUG)'}")

    if report["invalid_rows"]:
        print("\nRESULT: FAILED -- invalid rows found, see above. Do not proceed to Phase 4 until resolved.")
        sys.exit(1)
    else:
        print("\nRESULT: PASSED -- every reference_type exactly matches an ontology class name.")
        sys.exit(0)


if __name__ == "__main__":
    main()
