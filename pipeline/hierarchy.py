"""Type hierarchy (T, feat, parent, K+) -- Definition 3.5 -- mirrored from
agent_prompts_ABCD.md's "Ontology JSON (Variant B/C -- well-formed)" so the
SAME structure the agent is shown is what the compiler compiles against
(Definitions 4.1-5.4 operate on the conceptual system, not a separately
invented copy of it).

`own_features`: exactly what agent_prompts_ABCD.md's JSON lists under
"properties" for that type (feat(t) minus feat(parent(t)) -- Property 3.1's
cumulative inheritance is computed by `feat()` below, not stored redundantly).

`required`: K+(t) restricted to the values Part A's OWL equivalentClass
restrictions literally fix (Definition 3.3) -- deliberately does NOT include
`vegan_attribute_match` for DairyProduct/MeatProduct even though it would
restore type-level exclusion for G3_real/G4_real: doing so would also change
the symbolic 12-item walkthrough's item_003/item_005 grounding (Part C),
silently invalidating the already-verified Theorem 5.1 figures (11->7->5
types).

`vegan_attribute_match` is added to GroceryItem's own_features (Part A3) but
NOT to any `required` dict -- it is compiler-synthesized per-instance
(vegan_attribute_match.py), never a type-level fixed value.
"""

from __future__ import annotations

WELL_FORMED_HIERARCHY = {
    "StoreItem": {
        "parent": None,
        "own_features": ["price", "aisle_location", "in_stock", "category"],
        "required": {},
    },
    "GroceryItem": {
        "parent": "StoreItem",
        "own_features": [
            "expiry_date", "is_vegan", "calories", "allergens", "requires_refrigeration", "food_type",
            "vegan_attribute_match",  # Part A3 real-data addition
        ],
        "required": {"category": "grocery"},
    },
    "HouseholdItem": {
        "parent": "StoreItem",
        "own_features": ["is_hazardous", "volume"],
        "required": {"category": "household"},
    },
    "ClothingItem": {
        "parent": "StoreItem",
        "own_features": ["size", "material"],
        "required": {"category": "clothing"},
    },
    "ElectronicsItem": {
        "parent": "StoreItem",
        "own_features": ["warranty_months", "voltage"],
        "required": {"category": "electronics"},
    },
    "FreshProduce": {
        "parent": "GroceryItem",
        "own_features": ["is_organic", "weight", "produce_type"],
        "required": {"food_type": "fresh"},
    },
    "PackagedFood": {
        "parent": "GroceryItem",
        "own_features": ["ingredients_list", "shelf_stable"],
        "required": {"food_type": "packaged"},
    },
    "DairyProduct": {
        "parent": "GroceryItem",
        "own_features": ["lactose_free"],
        "required": {"food_type": "dairy", "is_vegan": False},
    },
    "MeatProduct": {
        "parent": "GroceryItem",
        "own_features": ["cut_type"],
        "required": {"food_type": "meat", "is_vegan": False, "requires_refrigeration": True},
    },
    "Fruit": {
        "parent": "FreshProduce",
        "own_features": ["sugar_content"],
        "required": {"produce_type": "fruit"},
    },
    "Vegetable": {
        "parent": "FreshProduce",
        "own_features": [],
        "required": {"produce_type": "vegetable"},
    },
}


WEAKENED_HIERARCHY = {
    # Mirrors agent_prompts_ABCD.md's "Ontology JSON (Variant D -- weakened)"
    # exactly: category/food_type/produce_type removed from BOTH own_features
    # (the agent cannot even observe them) and required (no longer
    # discriminating). DairyProduct/MeatProduct keep isVegan/
    # requiresRefrigeration -- never the discriminating features under test.
    "StoreItem": {"parent": None, "own_features": ["price", "aisle_location", "in_stock"], "required": {}},
    "GroceryItem": {
        "parent": "StoreItem",
        "own_features": ["expiry_date", "is_vegan", "calories", "allergens", "requires_refrigeration",
                          "vegan_attribute_match"],
        "required": {},
    },
    "HouseholdItem": {"parent": "StoreItem", "own_features": ["is_hazardous", "volume"], "required": {}},
    "ClothingItem": {"parent": "StoreItem", "own_features": ["size", "material"], "required": {}},
    "ElectronicsItem": {"parent": "StoreItem", "own_features": ["warranty_months", "voltage"], "required": {}},
    "FreshProduce": {"parent": "GroceryItem", "own_features": ["is_organic", "weight"], "required": {}},
    "PackagedFood": {"parent": "GroceryItem", "own_features": ["ingredients_list", "shelf_stable"], "required": {}},
    "DairyProduct": {"parent": "GroceryItem", "own_features": ["lactose_free"], "required": {"is_vegan": False}},
    "MeatProduct": {
        "parent": "GroceryItem",
        "own_features": ["cut_type"],
        "required": {"is_vegan": False, "requires_refrigeration": True},
    },
    "Fruit": {"parent": "FreshProduce", "own_features": ["sugar_content"], "required": {}},
    "Vegetable": {"parent": "FreshProduce", "own_features": [], "required": {}},
}


def feat(hierarchy: dict, type_name: str) -> list[str]:
    """Cumulative feature set (Property 3.1): feat(t) includes feat(parent(t)),
    each feature listed once at its shallowest point of introduction."""
    result = []
    seen = set()
    t = type_name
    while t is not None:
        for f in hierarchy[t]["own_features"]:
            if f not in seen:
                result.append(f)
                seen.add(f)
        t = hierarchy[t]["parent"]
    return result


def required_cumulative(hierarchy: dict, type_name: str) -> dict:
    """K+(t) (Definition 3.3), cumulative per Property 3.2: K+(t) is a
    superset of K+(parent(t)). A child's own requirement wins if it somehow
    named the same feature as an ancestor (not the case in this hierarchy,
    but defined defensively)."""
    result = {}
    chain = ancestors_inclusive(hierarchy, type_name)
    for t in reversed(chain):  # root first, so a more specific type's own requirement can override
        result.update(hierarchy[t]["required"])
    return result


def ancestors_inclusive(hierarchy: dict, type_name: str) -> list[str]:
    """[type_name, parent, grandparent, ..., root]."""
    result = []
    t = type_name
    while t is not None:
        result.append(t)
        t = hierarchy[t]["parent"]
    return result


def descendants_inclusive(hierarchy: dict, type_name: str) -> set[str]:
    """{t in T : t <=_T type_name} -- the down-set used by Definition 4.2."""
    return {t for t in hierarchy if type_name in ancestors_inclusive(hierarchy, t)}


def parent_within(hierarchy: dict, type_name: str, allowed_types: set[str]) -> str | None:
    """The immediate <=_T-predecessor of type_name, restricted to
    allowed_types (Definition 5.1) -- None if the parent is outside
    allowed_types (type_name is then a root of the compiled hierarchy)."""
    parent = hierarchy[type_name]["parent"]
    return parent if parent in allowed_types else None
