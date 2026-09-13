## Part C — RDF Individuals (Occurrences layer, Section 3.4 / 6.1)

Types are deliberately **not** asserted here beyond the universal `store:StoreItem` —
the specific subtype for each item is left for the OWL reasoner to infer from the
property assertions via the `owl:equivalentClass` axioms in Part A, exactly as
Definition 3.6 requires (grounding is computed, not given). Item `item_011` omits
`isVegan` and `calories` entirely, per Definition 3.2 (absence = unobserved, not false).

```turtle
@prefix store: <http://example.org/store#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

store:item_001 a store:StoreItem ;                       # → reasoner infers: Fruit
    store:category "grocery" ; store:foodType "fresh" ; store:produceType "fruit" ;
    store:price "0.50"^^xsd:float ; store:aisleLocation "Produce" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "true"^^xsd:boolean ; store:calories "52"^^xsd:integer ;
    store:isOrganic "true"^^xsd:boolean ; store:weight "0.15"^^xsd:float ; store:sugarContent "10.0"^^xsd:float .

store:item_002 a store:StoreItem ;                       # → Vegetable
    store:category "grocery" ; store:foodType "fresh" ; store:produceType "vegetable" ;
    store:price "0.30"^^xsd:float ; store:aisleLocation "Produce" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "true"^^xsd:boolean ; store:calories "41"^^xsd:integer ;
    store:isOrganic "false"^^xsd:boolean ; store:weight "0.10"^^xsd:float .

store:item_003 a store:StoreItem ;                       # → DairyProduct (isVegan entailed false)
    store:category "grocery" ; store:foodType "dairy" ;
    store:price "3.50"^^xsd:float ; store:aisleLocation "Dairy" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "false"^^xsd:boolean ; store:calories "42"^^xsd:integer ;
    store:requiresRefrigeration "true"^^xsd:boolean ; store:lactoseFree "false"^^xsd:boolean .

store:item_004 a store:StoreItem ;                       # → PackagedFood
    store:category "grocery" ; store:foodType "packaged" ;
    store:price "4.20"^^xsd:float ; store:aisleLocation "Dairy-alt" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "true"^^xsd:boolean ; store:calories "45"^^xsd:integer ;
    store:requiresRefrigeration "true"^^xsd:boolean ;
    store:ingredientsList "oats,water" ; store:shelfStable "false"^^xsd:boolean .

store:item_005 a store:StoreItem ;                       # → MeatProduct
    store:category "grocery" ; store:foodType "meat" ;
    store:price "8.90"^^xsd:float ; store:aisleLocation "Deli" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "false"^^xsd:boolean ; store:calories "145"^^xsd:integer ;
    store:requiresRefrigeration "true"^^xsd:boolean ; store:cutType "sliced" .

store:item_006 a store:StoreItem ;                       # → PackagedFood
    store:category "grocery" ; store:foodType "packaged" ;
    store:price "2.10"^^xsd:float ; store:aisleLocation "Canned" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "true"^^xsd:boolean ; store:calories "127"^^xsd:integer ;
    store:requiresRefrigeration "false"^^xsd:boolean ;
    store:ingredientsList "beans,water,salt" ; store:shelfStable "true"^^xsd:boolean .

store:item_007 a store:StoreItem ;                       # → PackagedFood (instance-excluded from G3/G4)
    store:category "grocery" ; store:foodType "packaged" ;
    store:price "5.50"^^xsd:float ; store:aisleLocation "Snacks" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "false"^^xsd:boolean ; store:calories "210"^^xsd:integer ;
    store:requiresRefrigeration "false"^^xsd:boolean ;
    store:ingredientsList "oats,whey-protein,cocoa" ; store:shelfStable "true"^^xsd:boolean .

store:item_008 a store:StoreItem ;                       # → HouseholdItem
    store:category "household" ;
    store:price "6.00"^^xsd:float ; store:aisleLocation "Cleaning" ; store:inStock "true"^^xsd:boolean ;
    store:isHazardous "true"^^xsd:boolean ; store:volume "0.5"^^xsd:float .

store:item_009 a store:StoreItem ;                       # → ClothingItem
    store:category "clothing" ;
    store:price "25.00"^^xsd:float ; store:aisleLocation "Apparel" ; store:inStock "true"^^xsd:boolean ;
    store:size "M" ; store:material "cotton" .

store:item_010 a store:StoreItem ;                       # → ElectronicsItem
    store:category "electronics" ;
    store:price "15.00"^^xsd:float ; store:aisleLocation "Electronics" ; store:inStock "true"^^xsd:boolean ;
    store:warrantyMonths "24"^^xsd:integer ; store:voltage "5.0"^^xsd:float .

store:item_011 a store:StoreItem ;                       # → PackagedFood, but PENDING for G3/G4
    store:category "grocery" ; store:foodType "packaged" ;
    store:price "3.00"^^xsd:float ; store:aisleLocation "Snacks" ; store:inStock "true"^^xsd:boolean ;
    store:requiresRefrigeration "false"^^xsd:boolean ; store:shelfStable "true"^^xsd:boolean .
    # NOTE: isVegan and calories deliberately omitted — label unreadable, open-world unknown.

store:item_012 a store:StoreItem ;                       # → PackagedFood
    store:category "grocery" ; store:foodType "packaged" ;
    store:price "3.80"^^xsd:float ; store:aisleLocation "Deli-veg" ; store:inStock "true"^^xsd:boolean ;
    store:isVegan "true"^^xsd:boolean ; store:calories "76"^^xsd:integer ;
    store:requiresRefrigeration "true"^^xsd:boolean ;
    store:ingredientsList "soybeans,water" ; store:shelfStable "false"^^xsd:boolean .
```

---

