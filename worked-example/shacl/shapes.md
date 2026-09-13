## Part B — SHACL Shapes (Section 6.2)

```turtle
@prefix store: <http://example.org/store#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

#################################################################
## Completeness shapes — one per grounded (leaf) type,
## checking that every K+ pair is observed (Definition 3.4,
## "undetermined" case). Used to detect pending/incomplete
## objects independently of any goal.
#################################################################

store:FruitCompletenessShape a sh:NodeShape ;
    sh:targetClass store:Fruit ;
    sh:property [ sh:path store:produceType ; sh:minCount 1 ] ;
    sh:property [ sh:path store:sugarContent ; sh:minCount 1 ] .

store:PackagedFoodCompletenessShape a sh:NodeShape ;
    sh:targetClass store:PackagedFood ;
    sh:property [ sh:path store:foodType ; sh:minCount 1 ] ;
    sh:property [ sh:path store:isVegan ; sh:minCount 1 ] ;
    sh:property [ sh:path store:calories ; sh:minCount 1 ] .

store:DairyProductCompletenessShape a sh:NodeShape ;
    sh:targetClass store:DairyProduct ;
    sh:property [ sh:path store:foodType ; sh:minCount 1 ] ;
    sh:property [ sh:path store:requiresRefrigeration ; sh:minCount 1 ] .

store:MeatProductCompletenessShape a sh:NodeShape ;
    sh:targetClass store:MeatProduct ;
    sh:property [ sh:path store:foodType ; sh:minCount 1 ] ;
    sh:property [ sh:path store:cutType ; sh:minCount 1 ] .

#################################################################
## Goal shapes (Definition 4.3–4.6) — G3 and G4.
## G1 needs no shape (Phi = R = empty set).
## G2 needs no property shape (type-level filtering only,
## already resolved by OWL classification).
#################################################################

store:G3VeganGoalShape a sh:NodeShape ;
    sh:targetClass store:GroceryItem ;
    sh:property [
        sh:path store:isVegan ;
        sh:minCount 1 ;
        sh:hasValue "true"^^xsd:boolean ;
        sh:severity sh:Violation ;
        sh:message "Missing is_vegan observation, or item is not vegan" ;
    ] .

store:G4VeganFitGoalShape a sh:NodeShape ;
    sh:targetClass store:GroceryItem ;
    sh:property [
        sh:path store:isVegan ;
        sh:minCount 1 ;
        sh:hasValue "true"^^xsd:boolean ;
        sh:severity sh:Violation ;
        sh:message "Missing is_vegan observation, or item is not vegan" ;
    ] ;
    sh:property [
        sh:path store:calories ;
        sh:minCount 1 ;
        sh:maxInclusive 150 ;
        sh:severity sh:Violation ;
        sh:message "Missing calories observation, or over 150 kcal" ;
    ] .

#################################################################
## Real-data goal shapes (Part A3) — photographic experiment,
## operating on Open Food Facts' native match/status fields
## instead of the symbolic walkthrough's simplified isVegan.
#################################################################

store:G3RealGoalShape a sh:NodeShape ;
    sh:targetClass store:GroceryItem ;
    sh:property [
        sh:path store:veganAttributeMatch ;
        sh:minCount 1 ;
        sh:hasValue 100 ;
        sh:severity sh:Violation ;
        sh:message "OFF vegan attribute status=unknown (missing), or match<100 (not vegan)" ;
    ] .

store:G4RealGoalShape a sh:NodeShape ;
    sh:targetClass store:GroceryItem ;
    sh:property [
        sh:path store:veganAttributeMatch ;
        sh:minCount 1 ;
        sh:hasValue 100 ;
        sh:severity sh:Violation ;
        sh:message "OFF vegan attribute status=unknown (missing), or match<100 (not vegan)" ;
    ] ;
    sh:property [
        sh:path store:calories ;
        sh:minCount 1 ;
        sh:maxInclusive 55 ;
        sh:severity sh:Violation ;
        sh:message "Missing calories observation, or over 55 kcal/100g" ;
    ] .
    # NOTE: threshold is 55, not the symbolic walkthrough's illustrative 150,
    # and the constraint is on calories directly rather than nutriscoreMatch.
    # See rationale in Part A3 above. nutriscoreMatch remains a stored
    # property in reference_labels.json for reference/analysis only -- it is
    # no longer part of any SHACL shape or agent-facing prompt.
```

---

