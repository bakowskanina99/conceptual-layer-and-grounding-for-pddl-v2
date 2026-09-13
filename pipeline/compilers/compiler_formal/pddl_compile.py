"""Stage 4: PDDL compilation (Definitions 5.1-5.4), shared by Variants B/C/D.

Encoding convention (formal_artifacts_owl_pddl_v2.md header note): one PDDL
predicate/function per formal feature; boolean -> unary predicate; numeric ->
PDDL function; categorical -> binary relation (feature ?item ?value - tag)
against a generic auxiliary type `tag`.

DEVIATION from Part D's worked example, by necessity, documented here rather
than treated as a silent choice: Part D's small symbolic walkthrough
pre-declares a FIXED, closed-vocabulary `:constants` block in the DOMAIN file
(cat-grocery, food-fresh, ...) because the symbolic example's categorical
values are a small, known, controlled set. Real photographic data has
open-ended categorical values (free-text `ingredients_list`,
`aisle_location`, `material`, ...) that cannot be enumerated ahead of time.
This compiler instead declares only the `tag` TYPE in the domain file and
emits the tag-VALUE objects actually observed in the compiled object set into
the PROBLEM file's `:objects` block -- a standard, semantically equivalent
PDDL idiom (the domain fixes the encoding scheme; the problem supplies the
concrete data). This does not change `size(D(G))` (Definition 5.3), which
counts only types and predicates/functions, never value-constants.
Free-text values are slugified into valid PDDL identifiers (`slugify_value`)
since planning correctness does not depend on these being human-legible --
none of the goals used here place any Phi(G)/R(G) constraint on a free-text
categorical feature.
"""

from __future__ import annotations

import hashlib
import re

from pipeline.feature_domains import FEATURE_DOMAINS
from pipeline.hierarchy import ancestors_inclusive, feat, parent_within


def to_pddl_ident(name: str) -> str:
    """snake_case feature/type name -> kebab-case PDDL identifier."""
    return name.replace("_", "-").lower()


def format_pddl_number(value: float) -> str:
    """Fast Downward's PDDL parser rejects fractional numeric literals in
    :init assignments outright ("Fractional numbers are not supported" --
    confirmed empirically, not documented in the spec files) -- only
    POSITIVE_NUMBER (integer) or a nested function expression is accepted.
    Rounding to the nearest integer costs nothing here: none of this
    experiment's numeric features (price, calories, weight, ...) are read by
    any action precondition/effect/goal -- the single `put-in-cart` action
    only checks the boolean `in-stock` -- so no planning behavior depends on
    sub-integer precision."""
    return str(round(value))


def to_pddl_object_name(object_id: str) -> str:
    """object_id (e.g. "obj_001") is already a valid PDDL identifier as-is;
    kept as a separate function so object-name policy can change independently
    of feature/type naming."""
    return object_id


def slugify_value(raw, max_len: int = 40) -> str:
    """Sanitizes a free-text categorical value into a valid PDDL constant
    name. Collisions from truncation are guarded with a short content hash."""
    s = str(raw).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if not s:
        s = "empty"
    if len(s) > max_len:
        suffix = hashlib.sha1(str(raw).encode("utf-8")).hexdigest()[:6]
        s = s[:max_len].rstrip("-") + "-" + suffix
    return "val-" + s  # prefix guards a slug starting with a digit (invalid PDDL name)


def find_predicate_owner(hierarchy: dict, active_types: set[str], feature_name: str) -> str | None:
    """The <=_T-maximal type in active_types with feature_name in its
    cumulative feat() -- Definition 5.2's "shallowest point of introduction
    within D(G)"."""
    candidates = [t for t in active_types if feature_name in feat(hierarchy, t)]
    for t in candidates:
        ancestors = set(ancestors_inclusive(hierarchy, t)) - {t}
        if not (ancestors & set(candidates)):
            return t
    return candidates[0] if candidates else None


def compile_domain_structure(hierarchy: dict, active_types: set[str], feature_domain_table: dict = FEATURE_DOMAINS) -> dict:
    """Definitions 5.1-5.3."""
    active_types = set(active_types)
    type_parent = {t: parent_within(hierarchy, t, active_types) for t in active_types}

    all_features: set[str] = set()
    for t in active_types:
        all_features |= set(feat(hierarchy, t))

    feature_owner = {f: find_predicate_owner(hierarchy, active_types, f) for f in all_features}

    booleans, categoricals, numerics = [], [], []
    for f in sorted(all_features):
        domain = feature_domain_table.get(f, "categorical")
        (booleans if domain == "boolean" else numerics if domain == "numeric" else categoricals).append(f)

    roots = sorted(t for t in active_types if type_parent[t] is None)
    if len(roots) != 1:
        raise ValueError(f"Expected exactly one root type in active domain, got {roots}")

    return {
        "active_types": active_types,
        "type_parent": type_parent,
        "root_type": roots[0],
        "all_features": all_features,
        "feature_owner": feature_owner,
        "booleans": booleans,
        "categoricals": categoricals,
        "numerics": numerics,
        "size": len(active_types) + len(all_features),
    }


def render_domain_pddl(domain_pddl_name: str, structure: dict) -> str:
    lines = [
        f"(define (domain {domain_pddl_name})",
        "  (:requirements :typing :negative-preconditions :equality)",
        "",
        "  (:types",
        "    tag - object",
    ]

    children_by_parent: dict[str, list[str]] = {}
    for t in structure["active_types"]:
        p = structure["type_parent"][t]
        if p is not None:
            children_by_parent.setdefault(p, []).append(t)

    lines.append(f"    {to_pddl_ident(structure['root_type'])} - object")
    for parent in sorted(children_by_parent):
        kids = " ".join(to_pddl_ident(k) for k in sorted(children_by_parent[parent]))
        lines.append(f"    {kids} - {to_pddl_ident(parent)}")
    lines.append("  )")
    lines.append("")

    root = to_pddl_ident(structure["root_type"])
    lines.append("  (:predicates")
    for f in structure["booleans"]:
        owner = to_pddl_ident(structure["feature_owner"][f])
        lines.append(f"    ({to_pddl_ident(f)} ?x - {owner})")
    for f in structure["categoricals"]:
        owner = to_pddl_ident(structure["feature_owner"][f])
        lines.append(f"    ({to_pddl_ident(f)} ?x - {owner} ?v - tag)")
    lines.append(f"    (in-cart ?x - {root})  ; planning-mechanism predicate, NOT a formal feature (excluded from size(D(G)))")
    lines.append("  )")
    lines.append("")

    if structure["numerics"]:
        lines.append("  (:functions")
        for f in structure["numerics"]:
            owner = to_pddl_ident(structure["feature_owner"][f])
            lines.append(f"    ({to_pddl_ident(f)} ?x - {owner})")
        lines.append("  )")
        lines.append("")

    # put-in-cart does NOT gate on in-stock, unlike Part D's symbolic worked
    # example: in_stock is genuinely unobservable from a
    # single real product photo (there is no shelf context to read stock
    # status from), so the agent reports "unknown" for it every time --
    # coercing that to a default of "true" at compile time would violate
    # Definition 3.2's open-world principle (never coerce absence to a
    # default), which is enforced consistently everywhere else in this
    # compiler (Stage 0 coercion, Stage 1b synthesis). Dropping the
    # precondition instead changes nothing about what the mechanism under
    # test (goal-dependent restriction) does -- in_stock is already vacuous/
    # non-discriminating even in the symbolic example, where it is always
    # asserted true and never actually excludes anything. `in-stock` remains
    # a declared predicate above and is still compiled into :init whenever
    # an object DOES report it -- it just no longer gates this action.
    lines.append("  (:action put-in-cart")
    lines.append(f"    :parameters (?x - {root})")
    lines.append("    :precondition (not (in-cart ?x))")
    lines.append("    :effect (in-cart ?x)")
    lines.append("  )")
    lines.append(")")
    return "\n".join(lines)


def render_problem_pddl(
    problem_pddl_name: str,
    domain_pddl_name: str,
    structure: dict,
    compiled_objects: list[dict],
) -> str:
    """compiled_objects: one dict per G-admitted/G-pending object (Definition
    5.4 -- G-excluded objects must already be filtered out by the caller,
    never passed in here). Each dict: {object_id, reasoner_type,
    coerced_properties, extra_properties, shacl_status}. `shacl_status` is
    "admitted"/"pending" for Variant C/D, or None for Variant B (no goal
    restriction -- Stage 4 note: every resolved object reaches here, and with
    no admission concept, every one of them is a goal target, matching how B
    always fully describes every object with no restriction)."""
    root = to_pddl_ident(structure["root_type"])

    tag_slug_map: dict[tuple[str, object], str] = {}
    for obj in compiled_objects:
        all_props = {**obj["coerced_properties"], **obj["extra_properties"]}
        for f in structure["categoricals"]:
            v = all_props.get(f)
            if v is not None and (f, v) not in tag_slug_map:
                tag_slug_map[(f, v)] = slugify_value(v)

    object_ids = [to_pddl_object_name(o["object_id"]) for o in compiled_objects]
    lines = [f"(define (problem {problem_pddl_name})", f"  (:domain {domain_pddl_name})", ""]

    objects_block = f"  (:objects {' '.join(object_ids)} - {root}"
    tag_slugs = sorted(set(tag_slug_map.values()))
    if tag_slugs:
        objects_block += f"\n    {' '.join(tag_slugs)} - tag"
    objects_block += ")"
    lines.append(objects_block)
    lines.append("")

    lines.append("  (:init")
    for obj in compiled_objects:
        oid = to_pddl_object_name(obj["object_id"])
        all_props = {**obj["coerced_properties"], **obj["extra_properties"]}
        facts = []
        for f in structure["booleans"]:
            if all_props.get(f) is True:
                facts.append(f"({to_pddl_ident(f)} {oid})")
            # False or None (unobserved): omitted -- Section 5.4's documented
            # open-world/closed-world caveat, not a bug -- a pending object's
            # unobserved feature is indistinguishable from a confirmed
            # negative once compiled, by design of the classical PDDL target.
        for f in structure["categoricals"]:
            v = all_props.get(f)
            if v is not None:
                facts.append(f"({to_pddl_ident(f)} {oid} {tag_slug_map[(f, v)]})")
        for f in structure["numerics"]:
            v = all_props.get(f)
            if v is not None:
                facts.append(f"(= ({to_pddl_ident(f)} {oid}) {format_pddl_number(v)})")
        lines.append("    " + " ".join(facts))
    lines.append("  )")
    lines.append("")

    goal_worthy = [
        to_pddl_object_name(o["object_id"])
        for o in compiled_objects
        if o.get("shacl_status") in ("admitted", None)
    ]
    lines.append(f"  (:goal (and {' '.join(f'(in-cart {oid})' for oid in goal_worthy)}))")
    lines.append(")")
    return "\n".join(lines)
