# Agent Prompts — All Four Variants, Full Text

`full-prompts-all-variants.md` is the complete, verbatim prompt specification for all
four experimental conditions described in Section 7 of the paper — including **Variant
D**, which is included here in full even though it is no longer discussed in the paper's
main text (see `../results/variant-D-ablation-full-results.md` for what it was used for).

The document contains, in order:

1. **The shared output JSON schema** — identical across all four variants by design, so
   that any difference in downstream domain size or accuracy traces back to what each
   variant was *given* and *instructed to prioritise*, never to an incidental difference
   in output format.
2. **Variant A** — no conceptual system (naive baseline).
3. **Variant B** — full well-formed conceptual system, no goal-dependent restriction.
4. **Variant C** — full conceptual system + goal-dependent restriction (the paper's main
   proposed mechanism).
5. **Variant D** — identical to Variant C in every instruction, with the well-formed
   ontology replaced by the deliberately weakened one (Assumption 3.1 violated). The
   agent is never told the ontology is weakened or that this is an ablation.
6. **The two ontology JSON blocks** actually embedded in the Variant B/C and Variant D
   prompts respectively, so the exact difference between them (three discriminating
   features removed, nothing else) is inspectable directly rather than only described.
7. Practical implementation notes (templating, raw-output logging, context window).

For the code that renders these templates programmatically per (variant, goal, photo
batch) at call time, see `../pipeline/prompts/`.
