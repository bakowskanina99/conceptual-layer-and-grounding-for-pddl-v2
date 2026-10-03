"""Reference implementation of Algorithm 1 (VerifySiblingDiscriminability),
parsing an OWL 2 DL Turtle encoding directly via rdflib -- no hand transcription
of contracts, to avoid exactly the kind of silent error this paper is about.

Extracts, per class: its immediate rdfs:subClassOf parent, and its K+/K- sets
(categorical (feature, value) requirements/forbiddances) from the
owl:Restriction nodes inside its owl:equivalentClass/owl:intersectionOf
definition -- owl:hasValue directly for K+, owl:hasValue wrapped in
owl:complementOf for K- (the standard OWL idiom for "forbidden value").
Every owl:hasValue restriction is treated as categorical, including
boolean-valued ones (a boolean feature has a finite, unordered domain, which is
the paper's definition of a categorical feature); numeric restrictions are out
of scope (Sect. 3).

Output: `violations` (sibling pairs of internally realizable types with no
discriminating witness, Theorem 1) and `unrealizable` (types whose own contract
fails the Sect. 4.1 precheck) are reported separately, never conflated.

Neither `well_formed.ttl` nor `weakened.ttl` (Sect. 6) actually uses
owl:complementOf, has an internally-inconsistent contract, or declares an
enumerated feature domain, so K- and the internal precheck are both exercised
only vacuously against those two files -- included here for correctness and
completeness, not because the validation set happens to exercise them (see the
paper's Sect. 6 note on this).

Usage:  python verify_sibling_discriminability.py [--domains DOMAINS.json] FILE.ttl ...
DOMAINS.json (optional) maps a feature IRI to the full list of its values, e.g.
{"http://example.org/store#size": ["small", "large"]}; it enables precheck
case (3), which needs dom(f).
"""
import json
import sys
from itertools import combinations
from collections import defaultdict
import rdflib
from rdflib import RDF, RDFS, OWL

def load_contracts(ttl_path):
    g = rdflib.Graph()
    g.parse(ttl_path, format="turtle")

    parent = {}
    kplus = defaultdict(set)   # cls -> set of (feature, value), required
    kminus = defaultdict(set)  # cls -> set of (feature, value), forbidden

    classes = set(g.subjects(RDF.type, OWL.Class))
    for cls in classes:
        for p in g.objects(cls, RDFS.subClassOf):
            if p in classes:
                parent[cls] = p

        for eq in g.objects(cls, OWL.equivalentClass):
            for inter in g.objects(eq, OWL.intersectionOf):
                for item in g.items(inter):
                    if (item, RDF.type, OWL.Restriction) not in g:
                        continue
                    prop = g.value(item, OWL.onProperty)
                    val = g.value(item, OWL.hasValue)
                    if prop is not None and val is not None:
                        kplus[cls].add((str(prop), str(val)))
                        continue
                    comp = g.value(item, OWL.someValuesFrom)
                    if comp is not None:
                        neg_val = g.value(comp, OWL.complementOf)
                        # owl:complementOf [owl:hasValue v] pattern for K-
                        if neg_val is not None:
                            v = g.value(neg_val, OWL.hasValue)
                            if v is not None:
                                kminus[cls].add((str(prop), str(v)))
    return parent, kplus, kminus

def internally_consistent(kplus_t, kminus_t, domains=None):
    """Precheck (Sect. 4.1): reject a type whose own contract admits no
    complete valuation sigma_t (Definition 2). Three cases:
      (1) the same (feature, value) is both required and forbidden;
      (2) two different required values of the same functional feature;
      (3) K-(t) forbids every value in some feature's domain, so sigma_t(f)
          has nothing left to take -- needs dom(f) known, via `domains`
          (feature -> full value set), not just the values mentioned in K-(t).
    Neither well_formed.ttl nor weakened.ttl declares an enumerated domain
    (owl:oneOf) for any categorical feature, so case (3) is never exercised
    against real data here (same caveat as Sect. 6's note on K- and this
    precheck generally); it is implemented regardless."""
    if kplus_t & kminus_t:
        return False
    by_feature_plus = defaultdict(set)
    for f, v in kplus_t:
        by_feature_plus[f].add(v)
    if any(len(vs) > 1 for vs in by_feature_plus.values()):
        return False
    if domains:
        by_feature_minus = defaultdict(set)
        for f, v in kminus_t:
            by_feature_minus[f].add(v)
        for f, forbidden in by_feature_minus.items():
            if f in domains and forbidden >= set(domains[f]):
                return False
    return True

def cat_consistent(t1, t2, kplus, kminus):
    """K(t1) ~cat K(t2): categorical contract consistency, Definition 3.
    True iff none of conditions (i)-(iii) holds, i.e. no discriminating
    witness exists (Lemma 1). Returns (consistent, witness_feature_or_None)."""
    kp1, km1 = kplus.get(t1, set()), kminus.get(t1, set())
    kp2, km2 = kplus.get(t2, set()), kminus.get(t2, set())

    by_feature_1 = defaultdict(set)
    for f, v in kp1:
        by_feature_1[f].add(v)
    for f, v2 in kp2:  # condition (i): conflicting K+/K+
        if f in by_feature_1 and any(v1 != v2 for v1 in by_feature_1[f]):
            return False, f
    for f, v in kp1 & km2:  # condition (ii): K+(t1) cap K-(t2)
        return False, f
    for f, v in km1 & kp2:  # condition (iii): K-(t1) cap K+(t2)
        return False, f
    return True, None

def verify(ttl_path, domains=None):
    parent, kplus, kminus = load_contracts(ttl_path)
    children = defaultdict(list)
    for c, p in parent.items():
        children[p].append(c)

    unrealizable = {t for t in set(kplus) | set(kminus) | set(parent)
                    if not internally_consistent(kplus.get(t, set()), kminus.get(t, set()), domains)}

    violations = []
    checked = 0
    for p, kids in children.items():
        kids = [k for k in kids if k not in unrealizable]
        for t1, t2 in combinations(sorted(kids, key=str), 2):
            checked += 1
            consistent, feature = cat_consistent(t1, t2, kplus, kminus)
            if consistent:  # Lemma 1: K(t1) ~cat K(t2) <=> no witness => violation
                violations.append((t1.split('#')[-1], t2.split('#')[-1]))
    return checked, violations, {t.split('#')[-1] for t in unrealizable}

if __name__ == "__main__":
    args = sys.argv[1:]
    domains = None
    if args and args[0] == "--domains":
        with open(args[1], encoding="utf-8") as fh:
            domains = {f: set(vs) for f, vs in json.load(fh).items()}
        args = args[2:]
    for path in args:
        checked, violations, unrealizable = verify(path, domains)
        print(f"\n=== {path} ===")
        print(f"Pairs checked: {checked}")
        print(f"Violations ({len(violations)}):")
        for t1, t2 in violations:
            print(f"  {t1} / {t2}")
        if unrealizable:
            print(f"Unrealizable types (internally inconsistent; excluded from pairwise checks): {sorted(unrealizable)}")
