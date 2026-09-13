# The Variant D Ablation — Full Results

The paper's Limitations section states that Assumption 3.1's practical necessity "was
additionally validated empirically via a dedicated ablation deliberately violating
Assumption 3.1; full results are reported in the project's companion repository." This
file is that delivery. It reproduces, in full, what an earlier draft of the paper
reported as a dedicated Results subsection (C vs. D) before it was cut for space — the
same figures, the same interpretation, none of it compressed.

## 1. What Variant D is, and why it exists

Variant D receives a **deliberately weakened conceptual system**: the three
discriminating features (`category`, `food_type`, `produce_type`) are removed from
every affected type's contract, and the corresponding `owl:disjointWith` axioms are
removed alongside them for every sibling group except `DairyProduct`/`MeatProduct`,
whose disjointness is deliberately retained. This is a direct, minimal-axis violation of
**Assumption 3.1 (sibling discriminability)** — see `../pipeline/ontology/weakened.ttl`
for the executable OWL realization, and `../agent-prompts/full-prompts-all-variants.md`
for the exact JSON diff between the well-formed and weakened ontologies shown to the
agent.

Variant D is otherwise identical to Variant C in every instruction — the agent is never
told the ontology is weakened, or that this is an ablation, so that it cannot compensate
using its own world knowledge (which would contaminate the ablation by measuring the
model's general competence rather than the ontology's formal well-formedness).

The point of this ablation is to test the paper's Section 3.4 remark directly: that
violating Assumption 3.1 can manifest as **either** non-uniqueness (ambiguous grounding)
**or**, when siblings are additionally declared disjoint but their remaining contracts
still stand in a subset relationship, a **logical inconsistency** — two structurally
distinct failure modes, not one.

## 2. Headline result: ambiguous-grounding and reasoner-inconsistent rates, C vs. D

| Variant | Goal | Ambiguous grounding | Reasoner inconsistent | (for comparison) genuine misclassification |
|---|---|---|---|---|
| C | G2_real | 0.000 (0/29) | 0.000 (0/29) | 0.069 (2/29) |
| C | G3_real | 0.000 (0/29) | 0.000 (0/29) | 0.034 (1/29) |
| C | G4_real | 0.000 (0/30) | 0.000 (0/30) | 0.033 (1/30) |
| D | G2_real | 0.769 (20/26) | 0.231 (6/26) | 0.000 (0/26) |
| D | G3_real | 0.643 (18/28) | 0.107 (3/28) | 0.071 (2/28) |
| D | G4_real | 0.731 (19/26) | 0.038 (1/26) | 0.077 (2/26) |

Ambiguous-grounding and reasoner-inconsistent rates are **exactly zero for C across all
three goals** and **substantial for D in every case** — this is the paper's headline
ablation evidence, and it is reported here as two separate rates rather than one
aggregate specifically because Section 3.4's remark predicts two structurally different
failure modes, not a single one:

- **Ambiguous grounding dominates** (64.3–76.9% across the three goals), consistent with
  the predicted total, transitive collapse across the non-Dairy/Meat branch of the
  weakened hierarchy — once `category`/`food_type`/`produce_type` are gone, most sibling
  groups (`GroceryItem`/`HouseholdItem`/`ClothingItem`/`ElectronicsItem`,
  `FreshProduce`/`PackagedFood`, `Fruit`/`Vegetable`) have no discriminating feature left
  at all, so an object satisfying one type's (near-empty) contract typically satisfies
  several sibling contracts simultaneously — non-uniqueness, not inconsistency.
- **Reasoner inconsistency is smaller and specific** (3.8–23.1%), consistent with the
  localized Dairy/Meat contract-subset finding: `DairyProduct`/`MeatProduct` are the one
  sibling pair whose disjointness axiom was deliberately *retained* in the weakened
  ontology. When an object's remaining (non-discriminating) contract also happens to
  stand in a subset relationship with its sibling's, the combination of "satisfies both"
  and "declared disjoint" is a genuine `owl:disjointWith` contradiction — HermiT reports
  an unsatisfiable class, not merely an ambiguous multiple-satisfaction.

**Notably, `genuine_misclassification` itself is *not* dramatically different between C
and D** (0.0–7.7% for D against 3.3–6.9% for C) — the ablation's effect is concentrated
entirely in *whether an object is groundable at all*, not in the rate of wrong-but-
resolved answers. This is the sharper, more defensible reading of Assumption 3.1's
necessity than a single aggregate failure rate would have offered: **the assumption is
not protecting answer quality, it is protecting the ability to answer at all.**

## 3. Fast Downward: not run for any (D, goal) combination

| Variant | Goal | Fast Downward |
|---|---|---|
| D | G2_real | NOT RUN |
| D | G3_real | NOT RUN |
| D | G4_real | NOT RUN |

In every (D, goal) combination, either every object failed to ground uniquely (ambiguous
or inconsistent) or the few that did resolve were then correctly SHACL-excluded, leaving
nothing admitted or pending to compile a PDDL problem from. This is reported as a result
in its own right, not a discarded run: it is itself evidence of the ablation's severity —
a weakened conceptual system does not just produce worse plans, it can leave nothing to
plan over at all.

## 4. Domain size and JSON-parse-failure rate, for completeness

| Variant | Goal | domain_size | JSON-parse-failure |
|---|---|---|---|
| D | G2_real | 23 | 6/32 (18.8%) |
| D | G3_real | 23 | 4/32 (12.5%) |
| D | G4_real | 23 | 6/32 (18.8%) |

D's domain size (23) is smaller than C's (26) — a direct, mechanical consequence of the
weakened hierarchy having fewer surviving discriminated types, not a separate finding
requiring interpretation. D's parse-failure rate (16/96 = 16.7% overall) is the highest
of the four variants, consistent with the general pattern that longer, more constrained
prompts (Variant D's prompt is structurally identical to Variant C's, which is the
longest of the four) produce more first-attempt schema violations from the underlying
model — see `aggregate-tables.md` §4 for the full cross-variant comparison.

## 5. Relationship to the paper's formal claims

This ablation is **empirical support**, not a substitute, for the paper's formal
argument (Section 3.4's remark, proved by construction from the definitions, not from
this data). The remark's claim — that a violation of Assumption 3.1 can manifest as
either non-uniqueness or logical inconsistency depending on whether siblings are
additionally declared disjoint and how their residual contracts relate — is a logical
consequence of Definitions 3.5/3.6 and holds regardless of what any particular ablation
run happens to show. What this ablation adds is confirmation that both predicted failure
modes actually occur, at the predicted relative magnitudes (large-scale ambiguity from
the broadly-weakened branch, smaller and localized inconsistency from the one branch
where disjointness was deliberately retained), on real photographic data rather than
only in the abstract.

## Source data

All figures above are computed by `../pipeline/scripts/report_raw.py` directly from
`results.jsonl`'s 96 Variant-D rows (32 objects × 3 goals). Re-run the script yourself to
verify any number in this file — see `../docs/reproducing-the-experiment.md`.
