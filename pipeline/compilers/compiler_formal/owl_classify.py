"""Stage 2: OWL classification (HermiT) + agent/reasoner agreement diagnostic.

compiler_pipeline_spec.md, Stage 2. Loads the well-formed ontology (Variant
B/C) or the weakened one (Variant D), asserts one individual's observed
properties (Stage 1 triples, plus the Stage 1b veganAttributeMatch synthesis
when applicable), and runs HermiT via owlready2 to compute
G_cert(o, C) (Definition 3.6).

owlready2 cannot natively parse Turtle, so ontology loading goes via an
rdflib Turtle -> RDF/XML bridge (see `load_ontology_world`).

One `OwlClassifier` is built per ontology variant (well-formed / weakened) and
reused across objects: each `classify_object` call creates one temporary
individual, reasons over it, records the result, then destroys the individual
so the next object starts from a clean TBox+ABox instead of accumulating state
or paying the full ontology-load cost per object.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import owlready2
import rdflib

STORE_NS = "http://example.org/store#"

# Found empirically: asserting a non-ISO-format date
# string (e.g. an agent-reported "09/20/2023") for `expiry_date` -- whose
# ontology range is declared xsd:dateTime -- triggers a SPURIOUS
# `OwlReadyInconsistentOntologyError` in HermiT: not a genuine logical
# contradiction (Assumption 3.1/Lemma 4.1's subject), but a datatype-format
# artifact. `expiry_date` plays no role in any type contract, goal, or SHACL
# shape in this experiment, so it is excluded from OWL/
# reasoner assertion entirely -- it remains correctly captured in the log and
# in compiled PDDL :init facts, only Stage 2 classification skips it.
REASONING_EXCLUDED_PROPERTIES = {"expiry_date"}


def _camel_case(snake: str) -> str:
    """properties in the agent JSON / coerced dict are snake_case
    (is_vegan, food_type, ...); the ontology uses camelCase (isVegan,
    foodType, ...). This is the single conversion point both rdf_individuals
    and owl_classify rely on -- keep it here so it is defined exactly once."""
    parts = snake.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def ttl_to_owlready_world(ttl_path: Path) -> tuple[owlready2.World, owlready2.Ontology]:
    """Bridges Turtle -> RDF/XML (owlready2 has no native Turtle parser) and
    loads the result into a fresh, isolated owlready2 World (never the global
    default_world -- keeps well-formed and weakened ontologies from ever
    sharing state)."""
    g = rdflib.Graph()
    g.parse(str(ttl_path), format="turtle")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".owl", delete=False, encoding="utf-8"
    ) as tmp:
        g.serialize(destination=tmp.name, format="xml")
        tmp_path = tmp.name

    world = owlready2.World()
    onto = world.get_ontology(f"file://{tmp_path}").load()
    return world, onto


class OwlClassifier:
    def __init__(self, ttl_path: Path):
        self.ttl_path = ttl_path
        self.world, self.onto = ttl_to_owlready_world(ttl_path)
        self.store_ns_owlready = self.onto.get_namespace(STORE_NS)

    def classify_object(self, object_id: str, coerced_properties: dict, extra_properties: dict | None = None) -> dict:
        """coerced_properties: {snake_case_property_name: coerced_value}, from
        Stage 0 (None values already mean "leave unasserted", per Definition
        3.2 -- must not be passed in as literal None assertions).

        extra_properties: additional {camelCase_or_snake_case: value} pairs to
        assert that are NOT part of the agent's own reported properties (e.g.
        Stage 1b's synthesized veganAttributeMatch) -- kept as a separate
        parameter, not merged into coerced_properties by the caller, so the
        provenance distinction (agent-reported vs. compiler-derived) survives
        into this function's own reasoning, not just the log.

        Returns a dict matching compiler_pipeline_spec.md Stage 2's shape:
        {status, reasoner_type(s), agent_type, agreement}.
        """
        StoreItem = self.store_ns_owlready.StoreItem
        individual = StoreItem(f"ind_{object_id}", namespace=self.store_ns_owlready)

        all_props = dict(coerced_properties)
        if extra_properties:
            all_props.update(extra_properties)

        try:
            for prop_name, value in all_props.items():
                if value is None:
                    continue  # Definition 3.2: absence, never asserted
                if prop_name in REASONING_EXCLUDED_PROPERTIES:
                    continue  # see REASONING_EXCLUDED_PROPERTIES docstring
                owl_prop_name = _camel_case(prop_name)
                owl_prop = getattr(self.store_ns_owlready, owl_prop_name, None)
                if owl_prop is None:
                    continue  # feature not declared in THIS ontology variant (e.g. Variant D's weakened set)
                getattr(individual, owl_prop_name).append(value)

            try:
                owlready2.sync_reasoner(self.world, infer_property_values=False, debug=0)
            except owlready2.OwlReadyInconsistentOntologyError:
                return {
                    "status": "reasoner_inconsistent",
                    "reasoner_type": None,
                    "reasoner_types": [],
                }

            inferred = [c for c in individual.INDIRECT_is_a if c is not owlready2.Thing and hasattr(c, "name")]
            most_specific = _most_specific_types(inferred)

            if len(most_specific) > 1:
                return {
                    "status": "ambiguous_grounding",
                    "reasoner_type": None,
                    "reasoner_types": sorted(c.name for c in most_specific),
                }

            if len(most_specific) == 0:
                # Should not happen (StoreItem is always asserted), but fail loudly-in-data rather than crash
                return {"status": "no_type_inferred", "reasoner_type": None, "reasoner_types": []}

            resolved_class = most_specific[0]
            ancestor_names = [
                c.name for c in resolved_class.ancestors()
                if c is not owlready2.Thing and hasattr(c, "name")
            ]
            return {
                "status": "resolved",
                "reasoner_type": resolved_class.name,
                "reasoner_types": [resolved_class.name],
                # Needed by Stage 3 (shacl_validate.py) to assert rdf:type for
                # the full class chain in its OWN independent rdflib graph --
                # sh:targetClass matching needs every ancestor, not just the
                # most-specific class, and Stage 3 deliberately does not reach
                # back into owlready2's internal World to get it.
                "reasoner_type_ancestors": ancestor_names,
            }
        finally:
            owlready2.destroy_entity(individual)


def _most_specific_types(classes: list) -> list:
    """Given the set of inferred owl classes for one individual, return the
    ones with no other class in the same set that is a STRICT subclass of
    them -- Definition 3.6's most-specific-type computation. More than one
    result means the classes are NOT chain-forming under <=_T (the
    non-chain-forming case Lemma 4.1 / Assumption 3.1 are about).

    Must use STRICT subclass (c in other.ancestors() AND other NOT in
    c.ancestors()), not "any ancestor relation" -- two classes owlready2
    reports as mutually equivalent (owl:equivalentClass, as the weakened
    ontology deliberately produces for several sibling groups) each appear in
    the other's ancestors() too. Treating that mutual relation as
    "dominated" would make every class in an equivalence group appear
    dominated by its own equivalence partner, incorrectly returning an EMPTY
    most-specific set instead of reporting the tied/collapsed group -- which
    is itself a valid, even more extreme instance of ambiguous grounding.
    """
    result = []
    for c in classes:
        dominated_by_strict_subclass = any(
            (other is not c) and (c in other.ancestors()) and (other not in c.ancestors())
            for other in classes
        )
        if not dominated_by_strict_subclass:
            result.append(c)
    return result


def normalise_type_name(name: str | None) -> str | None:
    """Case/underscore/space-insensitive comparison for agent-vs-reasoner type
    agreement (the agent writes "dairy_product" or "Dairy Product"; the
    reasoner/ontology writes "DairyProduct")."""
    if name is None:
        return None
    return re.sub(r"[\s_]+", "", name).lower()
