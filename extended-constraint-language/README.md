# Extended Constraint Language — Full Formal Content

This document generalizes the goal-dependent restriction mechanism already given in
this repository's `formal-proofs/full-proofs.md` and `worked-example/README.md` from a
flat conjunction of equality/threshold conditions to a genuine three-valued Boolean
constraint language: disjunction, negation, and cross-feature linear conditions,
evaluated under Kleene's strong three-valued logic (K3) to preserve the same
open-world treatment of missing observations. Everything needed to read this document
is either defined here or already present elsewhere in this repository — nothing in
it depends on any other repository.

---

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
f_k \bowtie c_0)$.

### 1.2 Three-valued atom evaluation under partial observation

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
and is not optional): the value of $\alpha$ is
- $\mathsf{F}$, if any $f_i \notin \mathrm{feat}(t)$ — some involved feature is not
  merely unobserved but *structurally inapplicable* to $t$: no instance of $t$ could
  ever supply an observation for it, so $\alpha$ can never contribute to satisfying
  $\psi_G$ for this type, regardless of what any particular instance does or doesn't
  observe;
- otherwise, $\alpha$'s value is whatever the truth assignment under consideration in
  Definition 8's satisfiability check assigns it, subject to consistency with
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
contract against a goal *before* any instance is in view.

### 1.3 Constraint formulas and Kleene semantics

**Definition 4 (Constraint formula).** The set of constraint formulas $\Psi$ over
$\mathcal{F}$ is defined inductively: every atom is a formula; if $\psi_1, \psi_2 \in
\Psi$, then $(\psi_1 \wedge \psi_2)$, $(\psi_1 \vee \psi_2)$, $\neg \psi_1 \in \Psi$.

**Definition 5 (Strong three-valued Kleene semantics, K3).** The value of a compound
formula under $\mathcal{O}(o)$ (instance-level) or under a type $t$ (type-level) is
computed recursively:

| $\psi_1$ | $\psi_2$ | $\psi_1 \wedge \psi_2$ | $\psi_1 \vee \psi_2$ |
|---|---|---|---|
| T | T | T | T |
| T | F | F | T |
| T | U | U | T |
| F | F | F | F |
| F | U | F | U |
| U | U | U | U |

with $\neg\mathsf{T}=\mathsf{F}$, $\neg\mathsf{F}=\mathsf{T}$, $\neg\mathsf{U}=\mathsf{U}$.

This is the standard strong three-valued logic K3 (Kleene, 1952) — applied here, not
proposed anew. Section 2's computational remark returns to a specific fragment of this
language for which a related tractability result (Baumann and Heinrich, 2023) applies.

### 1.4 Generalized goal and type contract

**Definition 6 (Generalized goal).** A goal is a pair $G = (T_G, \psi_G)$, where
$\psi_G \in \Psi$ is a single constraint formula, replacing the separate
$\Phi(G)$/$R(G)$ of the base formalism (`formal-proofs/full-proofs.md`,
`worked-example/README.md`) — a threshold is now simply a threshold atom inside the
same formula, not a separately structured component.

**Definition 7 (Generalized type contract).** $K^+(t)$, $K^-(t)$ are now sets of atoms
(simple or cross-feature), required/forbidden conjunctively. **Deliberate scoping
decision:** type contracts remain flat conjunctions, not full Boolean formulas —
allowing disjunction inside a contract would blur the sibling-discriminability
structure Assumption 3.1 depends on (`worked-example/README.md`, Section 2, and the
`owl:AllDisjointClasses` axioms in
`worked-example/ontology/well_formed_and_encoding.md`). This is a stated design
choice, not an oversight, and is the same restriction Baumann and Heinrich's bipolar
normal form exploits computationally in a different setting — see Section 2 below.

### 1.5 Generalized consistency and instance admissibility

**Definition 8 (Generalized goal-contract consistency).** $\psi_G \sim K(t)$ holds iff
there exists a truth assignment to $\psi_G$'s atoms — with any atom over a feature $f
\notin \mathrm{feat}(t)$ fixed to $\mathsf{F}$ when $t \in D_{\mathrm{rel}}(G)$, per
Definition 3's type-level clause — consistent with the values $K^+(t)/K^-(t)$ already
fix on the shared, applicable features, under which $\psi_G$ evaluates to $\mathsf{T}$
(Definition 5) — i.e., $\psi_G$ is satisfiable given both what the type's contract
already fixes and what the type's own feature set structurally rules out.

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

**Definition 9 (Generalized instance admissibility).** For object $o$ with grounded
type $t$:
- $G$-admitted if $t \in D(G)$ and $\psi_G$ evaluates to $\mathsf{T}$ under
  $\mathcal{O}(o)$;
- $G$-excluded if $t \notin D(G)$, or $\psi_G$ evaluates to $\mathsf{F}$;
- $G$-pending if $t \in D(G)$ and $\psi_G$ evaluates to $\mathsf{U}$.

A direct three-valued generalization of the admitted/excluded/pending trichotomy
already used throughout this repository (Proposition 4.1's proof in
`formal-proofs/full-proofs.md`; the per-item classification in
`worked-example/README.md`, Section 3), exact in the flat-conjunction special case.

---

## 2. Main result — generalized monotonicity theorem

**Theorem (generalizing Theorem 4.1 of `formal-proofs/full-proofs.md`).** Let $G, G'$
share the same target type set $T_G = T_{G'}$, and let $\psi_{G'} \models \psi_G$
(semantic entailment: every assignment satisfying $\psi_{G'}$ satisfies $\psi_G$).
Then $D(G') \subseteq D(G)$.

**Proof.** The relevance level is unaffected — the same argument as Theorem 4.1's
Step 1, depending only on $T_G$. At the admissibility level: suppose $t \notin
D_{\mathrm{adm}}(G)$, i.e. $\psi_G \not\sim K(t)$ — no assignment consistent with
$K(t)$ makes $\psi_G = \mathsf{T}$ (Definition 8). Suppose, toward contradiction, that
$t \in D_{\mathrm{adm}}(G')$ — some assignment $\alpha$ consistent with $K(t)$ makes
$\psi_{G'}(\alpha) = \mathsf{T}$. Since $\psi_{G'} \models \psi_G$, every assignment
satisfying $\psi_{G'}$ satisfies $\psi_G$ too — so $\psi_G(\alpha) = \mathsf{T}$. But
$\alpha$ is consistent with $K(t)$ by construction, contradicting the assumption that
no such assignment exists for $\psi_G$. Hence $t \notin D_{\mathrm{adm}}(G')$.
$\blacksquare$

**Reduction check.** If $\Phi(G) \subseteq \Phi(G')$ in the original, flat-set sense,
then under the natural embedding $\psi_G := \bigwedge \Phi(G)$, $\psi_{G'} \models
\psi_G$ holds automatically (a conjunction over a superset semantically entails the
conjunction over the subset) — Theorem 4.1 is exactly the special case of this one,
not merely compatible with it. Re-derived directly from Theorem 4.1's actual statement
before being accepted here, not from a restatement of it.

**Remark (Lemma on independence of relevance and admissibility).** The independence of
relevance-exclusion and admissibility-exclusion as two distinct mechanisms —
established via witness construction in `formal-proofs/full-proofs.md` (Lemma 4.1) —
was checked against the generalized language using the same two witnesses (a topically
irrelevant type; a relevant type whose contract directly conflicts).

> **Resolved.** Witness (i) (`HouseholdItem` against a vegan goal) specifically relies
> on $\Phi(G_3) \sim K(t_1)$ holding *vacuously*, since `is_vegan` $\notin
> \mathrm{feat}(\text{HouseholdItem})$. Definition 3's type-level clause — introduced
> to correctly exclude `PackagedFood` from $G_{\mathrm{disj}}$ in Section 3 below —
> would, if applied unconditionally, force exactly this kind of atom to $\mathsf{F}$,
> making $\psi_{G_3} \not\sim K(\text{HouseholdItem})$ too and contradicting witness
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
follow-up question, not resolved here.

---

## 3. Illustrative example — hypermarket domain

This section reuses the type hierarchy and contracts already given in this
repository's `worked-example/README.md` (11 types: `GroceryItem` and its subtree —
`FreshProduce`→{`Fruit`,`Vegetable`}, `PackagedFood`, `DairyProduct`, `MeatProduct` —
plus `HouseholdItem`, `ClothingItem`, `ElectronicsItem`), applying the new formalism to
two goals not previously used there, to keep the illustration self-contained while
staying within the same conceptual system.

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
Definition 8). *Both* disjuncts therefore evaluate to $\mathsf{F}$ for this type, so
$\psi_{\mathrm{disj}} = \mathsf{F} \vee \mathsf{F} = \mathsf{F}$ (Definition 5):
Definition 8's consistency check fails, and `PackagedFood` is genuinely
**admissibility-excluded** — a type-level exclusion the mechanism itself now produces,
correctly invoking Definition 8, rather than an unlicensed reading of "inapplicable"
as false.

### Cross-feature goal

$G_{\mathrm{cross}}$: "flag fresh produce for premium/import handling where price
exceeds four times its weight in kilograms":

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
