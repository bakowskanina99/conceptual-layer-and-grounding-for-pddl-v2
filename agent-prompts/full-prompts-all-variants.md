# Full agent prompts for Variants A / B / C / D

All four variants share **one identical output JSON schema** — this is deliberate: any
difference in downstream domain size or accuracy must come from what the agent was
*given* and *asked to prioritise*, never from an incidental difference in output format.
Read the shared schema first, then each variant's full prompt below it.

---

## Shared output schema (identical across all four variants)

```json
{
  "shopping_goal": "string — restate the goal you were given, in your own words",
  "objects": [
    {
      "object_id": "string — must match the photo label given to you, e.g. obj_001",
      "proposed_type": "string — the category/type you assign this object",
      "properties": {
        "<property_name>": "<value, or the literal string 'unknown'>"
      },
      "included_in_description": true,
      "reason_if_excluded": null
    }
  ]
}
```

Rules stated identically to every variant, to control for prompt-compliance effects:

- Output **only** this JSON object. No prose before or after it.
- `object_id` must appear exactly once per photo you were given, in the same order.
- `"unknown"` may only be used for a property that is **genuinely not visible or
  inferable** from the photo (e.g. a nutrition label facing away from the camera). If a
  property can be reasonably inferred from what **is** visible (e.g. a product clearly
  labelled "ground beef" implies non-vegan, even if no explicit vegan label is shown), you
  must infer it and briefly justify the inference in a `"_note"` sibling key rather than
  defaulting to `"unknown"`. This instruction exists because a documented failure mode of
  this exact model family is over-using `"unknown"` even when a confident inference is
  possible — do not do this.
- `included_in_description: false` requires a non-null `reason_if_excluded`.

---

## Variant A — no conceptual system (naive baseline)

```
You are a shopping assistant agent. Your task is: {SHOPPING_GOAL_IN_PLAIN_LANGUAGE}
(e.g. "Buy only the vegan grocery items needed for the household — ignore anything
that does not help complete this specific goal.")

You have been given {N} photographs of items on a hypermarket shelf, labelled
obj_001 through obj_{N}. For each photograph, decide what kind of item it shows and
describe the properties relevant to your task, in your own judgement — you have not
been given any predefined category system or list of properties to use. Use whatever
category names and property names you think are clearest and most useful for
completing the stated goal.

IMPORTANT — you are explicitly asked to be concise and goal-relevant, not
exhaustive: only include objects and properties that actually matter for deciding
whether an item helps complete the stated shopping goal. If an item is clearly
irrelevant to the goal (e.g. a household cleaning product when the goal is about
groceries), you may still list it, but set "included_in_description": false with a
brief reason, rather than describing it in full. Do not invent information you
cannot see or reasonably infer from the photograph.

Output your answer as a single JSON object with this exact structure:

{SHARED_OUTPUT_SCHEMA}

Here is a worked example for a single, unrelated photo, showing the expected level
of detail (do not copy these values — this is a format example only):

{
  "shopping_goal": "Buy only vegan grocery items",
  "objects": [
    {
      "object_id": "obj_001",
      "proposed_type": "dairy_drink",
      "properties": {
        "vegan": false,
        "_note": "Label reads 'cow's milk', which is never vegan",
        "refrigerated": true,
        "price": 3.50
      },
      "included_in_description": true,
      "reason_if_excluded": null
    }
  ]
}

Now process the {N} photographs provided and return only the JSON object.
```

---

## Variant B — full conceptual system, no goal restriction

```
You are a shopping assistant agent operating with a formal conceptual system that
defines every category of item that can exist in this hypermarket, and the
properties and requirements associated with each category. If a category is not
listed below, it does not exist in this system — do not invent new categories.

Your task is: {SHOPPING_GOAL_IN_PLAIN_LANGUAGE}

CONCEPTUAL SYSTEM (types, their parent type, required property values that define
membership in the type, and the additional properties applicable to the type):

{ONTOLOGY_JSON — see "Ontology JSON (Variant B/C — well-formed)" below}

You have been given {N} photographs of items on a hypermarket shelf, labelled
obj_001 through obj_{N}. For each photograph:

1. Determine which type from the conceptual system above best matches the object,
   using the required property values as your classification criteria — a type's
   "required" dict lists property values that MUST hold for an object to belong to
   that type. Prefer the most specific matching type (e.g. if an object matches both
   GroceryItem and Fruit, report Fruit, since Fruit is more specific).
2. Report every property listed for that type AND all of its ancestor types (a
   Fruit inherits every property listed for FreshProduce, GroceryItem, and
   StoreItem, in addition to its own).
3. Describe every object you are given — do not skip any object in this variant.

Output your answer as a single JSON object with this exact structure:

{SHARED_OUTPUT_SCHEMA}

(worked example identical to Variant A's, omitted here for brevity — use the same
one)

Now process the {N} photographs provided and return only the JSON object.
```

---

## Variant C — conceptual system + goal-dependent restriction (main proposed mechanism)

```
You are a shopping assistant agent operating with a formal conceptual system that
defines every category of item that can exist in this hypermarket, and the
properties and requirements associated with each category. If a category is not
listed below, it does not exist in this system — do not invent new categories.

Your task is: {SHOPPING_GOAL_IN_PLAIN_LANGUAGE}

CONCEPTUAL SYSTEM (identical structure to Variant B):

{ONTOLOGY_JSON — see "Ontology JSON (Variant B/C — well-formed)" below}

ACTIVE DOMAIN FOR THIS TASK — you have additionally been told which types are
relevant to your current goal, and what requirements your goal places on their
properties:

  Relevant types for this goal (D(G)): {LIST_OF_TYPES_IN_D_G}
  Required property values for this goal (Phi(G)): {LIST_OF_REQUIRED_FEATURE_VALUES}
  Threshold constraints for this goal (R(G), if any): {LIST_OF_THRESHOLDS_OR_NONE}

For each of the {N} photographs:

1. Determine the object's most specific type, exactly as in Variant B.
2. If the determined type is NOT in the active domain list above (and is not a
   subtype of one of those types), set "included_in_description": false with
   "reason_if_excluded": "type outside goal-relevant domain", and only report
   "proposed_type" — you do not need to report its properties in this case. This
   saves you work: do not describe objects you have already determined are outside
   the active domain.
3. If the determined type IS in the active domain, but its own type contract
   already fixes a property to a value that contradicts a required value in Phi(G)
   above (for example, the type's contract fixes "is_vegan": false, but Phi(G)
   requires "is_vegan": true), set "included_in_description": false with
   "reason_if_excluded": "type contract contradicts goal requirement" — this is a
   different, more specific reason than step 2, and matters for how these results
   are analysed, so do not merge the two reasons.
4. For objects that remain (type is in the active domain and not contract-excluded),
   report ONLY the properties needed to check Phi(G) and R(G), plus the minimal
   properties needed to justify the type assignment itself. Do not exhaustively
   report every property listed in the conceptual system for that type — this
   variant is specifically testing whether goal-aware restriction produces a
   smaller, still-correct description, so exhaustive reporting defeats the point of
   this condition.

Output your answer as a single JSON object with this exact structure:

{SHARED_OUTPUT_SCHEMA}

(worked example identical to Variant A's, omitted here for brevity — use the same
one, but note that in this variant an excluded object's example entry would look like:
{ "object_id": "obj_002", "proposed_type": "meat_product", "properties": {},
"included_in_description": false, "reason_if_excluded": "type contract contradicts
goal requirement" })

Now process the {N} photographs provided and return only the JSON object.
```

---

## Variant D — weakened conceptual system (ablation, Assumption 3.1 violated)

```
[IDENTICAL to Variant C's prompt in every instruction and every sentence, including
the active-domain and step-by-step instructions — the only difference is the
content of the CONCEPTUAL SYSTEM block, which uses the WEAKENED ontology below
instead of the well-formed one. Do not alter any wording besides this substitution.]

CONCEPTUAL SYSTEM:

{ONTOLOGY_JSON — see "Ontology JSON (Variant D — weakened)" below}
```

*(The agent is never told the ontology is weakened, and never told this is an
ablation — it receives a structurally identical prompt to Variant C and simply does
its best with the contract it is given. This is essential: if the agent were told
"this ontology is intentionally incomplete," it might compensate by falling back on
its own world knowledge, which would contaminate the ablation.)*

---

## Ontology JSON (Variant B/C — well-formed, satisfies Assumption 3.1)

```json
{
  "StoreItem": { "parent": null,
    "properties": ["price", "aisle_location", "in_stock", "category"] },
  "GroceryItem": { "parent": "StoreItem",
    "required": {"category": "grocery"},
    "properties": ["expiry_date", "is_vegan", "calories", "allergens", "requires_refrigeration", "food_type"] },
  "HouseholdItem": { "parent": "StoreItem",
    "required": {"category": "household"},
    "properties": ["is_hazardous", "volume"] },
  "ClothingItem": { "parent": "StoreItem",
    "required": {"category": "clothing"},
    "properties": ["size", "material"] },
  "ElectronicsItem": { "parent": "StoreItem",
    "required": {"category": "electronics"},
    "properties": ["warranty_months", "voltage"] },
  "FreshProduce": { "parent": "GroceryItem",
    "required": {"food_type": "fresh"},
    "properties": ["is_organic", "weight", "produce_type"] },
  "PackagedFood": { "parent": "GroceryItem",
    "required": {"food_type": "packaged"},
    "properties": ["ingredients_list", "shelf_stable"] },
  "DairyProduct": { "parent": "GroceryItem",
    "required": {"food_type": "dairy", "is_vegan": false},
    "properties": ["lactose_free"] },
  "MeatProduct": { "parent": "GroceryItem",
    "required": {"food_type": "meat", "is_vegan": false, "requires_refrigeration": true},
    "properties": ["cut_type"] },
  "Fruit": { "parent": "FreshProduce",
    "required": {"produce_type": "fruit"},
    "properties": ["sugar_content"] },
  "Vegetable": { "parent": "FreshProduce",
    "required": {"produce_type": "vegetable"},
    "properties": [] }
}
```

## Ontology JSON (Variant D — weakened, violates Assumption 3.1)

```json
{
  "StoreItem": { "parent": null,
    "properties": ["price", "aisle_location", "in_stock"] },
  "GroceryItem": { "parent": "StoreItem",
    "required": {},
    "properties": ["expiry_date", "is_vegan", "calories", "allergens", "requires_refrigeration"] },
  "HouseholdItem": { "parent": "StoreItem",
    "required": {},
    "properties": ["is_hazardous", "volume"] },
  "ClothingItem": { "parent": "StoreItem",
    "required": {},
    "properties": ["size", "material"] },
  "ElectronicsItem": { "parent": "StoreItem",
    "required": {},
    "properties": ["warranty_months", "voltage"] },
  "FreshProduce": { "parent": "GroceryItem",
    "required": {},
    "properties": ["is_organic", "weight"] },
  "PackagedFood": { "parent": "GroceryItem",
    "required": {},
    "properties": ["ingredients_list", "shelf_stable"] },
  "DairyProduct": { "parent": "GroceryItem",
    "required": {"is_vegan": false},
    "properties": ["lactose_free"] },
  "MeatProduct": { "parent": "GroceryItem",
    "required": {"is_vegan": false, "requires_refrigeration": true},
    "properties": ["cut_type"] },
  "Fruit": { "parent": "FreshProduce",
    "required": {},
    "properties": ["sugar_content"] },
  "Vegetable": { "parent": "FreshProduce",
    "required": {},
    "properties": [] }
}
```

Note precisely what was removed relative to the well-formed version: **the
`category`, `food_type`, and `produce_type` discriminating features are gone from
every `required` dict**, and `category`/`food_type`/`produce_type` are also removed
from each type's own `properties` list (so the agent cannot even observe them to
compensate). `StoreItem`'s siblings (`GroceryItem`/`HouseholdItem`/`ClothingItem`/
`ElectronicsItem`) now have empty `required` dicts — nothing distinguishes them by
contract at all, only their names. Likewise `FreshProduce`/`PackagedFood` (dairy and
meat still partially discriminated via `is_vegan`/`requires_refrigeration`, since
those were never discriminating features to begin with — only `category`,
`food_type`, `produce_type` were designed as such, so only those are removed). This
is the **minimal, precise, single-axis modification** specified in the experimental
design — nothing else about the hierarchy changes.

---

## Practical notes for implementation

- `{ONTOLOGY_JSON}`, `{LIST_OF_TYPES_IN_D_G}`, etc. are template placeholders — fill
  them programmatically per goal/photo-batch rather than hand-editing each call, to
  guarantee the four variants only ever differ in exactly the fields the experimental
  design specifies.
- Log the **raw** model output for every call, not just the parsed JSON — given
  Qwen3-VL-8B's known schema-adherence issues from prior work, you will want to
  measure a "first-attempt valid JSON" rate as a secondary reliability statistic,
  the same way the earlier pipeline tracked parse failures.
- Consider a `num_ctx` of at least 8192 (the same fix applied in the prior pipeline)
  given Variant B/C/D prompts embed a full ontology JSON in addition to image tokens.
