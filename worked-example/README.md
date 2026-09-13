# The Hypermarket Worked Example — Full Walkthrough

This is the complete, unabridged version of the symbolic worked example that appears
throughout Sections 3–6 of the paper in illustrative fragments. Everything here is
self-contained: the full type hierarchy with every contract, all 12 observed items, the
full computation for every goal (G1–G4), and the actual machine-readable artifacts
(OWL ontology, SHACL shapes, compiled PDDL) that realize it. If you only read one file
in this repository to understand how the formal mechanism actually behaves on concrete
data, read this one.

## 1. Why this example, and what it is for

The paper's formal results (Sections 3–5) are general — they hold for any well-formed
conceptual system and any goal satisfying Definition 4.1's constraint-language scope.
This example exists to make the formalism *legible*: a single, small-enough-to-hold-in-
your-head hierarchy on which every definition, theorem, and remark in the paper can be
checked by hand. It is not the paper's empirical evaluation (that uses 32 real
photographs — see `../results/` and `../experiment-data/`) — it is a symbolic,
hand-constructed illustration, used purely to demonstrate the mechanism cleanly before
any perceptual uncertainty is introduced.

Two mechanisms need a witness each, and this example is deliberately built to supply
both in one hierarchy:
- **Relevance-driven exclusion** (Definition 4.2): non-grocery types (`HouseholdItem`,
  `ClothingItem`, `ElectronicsItem`) are excluded from grocery-goal domains regardless
  of any constraint, simply because they are not comparable under `≤_T` to the target
  type.
- **Admissibility-driven exclusion** (Definition 4.4): `DairyProduct` and `MeatProduct`
  are excluded from vegan-goal domains *despite* being squarely inside the grocery
  branch, because their own type contracts fix `is_vegan = false`, directly
  contradicting a vegan goal's requirement.

Lemma 4.1's whole point — that these are two logically independent reasons a type can
be missing from $D(G)$ — is witnessed concretely by exactly these two pairs of types in
this one hierarchy. See `../formal-proofs/full-proofs.md` for the formal proof using
these same witnesses.

## 2. The conceptual system: full type hierarchy with contracts

```
StoreItem                         (price, aisle_location, in_stock, category)
├── GroceryItem                   K+: {category=grocery}
│   │                             (+ expiry_date, is_vegan, calories, allergens,
│   │                              requires_refrigeration, food_type)
│   ├── FreshProduce              K+: {category=grocery, food_type=fresh}
│   │   │                         (+ is_organic, weight, produce_type)
│   │   ├── Fruit                 K+: {..., produce_type=fruit}  (+ sugar_content)
│   │   └── Vegetable             K+: {..., produce_type=vegetable}
│   ├── PackagedFood              K+: {category=grocery, food_type=packaged}
│   │                             (+ ingredients_list, shelf_stable)
│   ├── DairyProduct              K+: {category=grocery, food_type=dairy,
│   │                                  is_vegan=false}         (+ lactose_free)
│   └── MeatProduct               K+: {category=grocery, food_type=meat,
│                                       is_vegan=false,
│                                       requires_refrigeration=true} (+ cut_type)
├── HouseholdItem                 K+: {category=household}  (+ is_hazardous, volume)
├── ClothingItem                  K+: {category=clothing}   (+ size, material)
└── ElectronicsItem               K+: {category=electronics} (+ warranty_months, voltage)
```

**Total: 11 types.** Every sibling group has an explicit discriminating feature
(`category` at the top level, `food_type` among `GroceryItem`'s children, `produce_type`
between `Fruit`/`Vegetable`) — this is Assumption 3.1 (sibling discriminability),
satisfied by construction, not by accident. See `ontology/well_formed.ttl` for the
executable OWL 2 DL realisation of this hierarchy, including the `owl:disjointWith`
axioms that give Assumption 3.1 a second, machine-checkable enforcement mechanism
(Section 6.1 of the paper).

**Total feature count: 24**, cumulative along `≤_T` (Property 3.1): `GroceryItem`
inherits `StoreItem`'s 4 features and adds 6 of its own (10 total); `FreshProduce` adds
3 more (13); `Fruit` adds 1 more (14); `PackagedFood` adds 2 (12 at that branch);
`DairyProduct`/`MeatProduct` add 1 each; `HouseholdItem`/`ClothingItem`/`ElectronicsItem`
add 2 each. This cumulative structure is why Section 5.3's observation holds
(predicate count shrinks proportionally *less* than type count as the goal narrows —
features near the root are "already paid for").

## 3. The 12 observed items (Occurrences)

| # | Name | Type (grounded) | is_vegan | calories | requires_refrig. | price |
|---|---|---|---|---|---|---|
| 1 | Apple | Fruit | true | 52 | false | 0.50 |
| 2 | Carrot | Vegetable | true | 41 | false | 0.30 |
| 3 | Cow milk | DairyProduct | **false** (K⁺) | 42 | true | 3.50 |
| 4 | Oat drink | PackagedFood | true | 45 | true | 4.20 |
| 5 | Sliced ham | MeatProduct | **false** (K⁺) | 145 | true | 8.90 |
| 6 | Canned beans | PackagedFood | true | 127 | false | 2.10 |
| 7 | Protein bar | PackagedFood | **false** (observed) | 210 | false | 5.50 |
| 8 | Dish soap | HouseholdItem | n/a | n/a | n/a | 6.00 |
| 9 | Cotton T-shirt | ClothingItem | n/a | n/a | n/a | 25.00 |
| 10 | Phone charger | ElectronicsItem | n/a | n/a | n/a | 15.00 |
| 11 | Granola bar (worn label) | PackagedFood | **unknown** | **unknown** | false | 3.00 |
| 12 | Tofu | PackagedFood | true | 76 | true | 3.80 |

Three items are deliberately special, each demonstrating a different formal mechanism:

- **#3 and #5** have `is_vegan = false` *entailed by their own type's contract*
  (`K⁺(DairyProduct)`/`K⁺(MeatProduct)`), not merely observed — this is what makes
  their exclusion from vegan goals an *admissibility* failure (Definition 4.4), not
  just an observed-value mismatch. Full ontological derivation: see
  `ontology/well_formed.ttl`, classes `DairyProduct`/`MeatProduct`.
- **#7** has `is_vegan = false` as a genuinely *observed* fact (whey protein), not an
  entailed one — its type (`PackagedFood`) places no fixed value on `is_vegan` at all,
  so this exclusion happens at the *instance* level (Definition 4.6), not the type
  level. This is the concrete pairing that distinguishes "type contract conflicts with
  goal" from "this particular observed value happens to conflict with the goal" —
  two different rows in Definition 4.6's admitted/excluded/pending trichotomy.
- **#11** has `is_vegan` and `calories` genuinely *unobserved* (open-world, Definition
  3.2) — not false, not zero, simply unknown (the label was rubbed off). This is the
  item that demonstrates the `G`-pending case of Definition 4.6: for any goal
  constraining `is_vegan` or `calories`, #11 is neither admitted nor excluded, but
  pending, and the correct system response is to request the missing observation, not
  silently drop the item.

Full RDF/Turtle assertions for all 12 items: see `occurrences/twelve-items.ttl`. Note
that each individual is asserted only as `StoreItem` plus its observed properties —
never with its specific type pre-assigned — so that the OWL reasoner (HermiT) derives
the grounded type independently, exactly per Definition 3.6 ("grounding is computed,
not given").

## 4. The four goals, and the full per-goal computation

| Goal | $T_G$ | $\Phi(G)$ | $R(G)$ | $D(G)$ (types) | $\|D(G)\|$ | pred count | size |
|---|---|---|---|---|---|---|---|
| $G_1$ | {StoreItem} | ∅ | ∅ | all 11 types | 11 | 24 | 35 |
| $G_2$ | {GroceryItem} | ∅ | ∅ | 7 grocery-side types | 7 | 18 | 25 |
| $G_3$ | {GroceryItem} | {is_vegan=true} | ∅ | 5 types (excl. Dairy/Meat) | 5 | 16 | 21 |
| $G_4$ | {GroceryItem} | {is_vegan=true} | {calories≤150} | 5 types (same as $G_3$) | 5 | 16 | 21 |

This table is Table 1 in the paper, reproduced here with the full derivation below.

### $G_1 \to G_2$: pure relevance reduction

$D_{\mathrm{rel}}(G_2) = \{t \in T : t \leq_T \text{GroceryItem}\}$ = `GroceryItem`,
`FreshProduce`, `Fruit`, `Vegetable`, `PackagedFood`, `DairyProduct`, `MeatProduct` — 7
types. `HouseholdItem`/`ClothingItem`/`ElectronicsItem` are excluded because they are
not $\leq_T$-comparable to `GroceryItem` (Lemma 4.1's witness (i)). $\Phi(G_2) =
\emptyset$, so $D_{\mathrm{adm}}(G_2) = D_{\mathrm{rel}}(G_2)$ exactly — admissibility
filtering has nothing to check yet. **Instance level**: items #1–#7, #11, #12 (9 of 12)
qualify by type; #8–#10 are excluded as irrelevant.

Predicate count: `GroceryItem`'s cumulative 10 + `FreshProduce`'s 3 + `Fruit`'s 1 +
`Vegetable`'s 0 + `PackagedFood`'s 2 + `DairyProduct`'s 1 + `MeatProduct`'s 1 = 18.
$\mathrm{size}(D(G_2)) = 7 + 18 = 25$ — a 29% reduction from $G_1$'s 35.

### $G_2 \to G_3$: admissibility reduction added

$\Phi(G_3) = \{v_f = \mathsf{true}\}$ where $v_f$ is `is_vegan`. Checking Definition 4.3
against each of $G_2$'s 7 types: `DairyProduct`'s contract fixes `is_vegan = false`,
which conflicts directly ($\mathsf{true} \neq \mathsf{false}$ on the same feature) —
excluded. Same for `MeatProduct`. The remaining 5 types (`GroceryItem`, `FreshProduce`,
`Fruit`, `Vegetable`, `PackagedFood`) have no fixed value on `is_vegan` in their own
contracts, so no conflict — all 5 remain admissible. $D(G_3) = D_{\mathrm{rel}}(G_2)
\setminus \{\text{DairyProduct}, \text{MeatProduct}\}$, 5 types.

**Instance level**: of the 9 grocery-side items, #3 (Dairy) and #5 (Meat) are excluded
by *type* (their grounded type itself is outside `D(G_3)`) — this is different from
#7's exclusion, below. #7 (`PackagedFood`, observed `is_vegan=false`) is excluded at the
*instance* level: its type is in $D(G_3)$, but its own observed value violates
$\Phi(G_3)$. #11 (`PackagedFood`, `is_vegan` unobserved) is *pending*: its type is in
$D(G_3)$, no violation is observed, but the required feature is unobserved. The
remaining 5 (#1, #2, #4, #6, #12) are admitted. Total: **5 admitted, 2 type-excluded, 1
instance-excluded, 1 pending** — exactly 9 accounted for.

Predicate count: 10 (`GroceryItem`) + 3 (`FreshProduce`) + 1 (`Fruit`) + 0 (`Vegetable`)
+ 2 (`PackagedFood`) = 16. $\mathrm{size}(D(G_3)) = 5 + 16 = 21$ — a 40% reduction from
$G_1$, a further ~16% reduction from $G_2$.

### $G_3 \to G_4$: same types, different instances

$\Phi(G_4) = \Phi(G_3)$ exactly (both require `is_vegan` = true); only $R(G_4)$ adds
a constraint `calories` $\leq 150$, and $R(G_3) = \emptyset$. Since
Definition 4.3 (type-level admissibility) checks only $\Phi(G)$ against $K(t)$, never
$R(G)$ (see the paper's Remark on Definition 4.3's scope — no type in this hierarchy
fixes a numeric feature to a constant value, so no type-level conflict with $R(G)$ can
ever arise here), $D(G_4) = D(G_3)$ *exactly* — same 5 types, same predicate count,
same `size = 21`. This is not a coincidence to be surprised by — it is Theorem 4.1
applied with $T_G$ fixed and $\Phi$ unchanged between $G_3$ and $G_4$, so no further
type-level shrinkage is predicted, and none occurs.

**Instance level**: of $G_3$'s 5 admitted items (#1, #2, #4, #6, #12), check
`calories ≤ 150` for each: #1=52 ✓, #2=41 ✓, #4=45 ✓, #6=127 ✓, #12=76 ✓ — **all 5 pass**.
So $G_4$ admits the same 5 items as $G_3$; the only structural difference is that #11
(pending under $G_3$ due to unobserved `is_vegan`) is now pending on *two* grounds under
$G_4$ (unobserved `is_vegan` *and* unobserved `calories`) rather than one — still
pending either way, not excluded, since Definition 4.6's pending case doesn't
distinguish "pending on one unobserved feature" from "pending on several."

This is Proposition 4.1's complementary, instance-level result to Theorem 4.1's
type-level one: two goals can share an identical compiled domain while differing in
which concrete items ultimately qualify — the reduction from $G_3$ to $G_4$ is real, but
it happens entirely below the level Theorem 5.1 measures (`size(D(G))`), which is
exactly the empirical pattern the real photographic experiment reproduces at a larger
scale (see `../results/`).

## 5. From this table to compiled PDDL

`pddl/domain_G1.pddl` and `pddl/domain_G3.pddl` show the actual compiled `:types` and
`:predicates` blocks for the two extremes of this table (11 types/24 predicates vs. 5
types/16 predicates), built directly from Definitions 5.1–5.2. `pddl/problem_G3.pddl`
shows the compiled `:init` block for $G_3$, populated only with the 5 admitted items
(#1, #2, #4, #6, #12) plus item #11 in its pending state (properties partially
asserted, matching Definition 5.4) — #3, #5 (type-excluded) and #7 (instance-excluded)
never appear in the compiled problem at all, and #8–#10 (relevance-excluded) never
entered the picture from $G_2$ onward.

## 6. Machine-readable artifacts in this folder

| File | Content |
|---|---|
| `ontology/well_formed.ttl` | Full OWL 2 DL ontology: all 11 classes, all contracts as `owl:equivalentClass` restrictions, `owl:disjointWith` axioms enforcing Assumption 3.1 |
| `ontology/weakened.ttl` | The deliberately weakened ontology used for the paper's Variant D ablation (discriminating features and, for most sibling groups, disjointness axioms removed) — see `../results/variant-D-ablation-full-results.md` for what this produces empirically |
| `shacl/symbolic-shapes.ttl` | SHACL shapes for `G_3`/`G_4` as used in this symbolic walkthrough |
| `shacl/real-data-shapes.ttl` | SHACL shapes for the real experiment's goals (`G2_real`–`G4_real`), operating on Open Food Facts' native `veganAttributeMatch`/`calories` fields rather than this symbolic example's simplified `is_vegan` boolean |
| `occurrences/twelve-items.ttl` | RDF assertions for all 12 items, as described in Section 3 above |
| `pddl/domain_G1.pddl`, `pddl/domain_G3.pddl` | Compiled PDDL domains for the two size extremes in the table above |
| `pddl/problem_G3.pddl` | Compiled PDDL problem for $G_3$, with a worked Fast Downward plan |

All Turtle files validate against the OWL 2 DL profile (checked with HermiT) and the
SHACL files validate against the pySHACL reference implementation; see
`../pipeline/README.md` for how to run these checks yourself.
