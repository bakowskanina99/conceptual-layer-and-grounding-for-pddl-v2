"""Compiler-N (Variant A only) -- naive/ad-hoc compilation,
compiler_pipeline_spec.md. No reasoner, no SHACL, no reference ontology --
mechanical, by design, over whatever ad-hoc type/predicate vocabulary the
agent invented.

`infer_kind` self-detects a value's kind from its own shape (JSON bool ->
boolean; a number or numeric-parseable string -> numeric; else categorical)
rather than using Stage 0's coercion/feature_domain_table -- Variant A's
agent invents its own property names, so there is no fixed domain table to
look them up in; the spec's own compile_naive pseudocode does not call
coerce() for exactly this reason.
"""

from __future__ import annotations

import json

from pipeline.compilers.compiler_formal.pddl_compile import (
    format_pddl_number,
    slugify_value,
    to_pddl_ident,
    to_pddl_object_name,
)


def _canonical_value(val):
    """Categorical values must be hashable to use as a dict key. Variant A's
    agent invents its own property VALUE shapes too, not just names -- e.g. a
    JSON list for a naturally multi-valued property like an ingredients list
    (found via testing: `"ingredients": ["haricots verts", "carottes", ...]`
    crashed with `TypeError: unhashable type: 'list'`). Canonicalize to a
    stable string instead of crashing or silently dropping the fact."""
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    if isinstance(val, dict):
        return json.dumps(val, sort_keys=True)
    return val


def infer_kind(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "numeric"
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "false", "yes", "no"):
            return "boolean"
        try:
            float(value)
            return "numeric"
        except ValueError:
            pass
    return "categorical"


def compile_naive(agent_objects: list[dict]) -> dict:
    """agent_objects: the "objects" list from Variant A's shared-schema JSON.

    Returns {types_seen, predicates_seen, included_objects, domain_size} --
    domain_size = |types| + |predicates|, the same size(D) formula as
    Definition 5.3, applied to Variant A's own invented vocabulary (state
    this equivalence explicitly in the paper -- compiler_pipeline_spec.md's
    own note, not an incidental implementation similarity)."""
    types_seen: dict = {}
    predicates_seen: dict = {}
    included_objects: list[dict] = []

    for obj in agent_objects:
        if not obj["included_in_description"]:
            continue
        t = obj["proposed_type"]
        types_seen[t] = None
        for prop, val in obj.get("properties", {}).items():
            if prop.startswith("_"):
                continue  # "_note" and similar are agent commentary, not compiled features
            predicates_seen[prop] = infer_kind(val)
        included_objects.append(obj)

    domain_size = len(types_seen) + len(predicates_seen)
    return {
        "types_seen": types_seen,
        "predicates_seen": predicates_seen,
        "included_objects": included_objects,
        "domain_size": domain_size,
    }


def render_naive_pddl(domain_pddl_name: str, problem_pddl_name: str, compiled: dict) -> tuple[str, str]:
    """Renders (domain_pddl_text, problem_pddl_text) for Variant A -- flat
    types (no hierarchy: the agent gave none), predicates generically typed
    to `object` (Variant A has no feat(t) ownership concept at all, just a
    flat bag of predicates observed across included objects). Uses the same
    `put-in-cart` action pattern as Compiler-F's output so the Fast Downward
    A-vs-C comparison (experimental_design_v2.md) is measuring domain
    size/planning cost, not two structurally different planning problems.
    """
    types_seen = compiled["types_seen"]
    predicates_seen = compiled["predicates_seen"]
    included_objects = compiled["included_objects"]

    pddl_types = sorted({to_pddl_ident(t) for t in types_seen})

    booleans = sorted(p for p, k in predicates_seen.items() if k == "boolean")
    categoricals = sorted(p for p, k in predicates_seen.items() if k == "categorical")
    numerics = sorted(p for p, k in predicates_seen.items() if k == "numeric")

    domain_lines = [
        f"(define (domain {domain_pddl_name})",
        "  (:requirements :typing :negative-preconditions :equality)",
        "",
        "  (:types",
        f"    tag {' '.join(pddl_types)} - object" if pddl_types else "    tag - object",
        "  )",
        "",
        "  (:predicates",
    ]
    for p in booleans:
        domain_lines.append(f"    ({to_pddl_ident(p)} ?x - object)")
    for p in categoricals:
        domain_lines.append(f"    ({to_pddl_ident(p)} ?x - object ?v - tag)")
    domain_lines.append("    (in-cart ?x - object)  ; planning-mechanism predicate, NOT a formal feature")
    domain_lines.append("  )")
    domain_lines.append("")
    if numerics:
        domain_lines.append("  (:functions")
        for p in numerics:
            domain_lines.append(f"    ({to_pddl_ident(p)} ?x - object)")
        domain_lines.append("  )")
        domain_lines.append("")
    domain_lines += [
        "  (:action put-in-cart",
        "    :parameters (?x - object)",
        "    :precondition (not (in-cart ?x))",
        "    :effect (in-cart ?x)",
        "  )",
        ")",
    ]

    tag_slug_map: dict = {}
    for obj in included_objects:
        for prop, val in obj.get("properties", {}).items():
            if prop.startswith("_") or predicates_seen.get(prop) != "categorical":
                continue
            key = (prop, _canonical_value(val))
            if key not in tag_slug_map:
                tag_slug_map[key] = slugify_value(key[1])

    object_ids = [to_pddl_object_name(o["object_id"]) for o in included_objects]
    object_type_by_id = {to_pddl_object_name(o["object_id"]): to_pddl_ident(o["proposed_type"]) for o in included_objects}

    problem_lines = [f"(define (problem {problem_pddl_name})", f"  (:domain {domain_pddl_name})", ""]
    objects_by_type: dict[str, list[str]] = {}
    for oid, t in object_type_by_id.items():
        objects_by_type.setdefault(t, []).append(oid)
    obj_block_lines = [f"    {' '.join(sorted(ids))} - {t}" for t, ids in sorted(objects_by_type.items())]
    tag_slugs = sorted(set(tag_slug_map.values()))
    if tag_slugs:
        obj_block_lines.append(f"    {' '.join(tag_slugs)} - tag")
    problem_lines.append("  (:objects\n" + "\n".join(obj_block_lines) + "\n  )")
    problem_lines.append("")

    problem_lines.append("  (:init")
    for obj in included_objects:
        oid = to_pddl_object_name(obj["object_id"])
        facts = []
        for prop, val in obj.get("properties", {}).items():
            if prop.startswith("_"):
                continue
            kind = predicates_seen.get(prop)
            if kind == "boolean":
                truthy = isinstance(val, bool) and val or (isinstance(val, str) and val.strip().lower() in ("true", "yes"))
                if truthy:
                    facts.append(f"({to_pddl_ident(prop)} {oid})")
            elif kind == "categorical":
                facts.append(f"({to_pddl_ident(prop)} {oid} {tag_slug_map[(prop, _canonical_value(val))]})")
            elif kind == "numeric":
                try:
                    facts.append(f"(= ({to_pddl_ident(prop)} {oid}) {format_pddl_number(float(val))})")
                except (TypeError, ValueError):
                    pass  # unparsable numeric response -- Stage 0's parse-failure case, logged elsewhere, simply omitted here
        problem_lines.append("    " + " ".join(facts))
    problem_lines.append("  )")
    problem_lines.append("")

    goal_ids = [to_pddl_object_name(o["object_id"]) for o in included_objects]
    problem_lines.append(f"  (:goal (and {' '.join(f'(in-cart {oid})' for oid in goal_ids)}))")
    problem_lines.append(")")

    return "\n".join(domain_lines), "\n".join(problem_lines)
