## Part A3 — Additional properties and real-data goal specification (photographic experiment)

The symbolic 12-item walkthrough (Parts C–E below) uses a simplified Boolean `isVegan`
for pedagogical clarity. The **real photographic experiment** interfaces directly with
Open Food Facts' native Product Attribute representation instead — richer, and not
Boolean-valued. Two additional properties, used only for the real-data goals below (not
by the symbolic walkthrough):

```turtle
store:veganAttributeMatch  a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ; rdfs:range xsd:integer .
store:nutriscoreMatch      a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ; rdfs:range xsd:integer .
# In Open Food Facts itself, both are populated directly from the
# attribute_groups_en response: attribute.match (0-100), only when
# attribute.status == "known" (status == "unknown" => left unasserted,
# open-world "pending", Definition 3.2, never coerced to 0). This describes
# how the REFERENCE labels (reference_labels.json) were sourced.
#
# IMPLEMENTATION NOTE (agent-driven pipeline, locked decision): the agent is
# never asked to report veganAttributeMatch directly -- it is not exposed in
# the agent-facing ontology JSON (agent_prompts_ABCD.md), because an 8B VLM
# cannot plausibly estimate an OFF-internal ingredient-database match score
# from a photograph. Instead, Compiler-F SYNTHESISES veganAttributeMatch from
# the agent's own (already-requested) `is_vegan` property, after Stage 0
# coercion: is_vegan == true -> veganAttributeMatch = 100; is_vegan == false
# -> veganAttributeMatch = 0; is_vegan unknown/unparsable -> veganAttributeMatch
# left unasserted (pending, per Definition 3.2 -- never coerced to a default).
# This keeps G3RealGoalShape/G4RealGoalShape's veganAttributeMatch check
# operating on a value derived from the agent's own observation, not a
# ground-truth lookup, preserving the experiment's validity (Variant
# differences must come from what the agent produced). See
# compiler_pipeline_spec.md, Stage 1, for the exact synthesis step and its
# required per-object logging.
```

Real-data goal specification (Section 4's $T_G$/$\Phi(G)$/$R(G)$, instantiated against
OFF fields, replacing the illustrative $G_1$–$G_4$ for the empirical study):

| Goal | $T_G$ | $\Phi(G)$ | $R(G)$ |
|---|---|---|---|
| $G_1^{\text{real}}$ | $\{\text{StoreItem}\}$ | $\emptyset$ | $\emptyset$ |
| $G_2^{\text{real}}$ | $\{\text{GroceryItem}\}$ | $\emptyset$ | $\emptyset$ |
| $G_3^{\text{real}}$ | $\{\text{GroceryItem}\}$ | $\{(\text{veganAttributeMatch}, 100)\}$ | $\emptyset$ |
| $G_4^{\text{real}}$ | $\{\text{GroceryItem}\}$ | same as $G_3^{\text{real}}$ | $\{(\text{calories}, \leq, 55)\}$ |

The threshold 55 kcal/100g was chosen after inspecting the real sample's calorie
distribution among vegan grocery items (52-70 kcal/100g range), specifically so that
$G_3$ and $G_4$ diverge at the instance level in this dataset — at the illustrative
symbolic-example threshold of 150, every vegan item in the real sample would pass,
making $G_3$ and $G_4$ empirically indistinguishable. The constraint is placed on
`calories` directly (not `nutriscoreMatch`) because `nutriscoreMatch` is an
OFF-internal score computed from a full ingredients-database lookup — not a property a
vision-language model looking at a photograph could plausibly estimate — whereas
`calories` is exactly $R(G_4)$ as already proven in Section 5, and is the property
agents are actually asked to report.

---

