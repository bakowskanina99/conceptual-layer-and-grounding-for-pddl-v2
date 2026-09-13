"""Variant B -- full conceptual system, no goal restriction. Prompt text
verbatim from agent_prompts_ABCD.md, "Variant B -- full conceptual system, no
goal restriction". The doc's "(worked example identical to Variant A's,
omitted here for brevity -- use the same one)" is an instruction to the
implementer, not literal prompt text -- the actual worked example JSON is
substituted here, exactly as given for Variant A."""

from pipeline.prompts.ontology_json import WELL_FORMED_ONTOLOGY_JSON
from pipeline.prompts.shared_schema import WORKED_EXAMPLE, shared_output_schema_block

_TEMPLATE = """You are a shopping assistant agent operating with a formal conceptual system that
defines every category of item that can exist in this hypermarket, and the
properties and requirements associated with each category. If a category is not
listed below, it does not exist in this system — do not invent new categories.

Your task is: {goal}

CONCEPTUAL SYSTEM (types, their parent type, required property values that define
membership in the type, and the additional properties applicable to the type):

{ontology_json}

You have been given {n} photographs of items on a hypermarket shelf, labelled
obj_001 through obj_{n}. For each photograph:

1. Determine which type from the conceptual system above best matches the object,
   using the required property values as your classification criteria — a type's
   "required" dict lists property values that MUST hold for an object to belong to
   that type. Prefer the most specific matching type (e.g. if an object matches both
   GroceryItem and Fruit, report Fruit, since Fruit is more specific).
2. Report every property listed for that type AND all of its ancestor types (a
   Fruit inherits every property listed for FreshProduce, GroceryItem, and
   StoreItem, in addition to its own).
3. Describe every object you are given — do not skip any object in this variant.

Output your answer as a single JSON object with this exact structure:

{schema_block}

Here is a worked example for a single, unrelated photo, showing the expected level
of detail (do not copy these values — this is a format example only):

{worked_example}

Now process the {n} photographs provided and return only the JSON object."""


def build_prompt(shopping_goal_plain_language: str, n: int) -> str:
    return _TEMPLATE.format(
        goal=shopping_goal_plain_language,
        n=n,
        ontology_json=WELL_FORMED_ONTOLOGY_JSON,
        schema_block=shared_output_schema_block(),
        worked_example=WORKED_EXAMPLE,
    )
