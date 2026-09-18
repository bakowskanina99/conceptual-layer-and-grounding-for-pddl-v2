# Beyond Conjunctive Goals: A Three-Valued Constraint Language for Goal-Dependent Domain Restriction in Planning

This repository is the companion to an ICAART Position Paper (2nd stage submission).
Venue, year, and citation will be filled in after acceptance/publication.

The paper generalizes a goal-dependent restriction mechanism for planning domains —
one that filters a typed conceptual system by relevance and, independently,
contractual admissibility, before compilation to PDDL — from a flat conjunction of
equality/threshold conditions to a genuine three-valued Boolean constraint language
supporting disjunction, negation, and cross-feature linear conditions. It proves that
the mechanism's core monotonicity guarantee survives this generalization, states the
precise hypothesis (semantic entailment between constraint formulas) that replaces
the original flat-set-containment hypothesis, and works a disjunctive and a
cross-feature goal through a concrete hypermarket domain.

## What's in this repository

**`extended-constraint-language/README.md`** — the full formal content: constraint
atoms (simple and cross-feature), three-valued atom evaluation under partial
observation, Kleene K3 semantics, the generalized goal/type-contract/consistency/
admissibility definitions, the generalized monotonicity theorem with full proof, a
worked disjunctive and cross-feature example, and two explicitly flagged open items
(a scoping question in the type-level atom-evaluation clause, and the exact
boundary of a computational-cost result borrowed from the literature). This is the
paper's complete formal contribution — everything else below is background material
the new definitions build on.

## Background material this paper's constraint language generalizes

The definitions and theorem in `extended-constraint-language/` are a strict
generalization of a base formalism — flat conjunctive goals, type contracts as
required/forbidden feature-value pairs, and a two-level relevance/admissibility
restriction mechanism — together with a hypermarket conceptual system used
throughout to make that base formalism concrete. Both were developed and evaluated
in a separate, prior line of work; they are retained here only as the necessary,
self-contained background against which this paper's generalization is stated and
checked, not as this paper's own contribution:

- **`formal-proofs/`** — the base formalism's full proofs (monotone domain shrinking,
  the independence of relevance- and admissibility-exclusion, domain-size reduction),
  referenced throughout `extended-constraint-language/README.md` as "Theorem 4.1",
  "Lemma 4.1", etc.
- **`worked-example/`** — the 11-type hypermarket hierarchy and 12-item occurrence
  set that Section 3 of `extended-constraint-language/README.md` reuses for its
  disjunctive and cross-feature goals, plus the machine-readable OWL/SHACL/PDDL
  artifacts realizing it.
- **`pipeline/`, `agent-prompts/`, `experiment-data/`, `results/`, `docs/`** — the
  implementation, prompts, real photographic data, and results of an empirical pilot
  of the *base* (flat-conjunction) mechanism. This Position Paper introduces no new
  experiment of its own — it is a purely formal extension — so nothing here was
  produced for it; it is included because the base formalism it generalizes is
  defined relative to this same conceptual system and was itself empirically
  evaluated using it.

## License

This repository is licensed under [CC BY 4.0](LICENSE), with one exception: property
values in `experiment-data/reference_labels.json` and the images in
`experiment-data/images/obj_001.jpg`–`obj_023.jpg` derived from Open Food Facts remain
subject to Open Food Facts' own ODbL/CC BY-SA licensing — see
`experiment-data/README.md` for details.
