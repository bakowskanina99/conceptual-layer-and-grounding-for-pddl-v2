"""Shared output schema + shared rules text, verbatim from agent_prompts_ABCD.md
("Shared output schema (identical across all four variants)"). Defined once
here and interpolated into all four variant prompts, so a wording change can
never accidentally happen in only one variant."""

SHARED_OUTPUT_SCHEMA = """{
  "shopping_goal": "string — restate the goal you were given, in your own words",
  "objects": [
    {
      "object_id": "string — must match the photo label given to you, e.g. obj_001",
      "proposed_type": "string — the category/type you assign this object",
      "properties": {
        "<property_name>": "<value, or the literal string 'unknown'>"
      },
      "included_in_description": true,
      "reason_if_excluded": null
    }
  ]
}"""

SHARED_RULES = """Rules stated identically to every variant, to control for prompt-compliance effects:

- Output only this JSON object. No prose before or after it.
- object_id must appear exactly once per photo you were given, in the same order.
- "unknown" may only be used for a property that is genuinely not visible or
  inferable from the photo (e.g. a nutrition label facing away from the camera). If a
  property can be reasonably inferred from what is visible (e.g. a product clearly
  labelled "ground beef" implies non-vegan, even if no explicit vegan label is shown), you
  must infer it and briefly justify the inference in a "_note" sibling key rather than
  defaulting to "unknown". This instruction exists because a documented failure mode of
  this exact model family is over-using "unknown" even when a confident inference is
  possible — do not do this.
- included_in_description: false requires a non-null reason_if_excluded."""

def shared_output_schema_block() -> str:
    """The literal {SHARED_OUTPUT_SCHEMA} placeholder each variant prompt
    embeds -- agent_prompts_ABCD.md presents the JSON schema and the rules
    list together under one "Shared output schema" heading, and every
    variant references it as a single placeholder, so both parts are
    substituted together, not the JSON alone."""
    return f"```json\n{SHARED_OUTPUT_SCHEMA}\n```\n\n{SHARED_RULES}"


WORKED_EXAMPLE = """{
  "shopping_goal": "Buy only vegan grocery items",
  "objects": [
    {
      "object_id": "obj_001",
      "proposed_type": "dairy_drink",
      "properties": {
        "vegan": false,
        "_note": "Label reads 'cow's milk', which is never vegan",
        "refrigerated": true,
        "price": 3.50
      },
      "included_in_description": true,
      "reason_if_excluded": null
    }
  ]
}"""
