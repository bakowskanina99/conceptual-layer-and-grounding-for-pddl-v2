## Part A — OWL 2 DL Ontology (Conceptual System, Section 3 + 6.1–6.2)

```turtle
@prefix store: <http://example.org/store#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

#################################################################
## Datatype properties (features, F)
#################################################################

store:price                  a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:float .
store:aisleLocation          a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:string .
store:inStock                a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:boolean .
store:category                a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:string .

store:expiryDate             a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:dateTime .
store:isVegan                a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:boolean .
store:calories                a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:integer .
store:allergens               a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:string .
store:requiresRefrigeration  a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:boolean .
store:foodType                a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:string .

store:isOrganic              a owl:DatatypeProperty ; rdfs:domain store:FreshProduce ;   rdfs:range xsd:boolean .
store:weight                  a owl:DatatypeProperty ; rdfs:domain store:FreshProduce ;   rdfs:range xsd:float .
store:produceType            a owl:DatatypeProperty ; rdfs:domain store:FreshProduce ;   rdfs:range xsd:string .

store:sugarContent           a owl:DatatypeProperty ; rdfs:domain store:Fruit ;          rdfs:range xsd:float .

store:ingredientsList        a owl:DatatypeProperty ; rdfs:domain store:PackagedFood ;   rdfs:range xsd:string .
store:shelfStable            a owl:DatatypeProperty ; rdfs:domain store:PackagedFood ;   rdfs:range xsd:boolean .

store:lactoseFree            a owl:DatatypeProperty ; rdfs:domain store:DairyProduct ;   rdfs:range xsd:boolean .
store:cutType                 a owl:DatatypeProperty ; rdfs:domain store:MeatProduct ;    rdfs:range xsd:string .

store:isHazardous            a owl:DatatypeProperty ; rdfs:domain store:HouseholdItem ;  rdfs:range xsd:boolean .
store:volume                  a owl:DatatypeProperty ; rdfs:domain store:HouseholdItem ;  rdfs:range xsd:float .

store:size                    a owl:DatatypeProperty ; rdfs:domain store:ClothingItem ;   rdfs:range xsd:string .
store:material                a owl:DatatypeProperty ; rdfs:domain store:ClothingItem ;   rdfs:range xsd:string .

store:warrantyMonths         a owl:DatatypeProperty ; rdfs:domain store:ElectronicsItem ; rdfs:range xsd:integer .
store:voltage                 a owl:DatatypeProperty ; rdfs:domain store:ElectronicsItem ; rdfs:range xsd:float .

#################################################################
## Classes and contracts (T, K)
#################################################################

store:StoreItem a owl:Class .

store:GroceryItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:StoreItem
        [ a owl:Restriction ; owl:onProperty store:category ; owl:hasValue "grocery" ]
    ) ] .

store:HouseholdItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:StoreItem
        [ a owl:Restriction ; owl:onProperty store:category ; owl:hasValue "household" ]
    ) ] .

store:ClothingItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:StoreItem
        [ a owl:Restriction ; owl:onProperty store:category ; owl:hasValue "clothing" ]
    ) ] .

store:ElectronicsItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:StoreItem
        [ a owl:Restriction ; owl:onProperty store:category ; owl:hasValue "electronics" ]
    ) ] .

store:FreshProduce a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:foodType ; owl:hasValue "fresh" ]
    ) ] .

store:PackagedFood a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:foodType ; owl:hasValue "packaged" ]
    ) ] .

store:DairyProduct a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:foodType ; owl:hasValue "dairy" ]
        [ a owl:Restriction ; owl:onProperty store:isVegan  ; owl:hasValue "false"^^xsd:boolean ]
    ) ] .

store:MeatProduct a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:foodType ; owl:hasValue "meat" ]
        [ a owl:Restriction ; owl:onProperty store:isVegan  ; owl:hasValue "false"^^xsd:boolean ]
        [ a owl:Restriction ; owl:onProperty store:requiresRefrigeration ; owl:hasValue "true"^^xsd:boolean ]
    ) ] .

store:Fruit a owl:Class ; rdfs:subClassOf store:FreshProduce ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:FreshProduce
        [ a owl:Restriction ; owl:onProperty store:produceType ; owl:hasValue "fruit" ]
    ) ] .

store:Vegetable a owl:Class ; rdfs:subClassOf store:FreshProduce ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:FreshProduce
        [ a owl:Restriction ; owl:onProperty store:produceType ; owl:hasValue "vegetable" ]
    ) ] .

#################################################################
## Assumption 3.1 (sibling discriminability) — OWL disjointness
#################################################################

[] a owl:AllDisjointClasses ;
   owl:members ( store:GroceryItem store:HouseholdItem store:ClothingItem store:ElectronicsItem ) .

[] a owl:AllDisjointClasses ;
   owl:members ( store:FreshProduce store:PackagedFood store:DairyProduct store:MeatProduct ) .

[] a owl:AllDisjointClasses ;
   owl:members ( store:Fruit store:Vegetable ) .
```

---

