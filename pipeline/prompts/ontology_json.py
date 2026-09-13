"""Ontology JSON payloads, verbatim from agent_prompts_ABCD.md ("Ontology
JSON (Variant B/C -- well-formed)" and "Ontology JSON (Variant D -- weakened)").
Kept as raw JSON TEXT (not a Python dict re-serialized) so the exact
formatting given in the spec is what gets embedded in the prompt, byte for
byte -- no risk of key-ordering or whitespace drift from round-tripping
through json.dumps.

NOT extended with veganAttributeMatch/nutriscoreMatch --
the real-data goals were resolved without touching the agent-facing ontology
at all (Option 3), so these payloads are unchanged from the original spec.
"""

WELL_FORMED_ONTOLOGY_JSON = """{
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
}"""

WEAKENED_ONTOLOGY_JSON = """{
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
}"""
