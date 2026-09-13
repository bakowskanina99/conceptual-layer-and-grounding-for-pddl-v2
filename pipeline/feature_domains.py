"""Feature domain table (Definition 3.1: boolean / numeric / categorical),
derived from the well-formed OWL ontology's rdfs:range declarations
(formal_artifacts_owl_pddl_v2.md, Part A/A3). Single source of truth for
Stage 0 coercion (compiler_pipeline_spec.md).

Keys are snake_case, matching both the agent-facing ontology JSON
(agent_prompts_ABCD.md) and the shared output schema's property names.
xsd:string / xsd:dateTime map to "categorical" -- Definition 3.1 has no
separate "date" primitive, and expiry_date is not used by any goal or shape in
this experiment, so treating it as an opaque string loses nothing.
"""

FEATURE_DOMAINS = {
    "price": "numeric",
    "aisle_location": "categorical",
    "in_stock": "boolean",
    "category": "categorical",
    "expiry_date": "categorical",
    "is_vegan": "boolean",
    "calories": "numeric",
    "allergens": "categorical",
    "requires_refrigeration": "boolean",
    "food_type": "categorical",
    "is_organic": "boolean",
    "weight": "numeric",
    "produce_type": "categorical",
    "sugar_content": "numeric",
    "ingredients_list": "categorical",
    "shelf_stable": "boolean",
    "lactose_free": "boolean",
    "cut_type": "categorical",
    "is_hazardous": "boolean",
    "volume": "numeric",
    "size": "categorical",
    "material": "categorical",
    "warranty_months": "numeric",
    "voltage": "numeric",
    # Compiler-synthesized only -- never agent-reported.
    "vegan_attribute_match": "numeric",
    # Reference/metadata only -- never agent-reported, never
    # asserted into any individual. Included so an accidental agent mention
    # of it doesn't fall through to the "unseen -> categorical" default.
    "nutriscore_match": "numeric",
}
