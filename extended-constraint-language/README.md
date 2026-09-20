# Extended Constraint Language — Full Formal Content

This document generalizes the goal-dependent restriction mechanism already given in
this repository's `formal-proofs/full-proofs.md` and `worked-example/README.md` from a
flat conjunction of equality/threshold conditions to a genuine Boolean constraint
language: disjunction, negation, and cross-feature linear conditions, evaluated under
a **partial-information semantics** — three values (T/F/U) at the instance level,
extended to a **four-valued** logic at the type level with one additional value,
$\mathsf{NA}$, for atoms over structurally inapplicable features (Definition 3,
Definition 5). Everything needed to read this document is either defined here or
already present elsewhere in this repository — nothing in it depends on any other
repository.

**On this document's own history.** Problems found: an
inapplicability value that silently broke under negation (Section 1.2/1.3's
$\mathsf{NA}$, replacing an earlier, wrong use of $\mathsf{F}$), and a classical
logical equivalence (De Morgan's law) that does not survive four-valuedness (Section
1.3's second remark, and Definition 10 below). Both are reported here, with their
fixes, rather than smoothed over, since a semantics that looks obviously right until
checked against a concrete case is exactly the failure mode this kind of formal
argument needs to guard against.

---

## 0. Preliminaries (restated for self-containedness)

These base-formalism notions (`formal-proofs/full-proofs.md`, `worked-example/
README.md`) are restated, not re-derived, so the rest of this document is readable on
its own: $\mathcal{O}$ is a partial observation function — $\mathcal{O}(o)$ gives an
object $o$'s observed feature values, and a feature not in $\mathrm{dom}(\mathcal{O}
(o))$ is *unobserved*, never defaulted to false (open-world). $\mathrm{feat}(t)$ is
type $t$'s declared feature set. Given a goal's target type set $T_G$:
$D_{\mathrm{rel}}(G)$, the *relevance domain*, is the set of types reachable from
$T_G$ via the subtype order $\leq_T$; $D_{\mathrm{adm}}(G) := \{t \in
D_{\mathrm{rel}}(G) : \psi_G \sim K(t)\}$ (Definition 8), the *admissibility domain*,
further restricts this to types whose contract is consistent with the goal; and
$D(G) := D_{\mathrm{rel}}(G) \cap D_{\mathrm{adm}}(G)$ is the resulting *active
domain* — the type set the planning domain is actually restricted to.

## 1. Formalism — full definitions

### 1.1 Constraint atoms

**Definition 1 (Simple atom).** For a feature $f \in \mathcal{F}$ (the conceptual
system's feature set, declared type-by-type in
`worked-example/ontology/well_formed_and_encoding.md`): an equality atom is $(f = v)$
for $v \in \mathrm{dom}(f)$; if $f$ is ordered, a threshold atom is $(f \bowtie v)$ for
$\bowtie \in \{\leq, <, \geq, >\}$.

**Definition 2 (Cross-feature linear atom).** For numeric features $f_1, \ldots, f_k
\in \mathcal{F}$, rational coefficients $c_1, \ldots, c_k, c_0$, and comparator
$\bowtie \in \{=, \leq, <, \geq, >\}$: a cross-feature atom is $(c_1 f_1 + \cdots + c_k
f_k \bowtie c_0)$. **Units, stated explicitly:** each $c_i$ carries whatever unit
makes the sum dimensionally consistent — e.g. in the worked cross-feature goal
(Section 3), the coefficient $4$ on `weight` carries units of currency per kilogram,
so `price` (currency) minus `4 * weight` (currency) is a currency quantity, not an
implicit unit mismatch.

### 1.2 Atom evaluation under partial observation (three values at instance level, four at type level)

**Definition 3 (Atom value).** Let $\alpha$ be an atom (simple or cross-feature)
depending on features $f_1, \ldots, f_k$. Definition 8 and Definition 9 below invoke
$\alpha$'s value in two different contexts, and the value is computed differently in
each:

*Instance-level* (used by Definition 9, for an object $o$ with an already-grounded
type $t$): the value of $\alpha$ under $\mathcal{O}(o)$ is
- $\mathsf{U}$ (undefined), if any $f_i \notin \mathrm{dom}(\mathcal{O}(o))$ — at least
  one involved feature is a declared feature of $t$ but is unobserved on this
  particular instance (open-world; see e.g. item #11 in `worked-example/README.md`,
  Section 3, recorded as unobserved rather than false);
- otherwise $\mathsf{T}$ if the condition numerically/categorically holds for the
  observed values, else $\mathsf{F}$.

*Type-level* (used by Definition 8, for a type $t$ with declared feature set
$\mathrm{feat}(t)$, **and only when $t \in D_{\mathrm{rel}}(G)$** — see the scoping
note immediately after Definition 8, which states why this restriction is necessary
and is not optional — **and only for leaf, groundable types**, never internal
supertype nodes; see Definition 8's second scoping note): the value of $\alpha$ is
- $\mathsf{NA}$ (structurally inapplicable — see Definition 5 for its algebra), if any
  $f_i \notin \mathrm{feat}(t)$ — some involved feature is not merely unobserved but
  *structurally inapplicable* to $t$: no instance of $t$ could ever supply an
  observation for it, so $\alpha$ can never contribute to satisfying $\psi_G$ for this
  type, regardless of what any particular instance does or doesn't observe.
  $\mathsf{NA}$ is a distinct value from $\mathsf{U}$ above: $\mathsf{U}$ means "this
  feature could apply to this object but happens not to have been observed";
  $\mathsf{NA}$ means "this feature could never apply to this *type* at all." An
  earlier version of this clause used $\mathsf{F}$ here instead of a dedicated value —
  the remark after Definition 5 explains exactly why that was wrong and had to be
  corrected;
- otherwise, $\alpha$'s value is whatever the feature valuation $\sigma$ under
  consideration in Definition 8's satisfiability check assigns it (Definition 8 below
  states precisely what $\sigma$ is and why), subject to consistency with
  $K^+(t)/K^-(t)$'s already-fixed values on the shared, applicable features.

For $t \notin D_{\mathrm{rel}}(G)$, this type-level clause does not apply at all —
Definition 8's evaluation of $\psi_G \sim K(t)$ for such a $t$ instead retains the
original, unconditional consistency reading (a feature absent from $t$'s contract
entirely produces no conflict, hence no exclusion), unchanged from before this clause
was introduced.

The instance-level clause directly extends the open-world principle to cross-feature
atoms: the absence of even one involved, *applicable* feature renders the entire atom
undefined, not merely false. The type-level clause is different in kind — it is not a
claim about what some instance does or doesn't observe, but about whether the feature
could ever be observed for that type at all — which is exactly why Definition 9 does
not need it: an object's grounded type has already settled feature-applicability
before Definition 9 is ever evaluated, whereas Definition 8 must check a type's
contract against a goal *before* any instance is in view. Definition 9 therefore only
ever evaluates atoms to $\mathsf{T}$, $\mathsf{F}$, or $\mathsf{U}$ — $\mathsf{NA}$ is
exclusively a type-level, pre-grounding value, so instance classification
(admitted/excluded/pending) remains an exhaustive trichotomy, unaffected by the
fourth value's introduction.

### 1.3 Constraint formulas (negation normal form) and four-valued semantics

**Definition 4 (Constraint formula, negation normal form).** The set of constraint
formulas $\Psi$ over $\mathcal{F}$ is restricted to negation normal form (NNF) by
construction: every atom $\alpha$ is a formula, so is its negation $\neg\alpha$
(negation applies only to atoms, never to a compound sub-formula), and if $\psi_1,
\psi_2 \in \Psi$, then $(\psi_1 \wedge \psi_2)$ and $(\psi_1 \vee \psi_2)$ are too.
**Deliberate scoping restriction, not a loss of expressiveness for this language's
purposes:** $\neg(\psi_1 \wedge \psi_2)$ is not itself well-formed — write the
De Morgan-equivalent $\neg\psi_1 \vee \neg\psi_2$ directly if that is intended. This
sidesteps, rather than patches, the problem described in Section 1.3's second remark
below: $\mathsf{NA}$ makes classical De Morgan equivalence unsafe once compound
negation is allowed, so restricting the grammar removes the unsafe construction from
the language entirely, rather than asking every goal author to reason about when it
is safe. Every goal used in this document's Section 3, and every goal in the
12-item worked example (`worked-example/README.md`), is already expressible in this
restricted grammar — each negation there applies directly to a single atom — so
nothing already relied upon is lost.

**Definition 5 (Four-valued semantics: K3 extended with $\mathsf{NA}$).** The value of
a compound formula under $\mathcal{O}(o)$ (instance-level) or under a type $t$
(type-level) is computed recursively over $\{\mathsf{T}, \mathsf{F}, \mathsf{U},
\mathsf{NA}\}$:

| $\psi_1$ | $\psi_2$ | $\psi_1 \wedge \psi_2$ | $\psi_1 \vee \psi_2$ |
|---|---|---|---|
| T | T | T | T |
| T | F | F | T |
| T | U | U | T |
| T | NA | NA | T |
| F | F | F | F |
| F | U | F | U |
| F | NA | NA | F |
| U | U | U | U |
| U | NA | NA | U |
| NA | NA | NA | NA |

with $\neg\mathsf{T}=\mathsf{F}$, $\neg\mathsf{F}=\mathsf{T}$, $\neg\mathsf{U}=\mathsf{U}$,
and, critically, $\neg\mathsf{NA}=\mathsf{NA}$ — $\mathsf{NA}$ **never flips to a usable
truth value under negation**. Restricted to $\{\mathsf{T},\mathsf{F},\mathsf{U}\}$, this
is exactly the standard strong three-valued logic K3 (Kleene, 1952), applied here, not
proposed anew, for those three values and $\wedge$/$\vee$/$\neg$ among them.
$\mathsf{NA}$ and its three governing rules —

- $\neg\mathsf{NA} = \mathsf{NA}$,
- $\mathsf{NA} \wedge X = \mathsf{NA}$ for every $X \in \{\mathsf{T},\mathsf{F},\mathsf{U},\mathsf{NA}\}$
  (a conjunction requiring a structurally impossible condition is itself structurally
  impossible), and
- $\mathsf{NA} \vee X = X$ for every $X$ (an inapplicable disjunct contributes nothing;
  the disjunction's value is exactly whatever the other disjunct's value is) —

are **not** part of K3 or any other named, off-the-shelf logic. They were derived
specifically for this formalism, to fix the bug described immediately below, and are
flagged here honestly as a genuine, non-standard extension whose properties have not
been fully characterized — a real fourth truth value, not a relabelling of
$\mathsf{F}$ or $\mathsf{U}$ — rather than presented as an established system merely
being applied.

**Remark (why a fourth value, and why $\mathsf{F}$ was wrong).** An earlier version of
Definition 3's type-level clause used $\mathsf{F}$, not $\mathsf{NA}$, for a
structurally-inapplicable feature. This is fine for atoms in *positive* position — see
the oat-drink case in Section 3 below, re-verified against $\mathsf{NA}$ there — but
breaks under negation, because $\neg\mathsf{F} = \mathsf{T}$: a goal $\psi_G =
\neg(\mathrm{price} > 10)$ evaluated for a type $t$ with no `price` feature would have
the `price` atom forced to $\mathsf{F}$, hence $\psi_G$ forced to $\mathsf{T}$ —
Definition 8 would then read $t$ as satisfying $\psi_G$, admitting it as though "not
expensive" had been affirmatively checked, when in fact price was never even a
meaningful question for $t$. With $\mathsf{NA}$ in place of $\mathsf{F}$, and
$\neg\mathsf{NA} = \mathsf{NA}$: the `price` atom is $\mathsf{NA}$, so $\psi_G =
\neg\mathsf{NA} = \mathsf{NA} \neq \mathsf{T}$ — Definition 8's check correctly fails,
and $t$ is not admitted via this route. **This specific counterexample no longer
arises**, because $\mathsf{NA}$, unlike $\mathsf{F}$, has no truth-value polarity for
negation to flip — stated narrowly, about this one counterexample, not as a
categorical claim about the extension's correctness in general, since a second,
different counterexample (below) was found in this same logic after this first one
was fixed. Section 3 below re-verifies both the original motivating case (the
oat-drink disjunction) and this negation case concretely, against the new value.

**Remark (classical equivalence does not carry over: a second counterexample).** A
second, independent review found that classical (two-valued) logical equivalences are
not safe to assume under this four-valued semantics, even though the fix above looked
complete. Take De Morgan's law, $\neg(A \wedge B) \equiv \neg A \vee \neg B$,
classically valid for any $A, B$. Under the table above, with $A = \mathsf{NA}$ and $B
= \mathsf{F}$: $A \wedge B = \mathsf{NA}$ (the rule $\mathsf{NA}\wedge X = \mathsf{NA}$),
so $\neg(A \wedge B) = \neg\mathsf{NA} = \mathsf{NA}$; but $\neg A \vee \neg B =
\mathsf{NA} \vee \mathsf{T} = \mathsf{T}$ (the rule $\mathsf{NA}\vee X = X$, with $X =
\mathsf{T}$). The two sides diverge: $\mathsf{NA} \neq \mathsf{T}$. This does **not**
make the monotonicity theorem (Section 2) false — nothing in its statement or proof
assumed De Morgan's law — but it means the theorem's entailment hypothesis must be
given a precise, checkable definition rather than invoked as an informal "semantic
entailment" that classical intuitions about equivalence could silently mislead a
reader (or an author) about. Definition 10 (Section 2) gives that precise definition,
and Definition 4's NNF restriction independently closes off this specific
counterexample's syntactic trigger ($\neg(A \wedge B)$ is simply not well-formed),
though the semantic point — classical equivalence is not a safe substitute for
checking $\models_4$ directly — stands regardless of which formulas the grammar
admits.

Section 2's computational remark returns to a specific fragment of this language for
which a related tractability result (Baumann and Heinrich, 2023) applies; see the
caveat added there about atoms that evaluate to $\mathsf{NA}$.

### 1.4 Generalized goal and type contract

**Definition 6 (Generalized goal).** A goal is a pair $G = (T_G, \psi_G)$, where
$\psi_G \in \Psi$ is a single constraint formula, replacing the separate
$\Phi(G)$/$R(G)$ of the base formalism (`formal-proofs/full-proofs.md`,
`worked-example/README.md`) — a threshold is now simply a threshold atom inside the
same formula, not a separately structured component.

**Definition 7 (Generalized type contract).** $K^+(t)$, $K^-(t)$ are now sets of atoms
(simple or cross-feature), required/forbidden conjunctively. **Deliberate scoping
decision, with justification:** type contracts remain flat conjunctions, not full
Boolean formulas. The underlying formalism's well-formedness requirement checks that
sibling types' contracts pick out disjoint, machine-verifiable value sets (via
`owl:AllDisjointClasses` over each contract's required-feature values,
`worked-example/ontology/well_formed_and_encoding.md`) — Assumption 3.1
(`worked-example/README.md`, Section 2). A contract built as a disjunction of
value-combinations would need that same disjointness check to hold for *every*
disjunct against every sibling, multiplying the check without changing what a single
flat conjunction already verifies cleanly — the restriction buys nothing here and is
kept out by design, the same restriction Baumann and Heinrich's bipolar normal form
exploits computationally in a different setting — see Section 2 below.

### 1.5 Generalized consistency and instance admissibility

**Definition 8 (Generalized goal-contract consistency).** Rather than an unstructured
"truth assignment to $\psi_G$'s atoms" — which would let dependent atoms over the
same feature (e.g. $(f \leq 3)$ and $(f \leq 5)$) be assigned independently, an
inconsistency a reviewer correctly flagged — consistency is defined via a single
*feature valuation*. Let $\sigma : \mathrm{feat}(t) \to \bigcup_f \mathrm{dom}(f)$
assign every one of $t$'s declared features a value from its domain (**numeric
domains are taken to be $\mathbb{Q}$**, not $\mathbb{R}$, matching the QF_LRA
decidability discussion below); write $\sigma \models K(t)$ if $\sigma$ satisfies
every atom in $K^+(t)$ and falsifies every atom in $K^-(t)$. Then

$$\psi_G \sim K(t) \iff \exists\, \sigma\, \big(\sigma \models K(t) \;\wedge\;
\llbracket \psi_G \rrbracket_{t,\sigma} = \mathsf{T}\big),$$

where $\llbracket \psi_G \rrbracket_{t,\sigma}$ is $\psi_G$'s value (Definition 5)
with each atom evaluated against $\sigma$ where applicable (Definition 3's
"otherwise" clause) or forced to $\mathsf{NA}$ where not (its type-level clause).
Because $\sigma$ is a single, total function over $\mathrm{feat}(t)$, every atom
referencing the same feature $f$ necessarily agrees with the one value $\sigma(f)$
assigns it — dependent atoms are tied together correctly, unlike independently-
assignable Boolean propositions. **This strengthens, not just fixes, the existing
QF_LRA computational remark:** deciding $\psi_G \sim K(t)$ is now precisely a
constraint-satisfaction question over feature valuations — exactly the question an
SMT solver for this fragment decides — not merely analogous to one.

**Scoping note (why Definition 3's type-level clause is restricted to $t \in
D_{\mathrm{rel}}(G)$).** This clause applies only when $t \in D_{\mathrm{rel}}(G)$ —
i.e., only when Definition 8 is being asked a question that could actually arise in a
real computation of $D(G)$, since $D_{\mathrm{adm}}(G) := \{t \in D_{\mathrm{rel}}(G) :
\psi_G \sim K(t)\}$ by construction never evaluates Definition 8 for a type outside
$D_{\mathrm{rel}}(G)$ at all. Outside $D_{\mathrm{rel}}(G)$, the original
vacuous-consistency reading (a feature absent from $t$'s contract entirely produces no
conflict, hence no exclusion) is retained — this is the reading Lemma 4.1's
independence witnesses (`formal-proofs/full-proofs.md`) deliberately rely on,
evaluating $\Phi(G) \sim K(t)$ hypothetically for a type known to be excluded by
relevance, specifically to demonstrate that admissibility *alone* would not have
caught it. That is a different question (would admissibility alone, in isolation from
relevance, flag a problem here?) from the one Definition 8 answers inside a real
$D(G)$ computation (is this already-relevant type also admissible?) — the restriction
keeps the two questions from colliding under one clause.

**Scoping note (leaf types only).** This check is defined, and only ever evaluated,
for *leaf* types — the types an object can actually ground to (Definition 3.6 of the
base formalism) — never for internal (supertype) nodes of the type hierarchy. This is
a deliberate scoping decision, not an oversight: for an internal type such as a
grocery-item supertype, it is genuinely ambiguous whether $\mathrm{feat}(t)$ should
include features declared only on its subtypes, and answering that the wrong way
risks incorrectly excluding a supertype the compiled PDDL type hierarchy structurally
needs. Internal nodes are retained in the compiled domain automatically whenever any
descendant leaf type is retained, independent of this admissibility check — a
structural requirement of valid PDDL type hierarchies (see e.g.
`worked-example/pddl/compiled_domains.md`'s type declarations), not a separate
question Definition 8 needs to answer.

**Definition 9 (Generalized instance admissibility).** For object $o$ with grounded
type $t$:
- $G$-admitted if $t \in D(G)$ and $\psi_G$ evaluates to $\mathsf{T}$ under
  $\mathcal{O}(o)$;
- $G$-excluded if $t \notin D(G)$, or $\psi_G$ evaluates to $\mathsf{F}$;
- $G$-pending if $t \in D(G)$ and $\psi_G$ evaluates to $\mathsf{U}$.

This remains an **exhaustive trichotomy**: $\mathsf{NA}$ can only arise during
Definition 8's type-level check, never during this instance-level evaluation
(Definition 3's instance-level clause has no $\mathsf{NA}$ case, by construction — a
grounded object's type has already settled feature-applicability), so the fourth
value's introduction leaves instance classification exactly as before. A direct
three-valued generalization of the admitted/excluded/pending trichotomy already used
throughout this repository (Proposition 4.1's proof in `formal-proofs/full-proofs.md`;
the per-item classification in `worked-example/README.md`, Section 3), exact in the
flat-conjunction special case.

---

## 2. Main result — generalized monotonicity theorem

**Definition 10 (Four-valued entailment).** $\psi' \models_4 \psi$ iff for every
valuation $\nu$ over the atoms occurring in $\psi'$ and $\psi$, $\llbracket \psi'
\rrbracket_\nu = \mathsf{T}$ implies $\llbracket \psi \rrbracket_\nu = \mathsf{T}$.
**This must be checked directly in the four-valued semantics, not assumed from
classical equivalences:** Section 1.3's second remark shows $\neg A \vee \neg B$ and
$\neg(A \wedge B)$ are classically (two-valued) De Morgan-equivalent, yet with $A =
\mathsf{NA}, B = \mathsf{F}$ the first evaluates to $\mathsf{T}$ and the second to
$\mathsf{NA}$ — so $\neg A \vee \neg B \not\models_4 \neg(A \wedge B)$, even though the
two formulas would be indistinguishable under classical logic.

**Theorem (generalizing Theorem 4.1 of `formal-proofs/full-proofs.md`).** Let $G, G'$
share the same target type set $T_G = T_{G'}$, and let $\psi_{G'} \models_4 \psi_G$
(Definition 10). Then $D(G') \subseteq D(G)$.

**Proof.** The relevance level is unaffected — the same argument as Theorem 4.1's
Step 1, depending only on $T_G$. At the admissibility level: suppose $t \notin
D_{\mathrm{adm}}(G)$, i.e. $\psi_G \not\sim K(t)$ — no valuation $\sigma$ with $\sigma
\models K(t)$ (Definition 8) makes $\psi_G$ evaluate to $\mathsf{T}$. Suppose, toward
contradiction, that $t \in D_{\mathrm{adm}}(G')$ — some valuation $\sigma$ with
$\sigma \models K(t)$ makes $\llbracket \psi_{G'} \rrbracket_{t,\sigma} = \mathsf{T}$.
**By definition of $\models_4$** ($\psi_{G'} \models_4 \psi_G$, with $\sigma$ playing
the role of the universally-quantified valuation $\nu$), $\llbracket \psi_G
\rrbracket_{t,\sigma} = \mathsf{T}$ too. But $\sigma \models K(t)$ by construction,
contradicting the assumption that no such valuation exists for $\psi_G$. Hence $t
\notin D_{\mathrm{adm}}(G')$. $\blacksquare$

**The proof step that matters survives unchanged, once stated precisely.** The step
"since $\psi_{G'} \models \psi_G$, $\sigma$ satisfying $\psi_{G'}$ implies $\sigma$
satisfies $\psi_G$" was always the crux of this argument; with $\models$ left
undefined, a reader could reasonably (and, per Section 1.3's second remark,
incorrectly) fill it in with classical equivalence. With Definition 10, that step is
not an inference at all — it is $\models_4$'s definition applied directly, with
$\sigma$ instantiating the universally-quantified valuation $\nu$. Only the
previously implicit, easy-to-misread hypothesis needed fixing; the theorem and its
proof are otherwise exactly as before.

**Non-preservation disclaimer.** The theorem establishes monotonicity of the selected
type domain only; it does not establish plan-preservation, completeness, optimality,
or runtime improvement.

**Reduction check — sufficient, not necessary (corrected).** If $\Phi(G) \subseteq
\Phi(G')$ in the original, flat-set sense, then under the natural embedding $\psi_G :=
\bigwedge \Phi(G)$, $\psi_{G'} \models_4 \psi_G$ holds automatically (a conjunction
over a superset semantically entails the conjunction over the subset) — syntactic
containment is a **sufficient** condition for $\models_4$ under this embedding, **not
a necessary one**: $\models_4$ is strictly more general even restricted to simple
threshold atoms, e.g. $(f \leq 3) \models_4 (f \leq 5)$ holds with no syntactic
containment between the two atoms at all. Theorem 4.1 is thus recoverable as the
special case where $\psi_G$ is a flat conjunction and containment is assumed — a
**special case of this one, not an exact equivalence with it** — which is why this is
presented as a strict generalization, not merely a compatible, separately-derived
statement.

**Remark (Lemma on independence of relevance and admissibility).** The independence of
relevance-exclusion and admissibility-exclusion as two distinct mechanisms —
established via witness construction in `formal-proofs/full-proofs.md` (Lemma 4.1) —
was checked against the generalized language using the same two witnesses (a topically
irrelevant type; a relevant type whose contract directly conflicts).

> **Resolved.** Witness (i) (`HouseholdItem` against a vegan goal) specifically relies
> on $\Phi(G_3) \sim K(t_1)$ holding *vacuously*, since `is_vegan` $\notin
> \mathrm{feat}(\text{HouseholdItem})$. Definition 3's type-level clause — introduced
> to correctly exclude `PackagedFood` from $G_{\mathrm{disj}}$ in Section 3 below —
> would, if applied unconditionally, force exactly this kind of atom to $\mathsf{NA}$
> (structurally inapplicable; $\mathsf{F}$ in an earlier, corrected version of this
> clause — see Definition 5's remark), making $\psi_{G_3} \not\sim K(\text{HouseholdItem})$
> too either way, since neither value is $\mathsf{T}$, and contradicting witness
> (i) as stated (which needs admissibility to hold vacuously, not fail, precisely so
> that relevance is shown to be doing the excluding *alone*). The fix that correctly
> excludes `PackagedFood` (a *relevant* type lacking one feature) and the witness that
> needs vacuous consistency to hold (an *irrelevant* type lacking a different feature)
> were pulling in opposite directions over the same clause.
>
> This is resolved by restricting Definition 3's type-level clause to $t \in
> D_{\mathrm{rel}}(G)$ — see Definition 3 and the scoping note directly after
> Definition 8 above, which state the restriction and its justification in full where
> the clause itself is defined. In short: $D_{\mathrm{adm}}(G) := \{t \in
> D_{\mathrm{rel}}(G) : \psi_G \sim K(t)\}$ by construction never evaluates Definition
> 8 for a type outside $D_{\mathrm{rel}}(G)$ at all, so the restriction changes nothing
> about what a real $D(G)$ computation ever does — it only changes the answer to a
> hypothetical question (would admissibility alone flag this type?) that Lemma 4.1's
> witnesses ask about a type *already known to be irrelevant*, which is a different
> question from the one Definition 8 answers for a type *already known to be
> relevant*. `HouseholdItem` is outside $D_{\mathrm{rel}}(G_3)$, so the restricted
> clause does not apply to it and the original vacuous-consistency reading — and hence
> witness (i) exactly as stated in `formal-proofs/full-proofs.md` — goes through
> unchanged. `PackagedFood` is inside $D_{\mathrm{rel}}(G_{\mathrm{disj}})$ (see
> Section 3's explicit statement of $T_{G_{\mathrm{disj}}}$), so the restricted clause
> does apply to it and the corrected oat-drink example below is unaffected by this
> restriction.

**Remark (computational cost, corrected scope).** Definition 8's satisfiability
check, restricted to the equality-atom fragment of the language (Definition 1's
simple equality atoms only, no thresholds or cross-feature atoms), reduces to a single
Kleene K3 evaluation whenever $\psi_G$ is syntactically *bipolar* (no atom occurs with
both positive and negative polarity) relative to the partial interpretation $K(t)$
induces: satisfiability corresponds exactly to the K3 value being different from
$\mathsf{F}$ (not merely equal to $\mathsf{T}$), since a K3 value of $\mathsf{U}$
already signals that some two-valued completion evaluates to $\mathsf{T}$ (Baumann and
Heinrich, 2023, Theorem 2/3) — turning the check from general satisfiability into a
single tractable evaluation for that fragment. This does not extend automatically to
threshold or cross-feature atoms: Baumann and Heinrich's result assumes atoms are
semantically independent Boolean propositions, which fails once atoms can stand in
arithmetic entailment relationships with each other (e.g. $(f \leq 3)$ entails $(f
\leq 5)$) — extending the tractability result to cover this is a concrete, open
follow-up question, not resolved here. **Caveat added with $\mathsf{NA}$ (Definition
5):** this remark's fragment implicitly assumes every atom in $\psi_G$ is applicable to
$t$, i.e. none evaluates to $\mathsf{NA}$ — Baumann and Heinrich's result is stated for
three-valued Boolean propositions, and whether their tractability argument extends
unchanged once some atoms can additionally take the value $\mathsf{NA}$ is not checked
here.

---

## 3. Illustrative example — hypermarket domain

This section reuses the type hierarchy and contracts already given in this
repository's `worked-example/README.md` (11 types: `GroceryItem` and its subtree —
`FreshProduce`→{`Fruit`,`Vegetable`}, `PackagedFood`, `DairyProduct`, `MeatProduct` —
plus `HouseholdItem`, `ClothingItem`, `ElectronicsItem`), applying the new formalism to
three goals not previously used there, to keep the illustration self-contained while
staying within the same conceptual system. All three are already expressible in
Definition 4's NNF grammar — each negation below applies directly to a single atom.

### Disjunctive goal

$G_{\mathrm{disj}}$: "route fresh produce — fruit or vegetable — to the express
fresh-produce lane", with $T_{G_{\mathrm{disj}}} = \{\text{GroceryItem}\}$ (deliberately
broad: `PackagedFood`, `DairyProduct`, and `MeatProduct` are all $\leq_T
\text{GroceryItem}$ too, hence all in $D_{\mathrm{rel}}(G_{\mathrm{disj}})$ — it is the
disjunctive constraint below, not $T_G$, that is meant to separate fresh produce from
the rest):

```
ψ_disj = (produce_type = fruit) ∨ (produce_type = vegetable)
```

Evaluation on three items: an apple (`produce_type=fruit`) — first disjunct
$\mathsf{T}$, so $\psi_{\mathrm{disj}} = \mathsf{T}$ (Kleene: $\mathsf{T} \vee
\mathsf{F} = \mathsf{T}$) — **admitted**. A carrot (`produce_type=vegetable`) —
likewise **admitted** via the second disjunct.

A carton of oat drink (`PackagedFood`) has no `produce_type` at all:
`produce_type` $\notin \mathrm{feat}(\text{PackagedFood})$ — `produceType` is declared
only on `store:FreshProduce` in
`worked-example/ontology/well_formed_and_encoding.md`, and `PackagedFood` is a sibling
of `FreshProduce`, not a descendant of it. `PackagedFood` $\leq_T \text{GroceryItem}$,
so `PackagedFood` $\in D_{\mathrm{rel}}(G_{\mathrm{disj}})$ — Definition 3's type-level
clause applies (it is restricted to exactly this case; see the scoping note after
Definition 8). *Both* disjuncts therefore evaluate to $\mathsf{NA}$ (structurally
inapplicable) for this type, so $\psi_{\mathrm{disj}} = \mathsf{NA} \vee \mathsf{NA} =
\mathsf{NA}$ (Definition 5's rule $\mathsf{NA} \vee X = X$, with $X = \mathsf{NA}$):
$\psi_{\mathrm{disj}} \neq \mathsf{T}$, Definition 8's consistency check fails, and
`PackagedFood` is genuinely **admissibility-excluded** — a type-level exclusion the
mechanism itself now produces, correctly invoking Definition 8, using a dedicated
"structurally inapplicable" value rather than overloading $\mathsf{F}$ with a meaning
it does not have.

### Negation over a possibly-inapplicable feature

$G_{\mathrm{notvegan}}$: "flag anything **confirmed non-vegan** for the
general-merchandise handling lane" — not, as a looser reading might suggest, "anything
not confirmed vegan": $\neg\mathsf{U} = \mathsf{U}$ means an unobserved-but-applicable
`is_vegan` is *pending*, not flagged, so this description is fixed to match exactly
what the formula computes, no more — with $T_{G_{\mathrm{notvegan}}} =
\{\text{StoreItem}\}$ (deliberately the whole store, so household items are relevant
too) and

```
ψ_notvegan = ¬(is_vegan = true)
```

For `HouseholdItem`: `is_vegan` $\notin \mathrm{feat}(\text{HouseholdItem})$ —
`isVegan` is declared only on `store:GroceryItem` and its descendants
(`worked-example/ontology/well_formed_and_encoding.md`), and `HouseholdItem` is a
sibling of `GroceryItem`, not a descendant. `HouseholdItem` $\leq_T \text{StoreItem}$,
so `HouseholdItem` $\in D_{\mathrm{rel}}(G_{\mathrm{notvegan}})$ and Definition 3's
type-level clause applies: the `is_vegan = true` atom evaluates to $\mathsf{NA}$, so
$\psi_{\mathrm{notvegan}} = \neg\mathsf{NA} = \mathsf{NA}$ (Definition 5) —
$\psi_{\mathrm{notvegan}} \neq \mathsf{T}$, Definition 8's consistency check fails, and
`HouseholdItem` is **admissibility-excluded**, exactly as `PackagedFood` was above.
**This is the case that was broken before $\mathsf{NA}$ existed:** under the earlier,
corrected clause using $\mathsf{F}$, the same atom would have been forced to
$\mathsf{F}$, so $\psi_{\mathrm{notvegan}} = \neg\mathsf{F} = \mathsf{T}$ would have
held — Definition 8 would have wrongly admitted `HouseholdItem`, as if "not vegan" had
been affirmatively confirmed for an item where veganness is not even a meaningful
question. With $\mathsf{NA}$ and $\neg\mathsf{NA} = \mathsf{NA}$, that flip cannot
happen.

For `MeatProduct` (a `GroceryItem` descendant, so `is_vegan` *is* declared): if
observed `is_vegan = false`, the atom is $\mathsf{F}$ at the instance level (Definition
3's instance-level clause; this is a genuinely observed, applicable feature, not an
inapplicable one), so $\psi_{\mathrm{notvegan}} = \neg\mathsf{F} = \mathsf{T}$ —
correctly **admitted** (confirmed non-vegan, exactly as flagged): here the negation
*should* flip $\mathsf{F}$ to $\mathsf{T}$, because the feature genuinely applies and
was genuinely observed false. If `is_vegan` is instead genuinely applicable but
unobserved on some `MeatProduct` instance, the atom is $\mathsf{U}$ and
$\psi_{\mathrm{notvegan}} = \neg\mathsf{U} = \mathsf{U}$ — **pending**, matching the
corrected description above exactly, not flagged. $\mathsf{NA}$ changes nothing about
ordinary, applicable negation — only about negation over a feature that could never
have applied in the first place.

### Cross-feature goal

$G_{\mathrm{cross}}$: "flag fresh produce for premium/import handling where price
exceeds four times its weight in kilograms" (the coefficient $4$ carrying units of
currency per kilogram, per Definition 2's units note, so the subtraction below is
dimensionally consistent):

$$\psi_{\mathrm{cross}} = (\text{price} - 4 \cdot \text{weight} > 0)$$

Evaluation: an item priced 12.00 at 2.0 kg: $12.00 - 4(2.0) = 4.0 > 0$ — $\mathsf{T}$ —
**flagged**. An item priced 3.00 at 2.0 kg: $3.00 - 4(2.0) = -5.0 > 0$? No —
$\mathsf{F}$ — **not flagged**.

### Partial-observation case

An item with `produce_type = fruit` observed, but `weight` unobserved (label rubbed
off — the same open-world scenario used throughout this repository, e.g. item #11 in
`worked-example/README.md`). Under $G_{\mathrm{disj}}$: **admitted** (depends only on
`produce_type`, fully observed, and `produce_type` is a declared feature of this
item's type, so Definition 3's *instance-level* clause applies, not the type-level
one). Under $G_{\mathrm{cross}}$: `weight` *is* a declared feature of this item's type
but is unobserved on this instance — the cross-feature atom involves it, so by
Definition 3's instance-level clause the whole atom is $\mathsf{U}$ —
$\psi_{\mathrm{cross}} = \mathsf{U}$ — **pending**, not excluded, exactly the intended
behaviour rather than a silently assumed default.
