# Symbolic Walkthrough vs. Real Pipeline — Six Deliberate Differences

Sections 3–6's formal development and its 12-item symbolic worked example (see
`../worked-example/`) remain the paper's reference specification. The real,
photograph-grounded pipeline described in the paper's Section 7 instantiates the same
formalism but departs from the symbolic example in six specific, individually justified
ways. This table collected them in one place in an earlier draft of the paper, before
being cut for space — each is a real engineering decision with a traceable
justification, not an oversight, and the full table is reproduced here in full since it
remains genuinely useful context for understanding exactly where and why the real
pipeline diverges from the symbolic walkthrough.

| # | Symbolic walkthrough | Real pipeline | Reason |
|---|---|---|---|
| 1 | `is_vegan` (Boolean) | `veganAttributeMatch` (0–100), synthesized deterministically from the agent's reported `is_vegan` (`true`→100, `false`→0, unasserted→unasserted) | The VLM can judge veganness but not OFF's internal 0–100 score directly (see the paper's remark on feature-name alignment, Section 4.2; `../pipeline/compilers/compiler_formal/vegan_attribute_synthesis.py`) |
| 2 | `R(G_4)`: `calories` ≤ 150 | `R(G4_real)`: `calories` ≤ 55 | Recalibrated to the real sample's actual calorie distribution (52–70 kcal/100g for vegan items) so that `G3_real` and `G4_real` diverge empirically rather than being vacuously identical — a value closer to the symbolic walkthrough's illustrative 150 would have admitted every vegan item in this particular sample |
| 3 | `expiry_date` asserted in Occurrences | Excluded from OWL reasoning (Stage 2) entirely, though still logged and compiled into PDDL `:init` | A malformed (non-ISO) date string was found to trigger a spurious reasoner inconsistency unrelated to Assumption 3.1; since `expiry_date` plays no role in any contract, goal, or shape, it is simply never asserted to the reasoner |
| 4 | `in_stock` gates the `put-in-cart` action precondition | Precondition drops `in_stock` for the real-data domains (the predicate is still declared and populated whenever observed) | Genuinely unobservable from a single product photograph, unlike the symbolic walkthrough where it is stipulated |
| 5 | Twelve objects described together in one illustrative pass | One Ollama call per object (384 base combinations: 32 objects × 4 variants × 3 goals) | Maximises crash-resilience and enables true per-object incremental logging (see `../pipeline/logging_/incremental_writer.py`); the shared prompt's literal "obj_001 through obj_N" phrasing collapses to `obj_001` on every call as a consequence (`N=1` always) — object identity is tracked by the calling harness, not read from the model's own response |
| 6 | Goals treated as fixed background context | Variant B (no goal-dependent restriction) is nonetheless run separately for all three goals, not cached and reused | A determinism check (identical prompt, object, and variant repeated three times) confirmed the model's core classification fields are stable under repetition, but the *same* object under *different* goal phrasing was found to receive different answers — a goal-text sensitivity, not model non-determinism, but one that invalidates reusing Variant B's output across goals (see `runs/b_invariance_raw` in the project's working files and `b_invariance_check.jsonl`) |

## Where this fits relative to the paper

This table was originally the paper's Section 7.3 ("Symbolic Walkthrough versus the Real
Pipeline: Six Deliberate Differences"), a full `table*` spanning both columns. It was cut
in its entirety during a page/character-budget reduction pass, since the paper is
constrained to ICAART's submission character limit. Row 2's threshold justification and
row 6's Variant B determinism finding were judged load-bearing enough that one sentence
each was folded into the paper's remaining prose (Section 7, "The Three Variants"
subsection, and Section 7's goal-calibration paragraph) rather than lost outright; rows
1, 3, 4, and 5 are recorded only here.
