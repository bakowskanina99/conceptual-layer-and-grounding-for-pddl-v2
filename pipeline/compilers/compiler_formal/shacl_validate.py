"""Stage 3: SHACL goal-shape validation (compiler_pipeline_spec.md), Variants
C/D only (skipped for B -- B has no D(G) restriction to validate against).

Only meaningful for an object whose Stage 2 grounding_status is "resolved"
(Definition 4.6 presupposes a singleton grounded type, Definition 3.6) -- the
caller (the pipeline orchestrator) is responsible for not invoking this for
ambiguous_grounding/reasoner_inconsistent objects; this module assumes a
single resolved type and does not special-case the alternative.

Builds a SMALL, INDEPENDENT rdflib graph for the one individual being checked
(rdf:type for the resolved type and every ancestor, plus its observed
properties as typed literals) rather than reusing owlready2's internal World
-- keeps this stage decoupled from Stage 2's reasoner state and lets it be
tested/reasoned about on its own.

Validates against exactly ONE named goal shape at a time (e.g.
"G3RealGoalShape"), not the whole shapes.ttl graph -- shapes.ttl also contains
the symbolic G3VeganGoalShape/G4VeganFitGoalShape and completeness shapes,
which target the same classes with different property paths and would
otherwise contaminate the result with irrelevant violations.
"""

from __future__ import annotations

import rdflib
from rdflib import RDF, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from pipeline.compilers.compiler_formal.owl_classify import _camel_case
from pipeline.config import SHAPES_TTL, STORE_NS
from pipeline.feature_domains import FEATURE_DOMAINS

STORE = Namespace(STORE_NS)
SH = Namespace("http://www.w3.org/ns/shacl#")

_shapes_graph_cache: dict[str, rdflib.Graph] = {}


def load_shapes_graph(shapes_ttl_path=SHAPES_TTL) -> rdflib.Graph:
    key = str(shapes_ttl_path)
    if key not in _shapes_graph_cache:
        g = rdflib.Graph()
        g.parse(str(shapes_ttl_path), format="turtle")
        _shapes_graph_cache[key] = g
    return _shapes_graph_cache[key]


def extract_shape_subgraph(full_graph: rdflib.Graph, shape_local_name: str) -> tuple[rdflib.Graph, URIRef]:
    """Copies the named shape plus the transitive closure of every blank node
    it references (sh:property [...] blocks) into a standalone graph -- so
    pySHACL only ever sees the one goal shape we asked for."""
    shape_uri = STORE[shape_local_name]
    sub = rdflib.Graph()
    seen: set = set()
    frontier = [shape_uri]
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        for s, p, o in full_graph.triples((node, None, None)):
            sub.add((s, p, o))
            if isinstance(o, rdflib.BNode) and o not in seen:
                frontier.append(o)
    if len(sub) == 0:
        raise ValueError(f"Shape '{shape_local_name}' not found in {SHAPES_TTL} (0 triples extracted)")
    return sub, shape_uri


def _literal_for(feature_name: str, value, feature_domain_table: dict = FEATURE_DOMAINS) -> Literal:
    domain = feature_domain_table.get(feature_name, "categorical")
    if domain == "boolean":
        return Literal(bool(value), datatype=XSD.boolean)
    if domain == "numeric":
        # veganAttributeMatch/calories are declared xsd:integer in the ontology;
        # SHACL sh:hasValue 100 / sh:maxInclusive 55 are typed xsd:integer
        # literals -- an xsd:float literal (e.g. 100.0) would NOT term-match
        # sh:hasValue 100 under SHACL's exact-value-match semantics, so
        # integer-valued numerics must be emitted as xsd:integer, not
        # xsd:float, or admission would silently fail for every object.
        if float(value).is_integer():
            return Literal(int(value), datatype=XSD.integer)
        return Literal(float(value), datatype=XSD.float)
    return Literal(str(value))


def build_individual_graph(
    object_id: str,
    reasoner_type: str,
    reasoner_type_ancestors: list[str],
    coerced_properties: dict,
    extra_properties: dict,
    feature_domain_table: dict = FEATURE_DOMAINS,
) -> tuple[rdflib.Graph, URIRef]:
    g = rdflib.Graph()
    ind = STORE[object_id]

    g.add((ind, RDF.type, STORE[reasoner_type]))
    for ancestor in reasoner_type_ancestors:
        g.add((ind, RDF.type, STORE[ancestor]))

    all_props = dict(coerced_properties)
    all_props.update(extra_properties)
    for prop, value in all_props.items():
        if value is None:
            continue
        g.add((ind, STORE[_camel_case(prop)], _literal_for(prop, value, feature_domain_table)))

    return g, ind


def _shacl_status_from_report(conforms: bool, results_graph: rdflib.Graph) -> str:
    """Definition 4.6's priority: EXCLUDED (a real, observed violation) beats
    PENDING (a missing observation) when both occur -- but only across
    DIFFERENT property paths (relevant for G4RealGoalShape's two sh:property
    blocks; G3RealGoalShape has only one, where this never arises).

    Must group violations by sh:resultPath first: when a property is fully
    absent, pySHACL fires BOTH sh:minCount AND (e.g.) sh:hasValue on that SAME
    path simultaneously (the value set is empty, so hasValue fails too) --
    naively treating "any non-minCount violation anywhere" as "excluded" would
    wrongly call a simply-missing property "excluded" instead of "pending"
    (this is exactly what an earlier version of this function got wrong,
    caught by testing against a missing-veganAttributeMatch case). The
    correct rule: a path where minCount fired is "missing", full stop,
    regardless of what else co-fired on that SAME path; a path where a
    violation fired WITHOUT minCount is a genuine wrong-value-present case.
    Only the latter counts as "excluded".

    This is a deliberate, narrow refinement of compiler_pipeline_spec.md's
    illustrative single-check pseudocode (which only ever considered
    G3's one-property shape, where the two approaches agree) so the
    implementation matches Definition 4.6's stated priority exactly once a
    second, independent property (G4_real's calories) is added.
    """
    if conforms:
        return "admitted"

    path_to_components: dict = {}
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        paths = list(results_graph.objects(result, SH.resultPath))
        path = paths[0] if paths else None
        components = set(results_graph.objects(result, SH.sourceConstraintComponent))
        path_to_components.setdefault(path, set()).update(components)

    has_wrong_value_present = False
    has_missing = False
    for components in path_to_components.values():
        if SH.MinCountConstraintComponent in components:
            has_missing = True
        else:
            has_wrong_value_present = True

    if has_wrong_value_present:
        return "excluded"
    if has_missing:
        return "pending"
    return "excluded"  # conforms=False with no recognized component -- fail visibly, not silently as "admitted"


def validate_goal_shape(
    object_id: str,
    reasoner_type: str,
    reasoner_type_ancestors: list[str],
    coerced_properties: dict,
    extra_properties: dict,
    goal_shape_name: str,
    agent_included,
    agent_reason,
    feature_domain_table: dict = FEATURE_DOMAINS,
    shapes_ttl_path=SHAPES_TTL,
) -> dict:
    import pyshacl

    data_graph, _ind = build_individual_graph(
        object_id, reasoner_type, reasoner_type_ancestors, coerced_properties, extra_properties, feature_domain_table
    )
    full_shapes = load_shapes_graph(shapes_ttl_path)
    shape_graph, _shape_uri = extract_shape_subgraph(full_shapes, goal_shape_name)

    conforms, results_graph, _results_text = pyshacl.validate(
        data_graph,
        shacl_graph=shape_graph,
        ont_graph=None,
        inference=None,
        abort_on_first=False,
        meta_shacl=False,
        advanced=False,
        debug=False,
    )

    shacl_status = _shacl_status_from_report(conforms, results_graph)
    agent_included_bool = bool(agent_included)

    return {
        "shacl_status": shacl_status,
        "shacl_conforms": conforms,
        "agent_included": agent_included,
        "agent_reason": agent_reason,
        "agent_shacl_agreement": (shacl_status == "admitted") == agent_included_bool,
    }
