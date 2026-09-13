# Full Proofs — Companion to Sections 3–5 of the Paper

This document gives the complete, unabridged proofs for the results that appear in the
paper as proof *sketches* (Theorem 4.1, Theorem 5.1, Lemma 4.1) or as compressed
explanatory prose (Corollary 4.1′, Corollary 4.1). Definitions and notation (T, ≤_T,
K⁺/K⁻, Φ(G), R(G), D(G), etc.) are as given in Sections 3–4 of the paper; they are not
restated here in full, only referenced. Type and feature names (`GroceryItem`,
`is_vegan`, etc.) are set in inline code formatting throughout rather than LaTeX
`\texttt{}`, since this file is read as GitHub-rendered Markdown, not compiled through
a full LaTeX engine.

---

## Lemma 4.1 (Independence of relevance and admissibility exclusion)

**Statement.** Relevance-exclusion and admissibility-exclusion are logically independent
reasons for a type's absence from $D(G)$: there exist a goal $G$ and types $t_1, t_2 \in
T$ such that (i) $t_1 \notin D_{\mathrm{rel}}(G)$ while $\Phi(G) \sim K(t_1)$ would hold
if relevance were disregarded, and (ii) $t_2 \in D_{\mathrm{rel}}(G)$ but $\Phi(G)
\not\sim K(t_2)$.

**Full proof (by witness construction).** Take $G = G_3$ ("vegan groceries") from the
worked example, so $T_{G_3} = \{\text{GroceryItem}\}$ and $\Phi(G_3) =
\{(v_f, \mathsf{true})\}$ where $v_f$ is the `is_vegan` feature.

*(i)* Let $t_1 =$ `HouseholdItem`. By construction of the conceptual system, the
`is_vegan` feature is not in `HouseholdItem`'s feature set at all. Since neither
$K^+(t_1)$ nor $K^-(t_1)$ can contain any pair involving `is_vegan` (a contract can
only constrain features in the type's own feature set), Definition 4.3's consistency
check $\Phi(G_3) \sim K(t_1)$ holds *vacuously* — there is no feature for which both
$\Phi(G_3)$ and $K(t_1)$ make a claim, so no conflict can arise. Yet $t_1 \notin
D_{\mathrm{rel}}(G_3)$: by Definition 4.2, $D_{\mathrm{rel}}(G_3) = \{t \in T : t
\leq_T \text{GroceryItem}\}$, and $\text{HouseholdItem} \not\leq_T \text{GroceryItem}$
since they are siblings under `StoreItem`, not related by the subtype order. So $t_1$
is excluded from $D(G_3)$ purely by relevance, with admissibility never even brought to
bear.

*(ii)* Let $t_2 =$ `MeatProduct`. Since `MeatProduct` $\leq_T$ `GroceryItem` directly
(an immediate child of `GroceryItem`, a sibling of `FreshProduce`/`PackagedFood`/
`DairyProduct`), $t_2 \in D_{\mathrm{rel}}(G_3)$ by Definition 4.2 — $t_2$ is
*relevant*. But `K^+(MeatProduct)` fixes `is_vegan = false` by the type's own
contract (established in Section 3's worked hierarchy). Definition 4.3 requires, for
$\Phi(G_3) \sim K(t_2)$ to hold, that there be no feature $f$ and values $v_1 \neq v_2$
with $(f, v_1) \in \Phi(G_3)$ and $(f, v_2) \in K^+(t_2)$. Here $f =$ `is_vegan`, $v_1 =
\mathsf{true}$ (from `Φ(G_3)`), $v_2 = \mathsf{false}$ (from `K^+(t_2)`) — exactly
such a pair, so $\Phi(G_3) \not\sim K(t_2)$, and $t_2 \notin D_{\mathrm{adm}}(G_3)$
despite $t_2 \in D_{\mathrm{rel}}(G_3)$. So $t_2$ is excluded from $D(G_3)$ purely by
inadmissibility, with relevance never in question.

Since $t_1$ is excluded by relevance alone (admissibility check never fails — indeed
never even engages) and $t_2$ is excluded by admissibility alone (relevance check
succeeds), the two exclusion mechanisms are witnessed as operating independently: neither
is a special case or restatement of the other. $\blacksquare$

**Why this matters beyond the specific witnesses.** The proof technique generalises:
whenever a type's own feature set does not overlap with the features a goal constrains
(case i's pattern), only relevance can exclude it; whenever a type's contract fixes a
value that directly contradicts one of the goal's required values (case ii's pattern),
admissibility does the excluding regardless of relevance. A conceptual system where every
type's contract happened to be consistent with every goal ever posed would still have
relevance-driven exclusion; a single-type conceptual system (no sibling branches to be
irrelevant to) would still have admissibility-driven exclusion. The two mechanisms answer
genuinely different questions ("does this type's *topic* matter to the goal?" versus
"does this type's *contract* contradict the goal's requirements?"), which is precisely
why Definition 4.2 (relevance) and Definition 4.4 (admissibility) had to be defined
separately in the first place rather than as one combined filter.

---

## Theorem 4.1 (Monotone shrinking of the active domain under increasing specificity)

**Statement.** Let $G, G'$ share the same target type set ($T_G = T_{G'}$) with $\Phi(G)
\subseteq \Phi(G')$. Then $D(G') \subseteq D(G)$.

**Full proof.**

*Step 1 — relevance is unaffected.* By Definition 4.2, $D_{\mathrm{rel}}(G) =
\bigcup_{t \in T_G} \{t' \in T : t' \leq_T t\}$, a function purely of the target type set
$T_G$. Since $T_G = T_{G'}$ by hypothesis, $D_{\mathrm{rel}}(G) = D_{\mathrm{rel}}(G')$
identically — the two goals share exactly the same relevant domain; $\Phi$ plays no role
in Definition 4.2 at all.

*Step 2 — admissibility can only shrink.* We show $D_{\mathrm{adm}}(G') \subseteq
D_{\mathrm{adm}}(G)$ by contraposition: suppose $t \notin D_{\mathrm{adm}}(G)$. By
Definition 4.4, this means $t \in D_{\mathrm{rel}}(G)$ (else it wouldn't be a candidate
for $D_{\mathrm{adm}}$ at all — recall $D_{\mathrm{adm}}(G) \subseteq D_{\mathrm{rel}}(G)$
by construction) but $\Phi(G) \not\sim K(t)$. By Definition 4.3, $\Phi(G) \not\sim K(t)$
means there exists a feature $f$ and values $v_1 \neq v_2$ such that $(f, v_1) \in
\Phi(G)$ and $(f, v_2) \in K^+(t)$ (the argument is symmetric if the conflict is instead
with $K^-(t)$: $(f, v) \in \Phi(G)$ and $(f, v) \in K^-(t)$ for some shared $v$). Take the
first case. Since $\Phi(G) \subseteq \Phi(G')$ by hypothesis, the same pair $(f, v_1)$ is
also a member of $\Phi(G')$. But $(f, v_2) \in K^+(t)$ is a fact about the type $t$'s
contract, entirely independent of which goal we're checking against — it doesn't change
between $G$ and $G'$. So the *same* witness pair $(f, v_1) \in \Phi(G')$, $(f, v_2) \in
K^+(t)$ demonstrates $\Phi(G') \not\sim K(t)$ too, i.e. $t \notin D_{\mathrm{adm}}(G')$.

We have shown: $t \notin D_{\mathrm{adm}}(G) \Rightarrow t \notin D_{\mathrm{adm}}(G')$.
Contrapositively, $t \in D_{\mathrm{adm}}(G') \Rightarrow t \in D_{\mathrm{adm}}(G)$ for
every $t \in T$ — which is exactly the statement $D_{\mathrm{adm}}(G') \subseteq
D_{\mathrm{adm}}(G)$.

*Step 3 — combine.* $D(G) := D_{\mathrm{adm}}(G)$ by Definition 4.5. From Step 1,
$D_{\mathrm{rel}}(G) = D_{\mathrm{rel}}(G')$, so both $D_{\mathrm{adm}}(G)$ and
$D_{\mathrm{adm}}(G')$ are subsets drawn from the *same* relevant domain, and Step 2
shows the admissibility-filtered subset only shrinks. Therefore $D(G') = D_{\mathrm{adm}}
(G') \subseteq D_{\mathrm{adm}}(G) = D(G)$. $\blacksquare$

**Note on why the proof is this short.** The entire argument rests on one observation:
a type's contract $K(t)$ does not depend on which goal is being evaluated — only
$\Phi(G)$ does, and $\Phi(G) \subseteq \Phi(G')$ is exactly the hypothesis that lets a
witness of inconsistency transfer forward from the smaller constraint set to the larger
one. This is a general pattern (monotone filters composed with a growing constraint set
only ever remove more, never fewer, elements) — the mathematical content is simple by
design; the actual contribution is having defined `D_rel`/`D_adm`/`D` as the *right*
three-way decomposition in the first place (see Lemma 4.1 above and
the paper's Introduction for why this decomposition, not the proof technique, is the
paper's claimed contribution).

---

## Corollary 4.1′ (Monotonicity jointly in `T_G` and `Φ(G)`)

**Statement.** If $T_G \subseteq T_{G'}$ (holding $\Phi(G) = \Phi(G')$ and $R(G) =
R(G')$ fixed), then $D(G) \subseteq D(G')$.

**Full proof.** By Definition 4.2, $D_{\mathrm{rel}}(G) = \bigcup_{t \in T_G}
{\downarrow}t$ where ${\downarrow}t := \{t' \in T : t' \leq_T t\}$ is the down-set of $t$.
Since $T_G \subseteq T_{G'}$, the union defining $D_{\mathrm{rel}}(G)$ ranges over a
subset of the index set that defines $D_{\mathrm{rel}}(G')$:
```
D_rel(G) = union over t in T_G of (down-set of t)
         ⊆ union over t in T_G' of (down-set of t)
         = D_rel(G')
```
This is immediate from the general set-theoretic fact that a union over a subset of an
index set is contained in the union over the full index set — no property of down-sets
specifically is needed beyond this.

Since $\Phi(G) = \Phi(G')$ by hypothesis, Definition 4.3's consistency check $\Phi(G)
\sim K(t)$ and $\Phi(G') \sim K(t)$ are the *same* check for every $t$ — so
$D_{\mathrm{adm}}(G) = \{t \in D_{\mathrm{rel}}(G) : \Phi(G) \sim K(t)\}$ and
$D_{\mathrm{adm}}(G') = \{t \in D_{\mathrm{rel}}(G') : \Phi(G') \sim K(t)\}$ apply
*identical* admissibility filtering criteria, differing only in which relevant-domain
set they're filtering. Since $D_{\mathrm{rel}}(G) \subseteq D_{\mathrm{rel}}(G')$ and
the filter itself is unchanged, $D_{\mathrm{adm}}(G) \subseteq D_{\mathrm{adm}}(G')$
follows directly: every $t$ passing the (identical) filter while drawn from the smaller
set $D_{\mathrm{rel}}(G)$ is also drawn from the larger set $D_{\mathrm{rel}}(G')$ and
still passes the same filter. Hence $D(G) = D_{\mathrm{adm}}(G) \subseteq
D_{\mathrm{adm}}(G') = D(G')$. $\blacksquare$

**Why the combined-direction case is genuinely not guaranteed.** If both $T_G \subseteq
T_{G'}$ *and* $\Phi(G) \subseteq \Phi(G')$ hold simultaneously (target types grow *and*
constraints tighten at once), the two effects pull in opposite directions: growing
$T_G$ can only add candidate types to $D_{\mathrm{rel}}$, while growing $\Phi(G)$ can
only remove types from $D_{\mathrm{adm}}$ within whatever $D_{\mathrm{rel}}$ turns out to
be. A concrete counterexample to "monotone in both simultaneously" is easy to construct:
let $G$ have $T_G = \{\text{GroceryItem}\}$, $\Phi(G) = \emptyset$ (so $D(G) =
D_{\mathrm{rel}}(G)$, all 7 grocery-side types, no admissibility filtering at all), and
let $G'$ have $T_{G'} = \{\text{GroceryItem}, \text{HouseholdItem}\}$ (a strict superset of
$T_G$) with $\Phi(G') = \{(v_f, \mathsf{true})\}$ (a strict superset of $\Phi(G) =
\emptyset$), where $v_f$ is `is_vegan`. Here $D_{\mathrm{rel}}(G') \supsetneq
D_{\mathrm{rel}}(G)$ (gained `HouseholdItem` and its subtree), but $D_{\mathrm{adm}}(G')$
has *lost* `DairyProduct`/`MeatProduct` relative to $D(G)$ due to the new admissibility
constraint — so neither $D(G) \subseteq D(G')$ nor $D(G') \subseteq D(G)$ holds in
general once both axes move at once. This is why Theorem 4.1 and Corollary 4.1′ are
stated as two *separate* results (each varying only one axis while holding the other
fixed), not folded into one theorem claiming joint monotonicity.

---

## Proposition 4.1 (Monotone shrinking of admitted instances under increasing thresholds)

**Statement.** Let $G, G'$ satisfy the hypotheses of Theorem 4.1 ($T_G = T_{G'}$,
`Φ(G) ⊆ Φ(G')`), and additionally $R(G) \subseteq R(G')$ (every threshold
in $R(G')$ is at least as strict as some threshold in $R(G)$ on the same feature). Then
every object that is $G'$-admitted is also $G$-admitted.

**Full proof.** Let $o$ be $G'$-admitted, with grounded type $t = G_{\mathrm{cert}}
(o,\mathcal{C})$. By Definition 4.6, $G'$-admission requires: (a) $t \in D(G')$, (b)
$\forall (f,v) \in \Phi(G'): \mathcal{O}(o)(f) = v$, and (c) $\forall (f,{\bowtie},v) \in
R(G'): \mathcal{O}(o)(f) \bowtie v$, with every such $f$ observed.

*(a) implies `t ∈ D(G)`:* by Theorem 4.1, $D(G') \subseteq D(G)$, so $t \in D(G')
\Rightarrow t \in D(G)$ directly.

*(b) implies `Φ(G)`'s constraints are satisfied:* since $\Phi(G) \subseteq \Phi(G')$,
every pair $(f,v) \in \Phi(G)$ is also in $\Phi(G')$, and (b) already establishes
$\mathcal{O}(o)(f) = v$ for every such pair (since it holds for the larger set
$\Phi(G')$, it holds in particular for the subset `Φ(G)`).

*(c) implies `R(G)`'s constraints are satisfied:* by the hypothesis that every
threshold in $R(G')$ is at least as strict as some corresponding threshold in $R(G)$ on
the same feature, satisfying $R(G')$'s threshold on a feature $f$ (a stricter bound)
logically implies satisfying $R(G)$'s threshold on the same feature (a looser bound) —
e.g. if $R(G)$ requires `calories` $\leq 150$ and $R(G')$ requires `calories` $\leq 55$,
then an observed value $\leq 55$ trivially implies $\leq 150$, since $55 < 150$. The
same feature being observed for the stricter check means it is observed for the looser
one too.

Combining (a)–(c): $o$ satisfies every condition Definition 4.6 requires for
$G$-admission, so $o$ is $G$-admitted. $\blacksquare$

**Worked instantiation (the running example's `G_3`/`G_4`).** $\Phi(G_2) = \emptyset
\subseteq \Phi(G_3) = \Phi(G_4)$ (note $\Phi(G_3) = \Phi(G_4)$ exactly — they place
identical equality constraints on `is_vegan`), and $R(G_3) = \emptyset \subseteq
R(G_4) = \{(\text{calories}, \leq, v)\}$ for whatever threshold $v$ the symbolic
walkthrough uses (the paper genericises this value specifically to avoid conflation
with the real experiment's separately-calibrated 55 kcal/100g threshold — see the note
at the end of this document). Theorem 4.1 applied to $G_3, G_4$: since $\Phi(G_3) =
\Phi(G_4)$ (trivially $\Phi(G_3) \subseteq \Phi(G_4)$ and vice versa), $D(G_3) = D(G_4)$
*exactly* — both equal $D_{\mathrm{rel}}(G_2) \setminus \{\text{DairyProduct},
\text{MeatProduct}\}$, i.e. 5 types (see Table 1 in the paper). No further type-level
shrinkage occurs between $G_3$ and $G_4$, precisely because their $\Phi$ components are
identical and only $R$ differs. Proposition 4.1 then gives the complementary,
instance-level result: of the 5 grocery-side, non-dairy/meat items in the 12-item
symbolic set, all 5 qualify for $G_3$-admission (since $R(G_3) = \emptyset$ imposes no
threshold at all); of those same 5, only the ones whose observed `calories` value is at
or below the chosen threshold $v$ remain $G_4$-admitted. This is exactly why $G_3$ and
$G_4$ share an identical *type-level* domain (hence identical `size(D(G))`, Corollary
4.1 below) while differing in which *specific shelf items* ultimately qualify — the
reduction from $G_3$ to $G_4$ happens purely at the instance level, never touching the
compiled domain's type/predicate structure at all. See `worked-example/README.md` in
this repository for the full, item-by-item computation with concrete numeric values.

---

## Theorem 5.1 (Monotone domain-size reduction)

**Statement.** For goals $G, G'$ with $D(G') \subseteq D(G)$ (guaranteed by Theorem 4.1
whenever they share a target supertype and `Φ(G) ⊆ Φ(G')`),
$\mathrm{size}(D(G')) \leq \mathrm{size}(D(G))$.

**Full proof.**

*Type-count term.* $D(G') \subseteq D(G)$ is the hypothesis directly; cardinality is
monotone under subset inclusion, so $|D(G')| \leq |D(G)|$ immediately.

*Predicate-count term.* By Definition 5.2, $\mathrm{pred}(D(G)) = \bigcup_{t \in D(G)}
\mathrm{feat}(t)$. Since $D(G') \subseteq D(G)$, the union defining
$\mathrm{pred}(D(G'))$ ranges over a subset of the index set that defines
$\mathrm{pred}(D(G))$:
```
pred(D(G')) = union over t in D(G') of feat(t)
            ⊆ union over t in D(G) of feat(t)
            = pred(D(G))
```
by the same "union over a subset index set is a subset of the union over the full
index set" fact used in Corollary 4.1′'s proof above. Hence $|\mathrm{pred}(D(G'))|
\leq |\mathrm{pred}(D(G))|$.

*Combine.* By Definition 5.3, $\mathrm{size}(D(G)) = |D(G)| + |\mathrm{pred}(D(G))|$.
Summing the two established inequalities term-by-term:
```
size(D(G')) = |D(G')| + |pred(D(G'))|
            ≤ |D(G)| + |pred(D(G))|
            = size(D(G))                    ∎
```

**Why this discharges Corollary 4.1 exactly, not asymptotically.** Corollary 4.1 (domain-
size reduction, stated informally in Section 4 of the paper before this compilation
machinery existed) claimed "increasing goal specificity never increases the size of the
compiled planning domain" — Theorem 5.1 makes this exact: the reduction in `size(D(G))`
is a direct arithmetic consequence of two independent monotone set-containments
(types, predicates), not an empirical tendency observed to hold in this particular
worked example. If a real implementation ever produced $\mathrm{size}(D(G')) >
\mathrm{size}(D(G))$ for goals satisfying the theorem's hypotheses, that would indicate
either (a) a bug in the compiler (Definitions 5.1–5.2 not correctly implemented), or (b)
the hypotheses weren't actually satisfied for the goals in question (e.g. different
target type sets) — never a genuine counterexample to the theorem itself, since the
proof leaves no room for one.

---

## A note on the "150" vs. "55" threshold value

The proofs above (and the worked example throughout this repository) use a concrete
placeholder value for $R(G_4)$'s calorie threshold. In the *paper's* symbolic
walkthrough this value is left as a generic $v$ specifically to avoid implying any
connection to the *real, photograph-grounded experiment's* independently-calibrated
threshold of 55 kcal/100g (calibrated post-hoc to the collected sample's calorie
distribution, as disclosed in the paper's Experimental Setup section). The two
thresholds are deliberately unrelated: the symbolic walkthrough's value only needs to
demonstrate the *mechanism* (type-level equality between `G_3`/`G_4`, instance-level
divergence), and any concrete value serves that purpose equally well. In this
repository's full worked example (`worked-example/README.md`), we use 150 kcal/100g as
the illustrative value, matching the earliest fully-worked version of the symbolic
12-item example, since it cleanly admits all 5 non-dairy/meat vegan items and thus
demonstrates Proposition 4.1's mechanism as originally intended without needing to
recompute which specific items pass a different cutoff.
