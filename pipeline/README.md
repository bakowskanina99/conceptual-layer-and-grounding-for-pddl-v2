# Pipeline — Full Compiler and Orchestration Code

This is the actual, tested implementation behind Sections 5–7 of the paper: the two
compilers (Compiler-N for Variant A, Compiler-F for Variants B/C/D), the OWL/SHACL
realization of Section 6, the Ollama/Fast Downward orchestration, and the logging
infrastructure that produced `../results/results.jsonl`. Every module below is annotated
in its own docstring with the exact Definition/Section/Decision it implements; this
README is a map, not a duplicate of that detail.

## Layout and what each file implements

```
pipeline/
├── config.py                    Paths, run directories, shared constants
├── hierarchy.py                 Definition 3.5 (T, feat, parent, K+) — mirrors
│                                 agent-prompts/'s "well-formed" ontology JSON exactly,
│                                 so the compiler reasons over the same structure the
│                                 agent was shown
├── goals.py                     Definitions 4.1–4.5: goal specs, D_rel(G), D_adm(G),
│                                 D(G) — the real-data G2_real/G3_real/G4_real goals
├── feature_domains.py           Definition 3.1's value-domain table (Boolean/numeric/
│                                 categorical), single source of truth for Stage 0
├── ollama_client.py             One call per object, qwen3-vl:8b, temperature=0,
│                                 fixed seed, num_ctx>=8192 (Section 7's model config)
├── orchestrate.py               Ties prompts/ + ollama_client + compilers/ + planning/
│                                 + logging_/ together; per-object and per-(variant,
│                                 goal)-group orchestration (Section 7.3's pipeline)
│
├── compilers/
│   ├── coercion.py               Stage 0: value coercion against feature_domains.py
│   ├── compiler_naive.py         Compiler-N (Variant A) — ad-hoc, no reasoner, no SHACL
│   └── compiler_formal/          Compiler-F (Variants B/C/D)
│       ├── rdf_individuals.py     Stage 1(+1b) orchestrator: agent JSON -> RDF triples
│       ├── vegan_attribute_synthesis.py
│       │                          Stage 1b: veganAttributeMatch synthesis from the
│       │                          agent's own is_vegan — implements the
│       │                          true/false/unasserted -> 100/0/unasserted mapping
│       │                          the paper's Section 7 describes
│       ├── owl_classify.py        Stage 2: OWL classification via HermiT/owlready2 —
│       │                          Definition 3.6's G_cert(o, C), computed, not asserted
│       ├── shacl_validate.py      Stage 3: SHACL goal-shape validation (Definition
│       │                          4.6's admitted/excluded/pending), Variants C/D only
│       └── pddl_compile.py        Stage 4: PDDL compilation (Definitions 5.1–5.4)
│
├── ontology/
│   ├── well_formed.ttl            The real-data experiment's well-formed ontology
│   ├── weakened.ttl                Variant D's deliberately weakened ontology
│   └── shapes.ttl                  SHACL goal shapes for G2_real/G3_real/G4_real
│
│   Note on Assumption 3.1's OWL encoding: the paper's Section 6.2 illustrates sibling
│   disjointness using pairwise `owl:disjointWith` axioms for readability in a short
│   example. The shipped ontology in `well_formed.ttl` uses the semantically equivalent
│   `owl:AllDisjointClasses`/`owl:members` construct instead, since it scales better to
│   larger sibling groups without changing the disjointness semantics Assumption 3.1
│   requires -- both encode the same "every pair in this group is disjoint" claim.
│
├── planning/fast_downward.py     Fast Downward subprocess wrapper (--alias lama-first),
│                                 records wall-clock time and expanded states; never
│                                 raises on planner failure — a failure is a result
│
├── prompts/                     Programmatic prompt construction (see
│                                 ../agent-prompts/ for the full rendered prompt text)
│
├── logging_/
│   ├── schema.py                  The unified per-object log row schema — one row per
│   │                              object per variant per goal; every Results-section
│   │                              statistic is a filter/group-by over this one table
│   ├── incremental_writer.py      Append-only JSONL, flushed after every row (crash
│   │                              resilience — no buffering across objects)
│   └── reference_validation.py    Validates reference_labels.json against the ontology
│                                  before the full run (Phase 3 check)
│
└── scripts/
    ├── run_full.py                 Runs the full 384-combination experiment
    ├── smoke_test.py                Small-scale sanity run before the full run
    ├── report_raw.py                Computes every aggregate figure in
    │                                ../results/aggregate-tables.md directly from
    │                                results.jsonl — no numbers in that file were typed
    │                                by hand
    └── validate_references.py       Standalone entry point for reference_validation.py
```

## Design notes worth knowing before reading the code

- **Two-level orchestration** (`orchestrate.py`): Ollama calls are per-object, but PDDL
  compilation is per (variant, goal) group, since a planning problem needs all admitted
  objects together. `process_object` handles one agent call end-to-end and writes one
  log row immediately; `compile_and_plan_group` merges a group's processed objects into
  one domain+problem and runs Fast Downward once.
- **Stage 2 never trusts the agent's self-reported type.** `rdf_individuals.py` keeps it
  aside for the diagnostic comparison only; the individual is asserted with its observed
  properties alone, so HermiT's classification is a genuine, independent derivation
  (Definition 3.6), not a restatement of what the agent claimed.
- **Compiler-N and Compiler-F are deliberately separate modules**, not parameterized
  variants of one compiler — Variant A has no reference ontology to compile against at
  all, so sharing code would have meant threading a null-hierarchy case through every
  formal compiler stage for no benefit.
- **`report_raw.py` is the actual source of every number in `../results/`.** If you want
  to verify a figure rather than trust the write-up, run this script against
  `results.jsonl` yourself — see `../docs/reproducing-the-experiment.md`.

## Dependencies

HermiT (via `owlready2`), `rdflib`, pySHACL, and a working Fast Downward build (see
`../docs/reproducing-the-experiment.md` for exact setup steps — Fast Downward itself is
not vendored in this repository; it's built from the upstream source separately).
