## Part D — Compiled PDDL Domains (Section 5.1–5.3)

### D.1 — `domain_G1.pddl` (no restriction: 11 types, 24 features)

```lisp
(define (domain hypermarket-g1)
  (:requirements :typing :negative-preconditions :equality)

  (:types
    tag - object
    grocery-item household-item clothing-item electronics-item - store-item
    fresh-produce packaged-food dairy-product meat-product - grocery-item
    fruit vegetable - fresh-produce
  )

  (:constants
    ;; category values
    cat-grocery cat-household cat-clothing cat-electronics
    ;; food-type values
    food-fresh food-packaged food-dairy food-meat
    ;; produce-type values
    prod-fruit prod-vegetable
    - tag
  )

  (:predicates
    ;; --- 7 boolean features ---
    (in-stock ?x - store-item)
    (is-vegan ?x - grocery-item)
    (requires-refrigeration ?x - grocery-item)
    (is-organic ?x - fresh-produce)
    (shelf-stable ?x - packaged-food)
    (lactose-free ?x - dairy-product)
    (is-hazardous ?x - household-item)
    ;; --- 9 categorical (relational) features ---
    (category ?x - store-item ?v - tag)
    (food-type ?x - grocery-item ?v - tag)
    (produce-type ?x - fresh-produce ?v - tag)
    (aisle-location ?x - store-item ?v - tag)
    (allergens ?x - grocery-item ?v - tag)
    (ingredients-list ?x - packaged-food ?v - tag)
    (cut-type ?x - meat-product ?v - tag)
    (size ?x - clothing-item ?v - tag)
    (material ?x - clothing-item ?v - tag)
    ;; --- object-holding predicate for the planning task itself ---
    (in-cart ?x - store-item)
  )

  (:functions
    ;; --- 8 numeric features (incl. expiry-date as day offset) ---
    (price ?x - store-item)
    (calories ?x - grocery-item)
    (weight ?x - fresh-produce)
    (sugar-content ?x - fruit)
    (volume ?x - household-item)
    (warranty-months ?x - electronics-item)
    (voltage ?x - electronics-item)
    (expiry-date ?x - grocery-item)
  )

  (:action put-in-cart
    :parameters (?x - store-item)
    :precondition (and (in-stock ?x) (not (in-cart ?x)))
    :effect (in-cart ?x)
  )
)
```

*(24 declared features: 7 predicates + 9 relational predicates + 8 functions = matches
Section 5.3's $|\mathrm{pred}(D(G_1))|=24$; 11 types declared, matching $|D(G_1)|=11$.)*

### D.2 — `domain_G3.pddl` (vegan groceries: 5 types, 16 features)

```lisp
(define (domain hypermarket-g3)
  (:requirements :typing :negative-preconditions :equality)

  (:types
    tag - object
    fresh-produce packaged-food - grocery-item
    fruit vegetable - fresh-produce
  )
  ;; NOTE: dairy-product and meat-product do not appear — excluded by
  ;; Definition 4.4 (inadmissible), not merely unused. household-item,
  ;; clothing-item, electronics-item do not appear — excluded by
  ;; Definition 4.2 (irrelevant). grocery-item is the root of this
  ;; compiled hierarchy (its parent store-item is outside D(G3)).

  (:constants
    cat-grocery
    food-fresh food-packaged
    prod-fruit prod-vegetable
    - tag
  )

  (:predicates
    ;; --- 5 boolean features ---
    (in-stock ?x - grocery-item)
    (is-vegan ?x - grocery-item)
    (requires-refrigeration ?x - grocery-item)
    (is-organic ?x - fresh-produce)
    (shelf-stable ?x - packaged-food)
    ;; --- 6 categorical (relational) features ---
    (category ?x - grocery-item ?v - tag)
    (food-type ?x - grocery-item ?v - tag)
    (produce-type ?x - fresh-produce ?v - tag)
    (aisle-location ?x - grocery-item ?v - tag)
    (allergens ?x - grocery-item ?v - tag)
    (ingredients-list ?x - packaged-food ?v - tag)
    ;; --- planning-mechanism predicate (NOT a formal feature, excluded from the count) ---
    (in-cart ?x - grocery-item)
  )

  (:functions
    ;; --- 6 numeric features ---
    (price ?x - grocery-item)
    (calories ?x - grocery-item)
    (weight ?x - fresh-produce)
    (sugar-content ?x - fruit)
    (expiry-date ?x - grocery-item)
  )

  (:action put-in-cart
    :parameters (?x - grocery-item)
    :precondition (and (in-stock ?x) (not (in-cart ?x)))
    :effect (in-cart ?x)
  )
)
```

*(16 declared features: 5 boolean predicates + 6 relational predicates + 5 functions = 16,
matching Section 5.3's $|\mathrm{pred}(D(G_3))|=16$ exactly, with no domain-specific
optimisation — `category` is counted like any other inherited feature, consistent with
Definition 5.2 applied literally. An earlier draft of this file mistakenly omitted
`category`, which would have under-counted to 15; this is now corrected.)*

---

