# Goal-Dependent Grounding for LLM/VLM-to-PDDL Compilation via Formal Contracts

This repository is the companion to the paper:

> Nina Bąkowska and Krzysztof Zatwarnicki. **"Goal-Dependent Grounding for LLM/VLM-to-PDDL
> Compilation via Formal Contracts."** *[Venue, year — to be filled in after
> acceptance/publication.]*
>
> **Citation:** *[BibTeX / full citation to be added once the paper is published.]*

The paper introduces a formal frame around PDDL — a conceptual system of typed contracts
with a two-level, goal-dependent restriction mechanism (filtering by relevance and,
independently, contractual admissibility) — proves that this restriction shrinks
monotonically as a goal becomes more specific, and realises it in OWL 2 DL and SHACL. A
pilot grounds this frame in 32 real photographs via a vision-language agent.

## What's in this repository, and why it's more than the paper

**This repository contains material the paper only summarizes, compresses, or omits
outright for space** — it is not a duplicate of the paper's content, and several files
here exist specifically because the paper itself, at multiple points, points here rather
than including the full version inline. Concretely:

- Every proof the paper presents as a sketch (Theorem 4.1, Theorem 5.1, Lemma 4.1) or as
  compressed prose (Corollary 4.1′, Corollary 4.1) has its **full, unabridged proof**
  in `formal-proofs/`.
- The paper's 12-item symbolic walkthrough appears only in illustrative fragments across
  Sections 3–6; the **complete worked example** — full hierarchy, all 12 items, every
  goal's full derivation, and the actual OWL/SHACL/PDDL artifacts it compiles to — is in
  `worked-example/`.
- Variant D (the ablation deliberately violating Assumption 3.1) is no longer discussed
  in the paper's main text, cut for space during editing. Its prompt, ontology, and
  **full empirical results** — the same level of detail an earlier draft's dedicated
  Results subsection contained — are preserved in `agent-prompts/` and
  `results/variant-D-ablation-full-results.md`. The paper's Limitations section points
  here explicitly for these results.
- The six deliberate differences between the symbolic walkthrough and the real pipeline
  were originally their own table in the paper (`Section 7.3`), cut wholesale for space.
  The full table is in `results/six-differences-table.md`.
- The complete per-(variant, goal) breakdown — domain size, full accuracy categories,
  SHACL agreement, Fast Downward figures, at the same detail as the original working
  spreadsheet — is in `results/aggregate-tables.md`, of which the paper's own Table 5 is
  a compressed, two-comparison subset.

## Folder-by-folder orientation

**`formal-proofs/`** — Full, unabridged proofs for every result the paper states as a
sketch or in compressed prose. Read alongside Sections 3–5 of the paper.

**`worked-example/`** — The complete 12-item symbolic hierarchy, every goal's full
derivation, and the machine-readable OWL/SHACL/PDDL artifacts that realize it. If you
only read one thing here to understand how the formalism behaves concretely, read
`worked-example/README.md`.

**`pipeline/`** — The full, actually-run implementation: both compilers (Compiler-N for
the naive baseline, Compiler-F's four stages for the ontology-aware variants), the
OWL/SHACL realization, Ollama/Fast Downward orchestration, and the logging
infrastructure. See `pipeline/README.md` for a file-by-file map to the paper's Sections
5–7.

**`agent-prompts/`** — The complete, verbatim prompt text for all four experimental
variants (A/B/C/D), including Variant D's, which the paper's main text no longer
discusses.

**`experiment-data/`** — `reference_labels.json`, the ground-truth reference data for
all 32 objects; `images/`, the actual 32 photographs shown to the vision-language
agent; and full provenance notes distinguishing the 23 Open Food Facts-sourced
grocery items (with their attribution requirements) from the 9 items that are the
authors' own photographs.

**`results/`** — The full 384-row experimental log (`results.jsonl`, all four variants),
the complete aggregate-statistics breakdown, the full Variant D ablation write-up, and
the six-differences table cut from the paper.

**`docs/`** — `reproducing-the-experiment.md`: environment setup, how to run the
pipeline end to end, how to regenerate `results/results.jsonl` and every derived figure
from scratch, and how to recompile the paper itself.

## Reproducing this work

See [`docs/reproducing-the-experiment.md`](docs/reproducing-the-experiment.md) for a
full step-by-step guide, from environment setup through regenerating every reported
number and recompiling the paper.

## License

This repository is licensed under [CC BY 4.0](LICENSE), with one exception: property
values in `experiment-data/reference_labels.json` and the images in
`experiment-data/images/obj_001.jpg`–`obj_023.jpg` derived from Open Food Facts remain
subject to Open Food Facts' own ODbL/CC BY-SA licensing — see
`experiment-data/README.md` for details.
