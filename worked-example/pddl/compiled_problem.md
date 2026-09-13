## Part E — Compiled PDDL Problem (Section 5.4), for $G_3$

```lisp
(define (problem shopping-g3)
  (:domain hypermarket-g3)

  (:objects item_001 item_002 item_004 item_006 item_011 item_012 - grocery-item)
  ;; item_003, item_005 (dairy/meat) excluded: type-inadmissible (Def. 4.4)
  ;; item_007 excluded: instance-excluded, observed is-vegan=false (Def. 4.6)
  ;; item_008/009/010 excluded: irrelevant type (Def. 4.2), not compiled at all
  ;; item_011 included but PENDING: is-vegan/calories unobserved (Def. 4.6) —
  ;;   see Section 5.4 remark on the open-world/closed-world compilation gap;
  ;;   its is-vegan and calories facts are simply absent below, which a
  ;;   classical closed-world planner will read as false/undefined, not "unknown".

  (:init
    (in-stock item_001) (is-vegan item_001) (is-organic item_001)
    (category item_001 cat-grocery) (food-type item_001 food-fresh) (produce-type item_001 prod-fruit)
    (= (price item_001) 0.50) (= (calories item_001) 52) (= (weight item_001) 0.15) (= (sugar-content item_001) 10.0)

    (in-stock item_002) (is-vegan item_002)
    (category item_002 cat-grocery) (food-type item_002 food-fresh) (produce-type item_002 prod-vegetable)
    (= (price item_002) 0.30) (= (calories item_002) 41) (= (weight item_002) 0.10)

    (in-stock item_004) (is-vegan item_004) (requires-refrigeration item_004) (shelf-stable item_004)
    (category item_004 cat-grocery) (food-type item_004 food-packaged)
    (= (price item_004) 4.20) (= (calories item_004) 45)

    (in-stock item_006) (is-vegan item_006) (shelf-stable item_006)
    (category item_006 cat-grocery) (food-type item_006 food-packaged)
    (= (price item_006) 2.10) (= (calories item_006) 127)

    (in-stock item_011) (shelf-stable item_011)
    (category item_011 cat-grocery) (food-type item_011 food-packaged)
    (= (price item_011) 3.00)
    ;; is-vegan, calories: deliberately absent (pending, not false)

    (in-stock item_012) (is-vegan item_012) (requires-refrigeration item_012)
    (category item_012 cat-grocery) (food-type item_012 food-packaged)
    (= (price item_012) 3.80) (= (calories item_012) 76)
  )

  (:goal (and
    (in-cart item_001) (in-cart item_002) (in-cart item_004)
    (in-cart item_006) (in-cart item_012)
    ;; item_011 intentionally omitted from the goal — pending resolution
  ))
)
```
