## Part A2 — Weakened OWL Ontology for Variant D (ablation, Assumption 3.1 violated)

Identical to Part A except: for every sibling group that loses its discriminating
feature, the **corresponding `owl:disjointWith`/`owl:AllDisjointClasses` axiom is also
removed**. This is the corrected design (see version note above) — removing the
feature alone while keeping disjointness turns the ablation into a guaranteed 100%
ontology-inconsistency for nearly every object (uninformative, looks rigged); removing
both produces genuine *ambiguous grounding* (multiple sibling types simultaneously,
non-uniquely, satisfied), which is the actual failure mode Definition 3.6 and Lemma 4.1
are about.

```turtle
@prefix store: <http://example.org/store#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

#################################################################
## Same datatype properties as Part A, EXCEPT category/foodType/
## produceType are omitted entirely (the agent cannot observe what
## it is never told exists as a feature — see agent_prompts_ABCD.md,
## "Ontology JSON (Variant D — weakened)")
#################################################################

store:price                 a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:float .
store:aisleLocation         a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:string .
store:inStock                a owl:DatatypeProperty ; rdfs:domain store:StoreItem ;      rdfs:range xsd:boolean .
store:expiryDate             a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:dateTime .
store:isVegan                a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:boolean .
store:calories                a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:integer .
store:allergens               a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:string .
store:requiresRefrigeration  a owl:DatatypeProperty ; rdfs:domain store:GroceryItem ;    rdfs:range xsd:boolean .
store:isOrganic              a owl:DatatypeProperty ; rdfs:domain store:FreshProduce ;   rdfs:range xsd:boolean .
store:weight                  a owl:DatatypeProperty ; rdfs:domain store:FreshProduce ;   rdfs:range xsd:float .
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
## Classes — contracts stripped of discriminating requirements
#################################################################

store:StoreItem a owl:Class .

store:GroceryItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:StoreItem ) ] .

store:HouseholdItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:StoreItem ) ] .

store:ClothingItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:StoreItem ) ] .

store:ElectronicsItem a owl:Class ; rdfs:subClassOf store:StoreItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:StoreItem ) ] .

store:FreshProduce a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:GroceryItem ) ] .

store:PackagedFood a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:GroceryItem ) ] .

# DairyProduct/MeatProduct keep their isVegan/requiresRefrigeration requirements —
# those were never the discriminating features under test (category/foodType/
# produceType were); this is intentional, per the ablation's single-axis design.
store:DairyProduct a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:isVegan ; owl:hasValue "false"^^xsd:boolean ]
    ) ] .

store:MeatProduct a owl:Class ; rdfs:subClassOf store:GroceryItem ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        store:GroceryItem
        [ a owl:Restriction ; owl:onProperty store:isVegan ; owl:hasValue "false"^^xsd:boolean ]
        [ a owl:Restriction ; owl:onProperty store:requiresRefrigeration ; owl:hasValue "true"^^xsd:boolean ]
    ) ] .

store:Fruit a owl:Class ; rdfs:subClassOf store:FreshProduce ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:FreshProduce ) ] .

store:Vegetable a owl:Class ; rdfs:subClassOf store:FreshProduce ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf ( store:FreshProduce ) ] .

#################################################################
## Disjointness — REMOVED for the groups that lost their
## discriminator (this is the fix). DairyProduct/MeatProduct keep
## their mutual disjointness -- kept AS-IS, deliberately, even though
## it now produces a genuine reasoner inconsistency (see below) --
## while FreshProduce/PackagedFood are no longer disjoint from EACH
## OTHER, Fruit/Vegetable are no longer disjoint from each other, and
## the four StoreItem-level siblings are no longer mutually disjoint.
##
## VERIFIED EMPIRICAL EFFECT (HermiT, confirmed against this exact
## ontology -- not the milder effect an earlier draft of this note
## predicted):
##
## (a) TOTAL COLLAPSE, not localized sibling ambiguity. Every
##     non-Dairy/Meat object -- regardless of its properties --
##     grounds as ALL NINE of StoreItem/GroceryItem/HouseholdItem/
##     ClothingItem/ElectronicsItem/FreshProduce/PackagedFood/Fruit/
##     Vegetable simultaneously (Definition 3.6's non-chain-forming
##     case, at its most extreme). This is mathematically forced, not
##     a construction error: category/foodType/produceType are
##     removed at all three nested sibling levels at once, and each
##     `owl:equivalentClass [intersectionOf(single unrestricted
##     parent)]` makes that class LITERALLY IDENTICAL to its parent --
##     which chains transitively through all three nested levels into
##     one undifferentiated equivalence class. Report this as the
##     ablation's headline ambiguous-grounding result — see
##     `results/variant-D-ablation-full-results.md` for the full
##     ablation results.
##
## (b) A SEPARATE, NAMED failure mode for Dairy/Meat: not "comparatively
##     reliable" as originally predicted here, but a genuine, fully
##     explicable, LOCALIZED reasoner_inconsistent for every meat-like
##     object specifically. Once foodType is gone, MeatProduct's
##     contract (isVegan=false AND requiresRefrigeration=true) is a
##     strict subset match of DairyProduct's now-weaker contract
##     (isVegan=false alone) -- so every meat-like object automatically
##     satisfies Dairy's weaker condition too, contradicting their
##     retained owl:disjointWith. Deliberately kept as specified (a
##     locked decision, not a bug): this is qualitatively different
##     from the "100% ontology-inconsistency for nearly every object"
##     failure mode the disjointness-removal fix above was designed to
##     avoid -- it is narrow (meat-like objects only), fully explicable
##     from the axioms, and arguably a more interesting result in its
##     own right than uniform ambiguity. Dairy-only objects (isVegan
##     false, requiresRefrigeration false/absent) are unaffected and
##     resolve cleanly as DairyProduct.
##
## Report (a) and (b) as two DISTINCT, separately-named categories
## (`ambiguous_grounding` vs. `reasoner_inconsistent` -- the per-object
## log already distinguishes them, compiler_pipeline_spec.md Stage 2;
## see `results/variant-D-ablation-full-results.md` for the full
## breakdown) -- not every part of the ablated ontology fails the same
## way, and flattening both into one aggregate "failure rate" would
## erase exactly the gradient that makes this ablation informative.
#################################################################

[] a owl:AllDisjointClasses ;
   owl:members ( store:DairyProduct store:MeatProduct ) .
```

---

