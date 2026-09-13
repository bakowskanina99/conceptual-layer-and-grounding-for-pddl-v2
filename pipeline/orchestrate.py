"""Orchestrator: agent call -> JSON -> compiler -> PDDL, per object, per
variant, per goal. Ties together prompts/, ollama_client, compilers/,
planning/, logging_/ -- used by both the Phase 2 smoke test and (unmodified)
the Phase 4 full run.

Two-level design, matching the fact that Ollama calls are per-object
but PDDL compilation is naturally per variant+goal GROUP
(a "put N items in cart" planning problem needs the N items together):
  1. `process_object` -- one agent call, Stage 0/1/1b/2/3, one log row,
     written immediately (crash-resilience, user's brief).
  2. `compile_and_plan_group` -- merges a variant+goal's processed objects
     into one PDDL domain+problem, runs Fast Downward once.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from pipeline import config, goals
from pipeline.compilers import coercion
from pipeline.compilers.compiler_formal import owl_classify, pddl_compile, rdf_individuals, shacl_validate
from pipeline.compilers import compiler_naive
from pipeline.hierarchy import WEAKENED_HIERARCHY, WELL_FORMED_HIERARCHY
from pipeline.logging_.schema import build_log_row
from pipeline.ollama_client import call_agent, extract_json
from pipeline.planning.fast_downward import run_fast_downward
from pipeline.prompts import variant_a, variant_b, variant_c, variant_d

HIERARCHY_FOR_VARIANT = {
    "A": None,  # Compiler-N has no reference ontology at all
    "B": WELL_FORMED_HIERARCHY,
    "C": WELL_FORMED_HIERARCHY,
    "D": WEAKENED_HIERARCHY,
}

OWL_TTL_FOR_VARIANT = {
    "B": config.WELL_FORMED_TTL,
    "C": config.WELL_FORMED_TTL,
    "D": config.WEAKENED_TTL,
}


def _normalise_type_name(name):
    return owl_classify.normalise_type_name(name) if name else None


def build_prompt_for(variant: str, goal_name: str) -> str:
    goal_text = goals.PLAIN_LANGUAGE_GOAL_TEXT[goal_name]
    if variant == "A":
        return variant_a.build_prompt(goal_text, 1)

    hierarchy = HIERARCHY_FOR_VARIANT[variant]
    dg = goals.active_domain(WELL_FORMED_HIERARCHY, goal_name) if variant in ("C", "D") else set(hierarchy)
    phi = goals.GOALS[goal_name]["phi"] if variant in ("C", "D") else {}
    r = goals.GOALS[goal_name]["r"] if variant in ("C", "D") else {}

    if variant == "B":
        return variant_b.build_prompt(goal_text, 1)
    if variant == "C":
        return variant_c.build_prompt(goal_text, 1, dg, phi, r)
    if variant == "D":
        return variant_d.build_prompt(goal_text, 1, dg, phi, r)
    raise ValueError(f"unknown variant {variant!r}")


def process_object(
    object_id: str,
    variant: str,
    goal_name: str,
    reference_labels_by_id: dict,
    reasoners: dict,
    writer,
    raw_dir: Path | None = None,
) -> dict:
    """One agent call + Stage 0-3, one log row (written immediately).
    `reasoners`: {"B"/"C": OwlClassifier(well-formed), "D": OwlClassifier(weakened)}
    -- reused across objects, per owl_classify.py's design (destroy_entity
    resets state between calls, avoiding a full ontology reload per object).

    Returns a dict with everything `compile_and_plan_group` needs for this
    object (or {"dropped": True, ...} if the JSON never parsed -- logged, not
    silently discarded).
    """
    image_path = config.IMAGES_DIR / f"{object_id}.jpg"
    prompt_text = build_prompt_for(variant, goal_name)

    # Retry on empty/unparseable response (up to 3 attempts total).
    #
    # IMPORTANT: `first_attempt_valid_json` must reflect ONLY whether the
    # FIRST Ollama call alone produced usable JSON with no cleanup needed --
    # an earlier version of this loop overwrote a single `first_attempt_valid`
    # variable on every iteration, so a success on retry #2/#3 could look
    # identical to a true first-attempt success in that statistic. Each
    # attempt's outcome is kept separately so this cannot happen, and
    # `ollama_attempts_used`/`ollama_succeeded_on_attempt` make a retried
    # object distinguishable from a clean one in the log itself, not just
    # inferable from raw files.
    def _attempt_succeeded(parsed_attempt) -> bool:
        return parsed_attempt is not None and bool(parsed_attempt.get("objects"))

    max_attempts = 3
    attempt_call_results = []  # [(call_result, parsed, cleanup_free_bool), ...]
    for attempt in range(1, max_attempts + 1):
        try:
            attempt_call_result = call_agent(prompt_text, image_path)
        except requests.exceptions.RequestException as exc:
            # Found via testing: a genuine Ollama read-timeout (>300s, no
            # response at all) previously crashed the whole script instead of
            # being treated as one failed attempt.
            # Synthesize a failed-attempt record so the retry loop and every
            # downstream field (first_attempt_valid_json, ollama_attempts_used,
            # etc.) behave exactly as for an empty/unparseable response,
            # rather than needing a second, separate code path.
            attempt_call_result = {
                "raw_request": None, "raw_prompt_text": prompt_text,
                "raw_response_text": "", "elapsed_seconds": None,
                "ollama_metadata": {"exception": repr(exc)},
            }
        attempt_parsed, attempt_cleanup_free = extract_json(attempt_call_result["raw_response_text"])
        attempt_call_results.append((attempt_call_result, attempt_parsed, attempt_cleanup_free))
        if raw_dir is not None:
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / f"{variant}_{goal_name}_{object_id}_attempt{attempt}_response.txt").write_text(
                attempt_call_result["raw_response_text"], encoding="utf-8"
            )
            # Persisted for EVERY attempt, not just failures -- an empty or
            # truncated response is otherwise undiagnosable after the fact
            # (found the hard way: Ollama's server log showed real
            # `truncated=1` context-overflow events during this project's own
            # testing, but ollama_metadata itself was never saved anywhere,
            # so a specific failed call couldn't be attributed to truncation
            # vs. some other cause after it happened).
            (raw_dir / f"{variant}_{goal_name}_{object_id}_attempt{attempt}_metadata.json").write_text(
                json.dumps(attempt_call_result["ollama_metadata"], indent=2, default=str), encoding="utf-8"
            )
        if _attempt_succeeded(attempt_parsed):
            break

    ollama_attempts_used = len(attempt_call_results)
    call_result, parsed, _ = attempt_call_results[-1]
    ollama_succeeded_on_attempt = ollama_attempts_used if _attempt_succeeded(parsed) else None
    first_call_result, first_parsed, first_cleanup_free = attempt_call_results[0]
    first_attempt_valid = first_cleanup_free and _attempt_succeeded(first_parsed)

    if raw_dir is not None:
        (raw_dir / f"{variant}_{goal_name}_{object_id}_prompt.txt").write_text(prompt_text, encoding="utf-8")

    reference = reference_labels_by_id.get(object_id, {})

    if parsed is None or not parsed.get("objects"):
        row = build_log_row(
            object_id=object_id, variant=variant, goal=goal_name,
            json_parse_failure=True, first_attempt_valid_json=first_attempt_valid,
            ollama_attempts_used=ollama_attempts_used, ollama_succeeded_on_attempt=ollama_succeeded_on_attempt,
            elapsed_seconds=call_result["elapsed_seconds"],
            raw_prompt_text=call_result["raw_prompt_text"], raw_response_text=call_result["raw_response_text"],
            reference_type=reference.get("reference_type"), reference_properties=reference.get("reference_properties"),
        )
        writer.write_row(row)
        return {"object_id": object_id, "dropped": True}

    agent_obj = parsed["objects"][0]

    if variant == "A":
        final_type_correct = (
            _normalise_type_name(agent_obj.get("proposed_type")) == _normalise_type_name(reference.get("reference_type"))
        )
        row = build_log_row(
            object_id=object_id, variant=variant, goal=goal_name,
            agent_reported_object_id=agent_obj.get("object_id"),
            agent_proposed_type=agent_obj.get("proposed_type"),
            agent_included=agent_obj.get("included_in_description"),
            agent_reason=agent_obj.get("reason_if_excluded"),
            reference_type=reference.get("reference_type"), reference_properties=reference.get("reference_properties"),
            final_type_correct=final_type_correct,
            json_parse_failure=False, first_attempt_valid_json=first_attempt_valid,
            ollama_attempts_used=ollama_attempts_used, ollama_succeeded_on_attempt=ollama_succeeded_on_attempt,
            elapsed_seconds=call_result["elapsed_seconds"],
            raw_prompt_text=call_result["raw_prompt_text"], raw_response_text=call_result["raw_response_text"],
        )
        writer.write_row(row)
        return {"object_id": object_id, "dropped": False, "agent_object": agent_obj}

    # B/C/D: Stage 1 + 1b
    prepared = rdf_individuals.prepare_individual(agent_obj, goal_name)
    clf = reasoners[variant]
    classify_result = clf.classify_object(
        object_id, prepared["coerced_properties"], extra_properties=prepared["extra_properties"]
    )

    grounding_status = classify_result["status"]
    reasoner_type = classify_result.get("reasoner_type")
    type_agreement = (
        _normalise_type_name(reasoner_type) == _normalise_type_name(prepared["agent_claimed_type"])
        if grounding_status == "resolved" else None
    )
    final_type_correct = (
        _normalise_type_name(reasoner_type) == _normalise_type_name(reference.get("reference_type"))
        if grounding_status == "resolved" else False
    )

    shacl_result = None
    if variant in ("C", "D") and grounding_status == "resolved":
        if goal_name in goals.GOAL_SHAPE_NAMES:
            shacl_result = shacl_validate.validate_goal_shape(
                object_id, reasoner_type, classify_result["reasoner_type_ancestors"],
                prepared["coerced_properties"], prepared["extra_properties"],
                goals.GOAL_SHAPE_NAMES[goal_name],
                prepared["agent_included"], prepared["agent_reason"],
            )
        else:
            # G2_real (and any goal with Phi(G)=R(G)=empty set) has no SHACL
            # shape at all -- Definition 4.6's admitted/pending/excluded
            # conjunction over an EMPTY Phi(G) union R(G) is vacuously true,
            # so a resolved, type-admissible object is trivially G-admitted,
            # not "unchecked". Found via testing: leaving shacl_status as
            # None here made compile_and_plan_group's filter
            # (`shacl_status not in ("admitted","pending")`) silently exclude
            # EVERY resolved object for G2_real specifically.
            shacl_result = {
                "shacl_status": "admitted", "shacl_conforms": True,
                "agent_included": prepared["agent_included"], "agent_reason": prepared["agent_reason"],
                "agent_shacl_agreement": bool(prepared["agent_included"]),  # (shacl_status=="admitted") == agent_included, matching shacl_validate's own formula
            }

    row = build_log_row(
        object_id=object_id, variant=variant, goal=goal_name,
        agent_reported_object_id=prepared["agent_reported_object_id"],
        agent_proposed_type=prepared["agent_claimed_type"],
        reasoner_type=reasoner_type, reasoner_types=classify_result.get("reasoner_types"),
        type_agreement=type_agreement, grounding_status=grounding_status,
        agent_included=prepared["agent_included"], agent_reason=prepared["agent_reason"],
        shacl_status=shacl_result["shacl_status"] if shacl_result else None,
        agent_shacl_agreement=shacl_result["agent_shacl_agreement"] if shacl_result else None,
        stage1b_applicable=prepared["stage1b_log"]["stage1b_applicable"],
        stage1b_source_is_vegan=prepared["stage1b_log"]["stage1b_source_is_vegan"],
        derived_vegan_attribute_match=prepared["stage1b_log"]["derived_vegan_attribute_match"],
        reference_type=reference.get("reference_type"), reference_properties=reference.get("reference_properties"),
        final_type_correct=final_type_correct,
        parse_failures=prepared["parse_failures"], json_parse_failure=False,
        first_attempt_valid_json=first_attempt_valid,
        ollama_attempts_used=ollama_attempts_used, ollama_succeeded_on_attempt=ollama_succeeded_on_attempt,
        elapsed_seconds=call_result["elapsed_seconds"],
        raw_prompt_text=call_result["raw_prompt_text"], raw_response_text=call_result["raw_response_text"],
    )
    writer.write_row(row)

    return {
        "object_id": object_id, "dropped": False,
        "reasoner_type": reasoner_type, "grounding_status": grounding_status,
        "coerced_properties": prepared["coerced_properties"], "extra_properties": prepared["extra_properties"],
        "shacl_status": shacl_result["shacl_status"] if shacl_result else None,
    }


def compile_and_plan_group(variant: str, goal_name: str, processed_objects: list[dict], workdir: Path) -> dict:
    """Merges one variant+goal's processed objects into one PDDL domain+
    problem, runs Fast Downward. Returns {domain_text, problem_text,
    domain_size, fd_result}."""
    workdir.mkdir(parents=True, exist_ok=True)
    live = [o for o in processed_objects if not o.get("dropped")]

    if variant == "A":
        # Override the agent's own self-reported object_id with the TRUE one
        # (o["object_id"], the caller-controlled id that actually identifies
        # which photo was sent) -- the agent's own field is near-always
        # "obj_001" for every object under one-call-per-object (D12), and
        # compiler_naive.py reads o["object_id"] directly (Definition 5.3's
        # domain_size is unaffected -- it's keyed by type/property NAME, never
        # object_id -- but every object would otherwise collapse into one
        # PDDL object, corrupting the compiled PROBLEM and any Fast Downward
        # plan/timing measured from it).
        agent_objects = [{**o["agent_object"], "object_id": o["object_id"]} for o in live]
        compiled = compiler_naive.compile_naive(agent_objects)
        domain_text, problem_text = compiler_naive.render_naive_pddl(
            f"naive-{goal_name}", f"naive-{goal_name}-problem", compiled
        )
        domain_size = compiled["domain_size"]
    else:
        hierarchy = HIERARCHY_FOR_VARIANT[variant]
        active_types = set(hierarchy) if variant == "B" else goals.active_domain(hierarchy, goal_name)

        compiled_objects = []
        for o in live:
            if o.get("grounding_status") != "resolved":
                continue  # ambiguous_grounding/reasoner_inconsistent -- ungroundable, Definition 5.4 exclusion
            if o["reasoner_type"] not in active_types:
                continue  # type-inadmissible/irrelevant -- Definition 4.2/4.4 exclusion, never compiled
            if variant in ("C", "D") and o.get("shacl_status") not in ("admitted", "pending"):
                continue  # G-excluded (Definition 4.6) -- omitted entirely, Definition 5.4
            compiled_objects.append(
                {
                    "object_id": o["object_id"], "reasoner_type": o["reasoner_type"],
                    "coerced_properties": o["coerced_properties"], "extra_properties": o["extra_properties"],
                    "shacl_status": o.get("shacl_status"),
                }
            )

        structure = pddl_compile.compile_domain_structure(hierarchy, active_types)
        domain_text = pddl_compile.render_domain_pddl(f"{variant.lower()}-{goal_name}", structure)
        problem_text = (
            pddl_compile.render_problem_pddl(f"{variant.lower()}-{goal_name}-problem", f"{variant.lower()}-{goal_name}", structure, compiled_objects)
            if compiled_objects
            else None
        )
        domain_size = structure["size"]

    domain_path = workdir / "domain.pddl"
    domain_path.write_text(domain_text, encoding="utf-8")

    fd_result = None
    if problem_text is not None:
        problem_path = workdir / "problem.pddl"
        problem_path.write_text(problem_text, encoding="utf-8")
        fd_result = run_fast_downward(domain_path, problem_path, workdir / "fd")

    return {
        "domain_text": domain_text, "problem_text": problem_text,
        "domain_size": domain_size, "fd_result": fd_result,
    }
