# Aggregate Results Tables — Full Breakdown, All Four Variants

Every number in this file is computed directly from `results.jsonl` (384 rows) by
`../pipeline/scripts/report_raw.py` — nothing here is hand-typed or hand-aggregated.
Run the script yourself (see `../docs/reproducing-the-experiment.md`) to regenerate this
exact output. This is the full, uncompressed version of the paper's Table 5 (which
covers only Variants A/B/C, since Variant D is no longer discussed in the paper's main
text — see `variant-D-ablation-full-results.md` for the full D write-up).

Accuracy is broken into four mutually exclusive, exhaustive categories (verified in code
to sum to the denominator exactly, for every row): `exact_match`, `ancestor_fallback`
(Definition 3.4's undetermined case — an ancestor type correctly inferred from
deliberately minimal reporting, not an error), `genuine_misclassification` (a real wrong
answer), and `ungroundable` (ambiguous_grounding or reasoner_inconsistent — reported
separately by rate below, and included here too so nothing is silently dropped from the
denominator). Variant A has no formal hierarchy, so the ancestor-fallback distinction
does not apply to it; only exact-match vs. everything-else is reported for A.

## 1. Overview — domain size, exact-match rate, ambiguous/inconsistent rates, Fast Downward

| Variant | Goal | domain_size | exact_match | amb_rate | inconsist_rate | FD (actions) |
|---|---|---|---|---|---|---|
| A | G2_real | 62 | 0.125 (4/32) | 0.000 (0/32) | 0.000 (0/32) | 23 |
| A | G3_real | 22 | 0.219 (7/32) | 0.000 (0/32) | 0.000 (0/32) | 12 |
| A | G4_real | 8  | 0.281 (9/32) | 0.000 (0/32) | 0.000 (0/32) | 9 |
| B | G2_real | 36 | 0.903 (28/31) | 0.000 (0/31) | 0.000 (0/31) | 31 |
| B | G3_real | 36 | 0.906 (29/32) | 0.000 (0/32) | 0.031 (1/32) | 31 |
| B | G4_real | 36 | 0.871 (27/31) | 0.000 (0/31) | 0.032 (1/31) | 30 |
| C | G2_real | 26 | 0.724 (21/29) | 0.000 (0/29) | 0.000 (0/29) | 20 |
| C | G3_real | 26 | 0.414 (12/29) | 0.000 (0/29) | 0.000 (0/29) | 11 |
| C | G4_real | 26 | 0.400 (12/30) | 0.000 (0/30) | 0.000 (0/30) | 3 |
| D | G2_real | 23 | 0.000 (0/26) | 0.769 (20/26) | 0.231 (6/26) | NOT RUN |
| D | G3_real | 23 | 0.179 (5/28) | 0.643 (18/28) | 0.107 (3/28) | NOT RUN |
| D | G4_real | 23 | 0.154 (4/26) | 0.731 (19/26) | 0.038 (1/26) | NOT RUN |

D's Fast Downward is "NOT RUN" for every goal: in every (D, goal) combination, either
every object failed to ground uniquely or the few that did were then correctly
SHACL-excluded, leaving nothing admitted or pending to compile a problem from.

## 2. Full accuracy breakdown — all four categories, all four variants

| Variant | Goal | exact_match | ancestor_fallback | genuine_misclass | ungroundable |
|---|---|---|---|---|---|
| A | G2_real | 0.125 (4/32) | n/a | 0.875 (28/32) | n/a |
| A | G3_real | 0.219 (7/32) | n/a | 0.781 (25/32) | n/a |
| A | G4_real | 0.281 (9/32) | n/a | 0.719 (23/32) | n/a |
| B | G2_real | 0.903 (28/31) | 0.000 (0/31) | 0.097 (3/31) | 0.000 (0/31) |
| B | G3_real | 0.906 (29/32) | 0.031 (1/32) | 0.031 (1/32) | 0.031 (1/32) |
| B | G4_real | 0.871 (27/31) | 0.000 (0/31) | 0.097 (3/31) | 0.032 (1/31) |
| C | G2_real | 0.724 (21/29) | 0.207 (6/29) | 0.069 (2/29) | 0.000 (0/29) |
| C | G3_real | 0.414 (12/29) | 0.552 (16/29) | 0.034 (1/29) | 0.000 (0/29) |
| C | G4_real | 0.400 (12/30) | 0.567 (17/30) | 0.033 (1/30) | 0.000 (0/30) |
| D | G2_real | 0.000 (0/26) | 0.000 (0/26) | 0.000 (0/26) | 1.000 (26/26) |
| D | G3_real | 0.179 (5/28) | 0.000 (0/28) | 0.071 (2/28) | 0.750 (21/28) |
| D | G4_real | 0.154 (4/26) | 0.000 (0/26) | 0.077 (2/26) | 0.769 (20/26) |

Each row's four figures sum to exactly 1.000 (verified by an assertion in
`report_raw.py` itself, not just by eye) — e.g. D/G3_real: 0.179 + 0.000 + 0.071 + 0.750
= 1.000.

## 3. SHACL agreement, scoped to `D_rel(G)` (Variants C and D only — B has no Stage 3)

Excludes objects structurally outside the goal's relevant domain, for which agreement is
undefined by construction (comparing the agent's combined relevance+admissibility
decision against SHACL's admissibility-only verdict is not a fair test for an object
SHACL never even targets — see `../pipeline/scripts/report_raw.py`'s
`shacl_agreement_rate` docstring for the full reasoning, including why this was found
directly in the data rather than assumed).

| Variant | Goal | SHACL agreement (scoped) | Excluded (out of scope) |
|---|---|---|---|
| C | G2_real | 1.000 (20/20) | 9 |
| C | G3_real | 1.000 (20/20) | 9 |
| C | G4_real | 0.611 (11/18) | 12 |
| D | G2_real | n/a (0 in-scope) | 0 |
| D | G3_real | 1.000 (7/7) | 0 |
| D | G4_real | 1.000 (6/6) | 0 |

## 4. JSON-parse-failure (dropped-object) counts, per (variant, goal)

| Variant | G2_real | G3_real | G4_real | Variant total |
|---|---|---|---|---|
| A | 0/32 | 0/32 | 0/32 | 0/96 (0.0%) |
| B | 1/32 | 0/32 | 1/32 | 2/96 (2.1%) |
| C | 3/32 | 3/32 | 2/32 | 8/96 (8.3%) |
| D | 6/32 | 4/32 | 6/32 | 16/96 (16.7%) |
| **All** | | | | **26/384 (6.8%)** |

This is the full basis for the paper's Operational Cost figure (3.5%, 10/288, computed
over Variants A–C only, since Variant D's data is no longer part of the paper's main
results) and, restoring D, the original 6.8% (26/384) figure this table reproduces
exactly.

## 5. Pairwise comparison groupings (as reported in the paper's Section 8)

The paper's two headline comparisons are simple filters over the tables above, not
separately-collected data:

- **A vs. C** (Section 8.1): rows 1–3 vs. rows 7–9 of tables 1–2 above.
- **B vs. C** (Section 8.2): rows 4–6 vs. rows 7–9 of tables 1–2 and table 3 above.
- **C vs. D** (originally Section 8.3, removed from the paper's main text for space —
  see `variant-D-ablation-full-results.md`): rows 7–9 vs. rows 10–12 above.
