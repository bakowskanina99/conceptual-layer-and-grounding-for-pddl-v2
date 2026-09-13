"""Variant A -- no conceptual system (naive baseline). Prompt text verbatim
from agent_prompts_ABCD.md, "Variant A -- no conceptual system (naive
baseline)". Only {SHOPPING_GOAL_IN_PLAIN_LANGUAGE}, {N}, and the shared
schema/worked-example blocks are template-filled; no other wording is
altered, per the spec's explicit instruction not to paraphrase."""

from pipeline.prompts.shared_schema import WORKED_EXAMPLE, shared_output_schema_block

_TEMPLATE = """You are a shopping assistant agent. Your task is: {goal}
(e.g. "Buy only the vegan grocery items needed for the household — ignore anything
that does not help complete this specific goal.")

You have been given {n} photographs of items on a hypermarket shelf, labelled
obj_001 through obj_{n}. For each photograph, decide what kind of item it shows and
describe the properties relevant to your task, in your own judgement — you have not
been given any predefined category system or list of properties to use. Use whatever
category names and property names you think are clearest and most useful for
completing the stated goal.

IMPORTANT — you are explicitly asked to be concise and goal-relevant, not
exhaustive: only include objects and properties that actually matter for deciding
whether an item helps complete the stated shopping goal. If an item is clearly
irrelevant to the goal (e.g. a household cleaning product when the goal is about
groceries), you may still list it, but set "included_in_description": false with a
brief reason, rather than describing it in full. Do not invent information you
cannot see or reasonably infer from the photograph.

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
        schema_block=shared_output_schema_block(),
        worked_example=WORKED_EXAMPLE,
    )
