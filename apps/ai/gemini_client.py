"""
Shared Gemini client setup and tool-schema conversion.

Both copilot.py (customer) and admin_copilot.py (admin analytics) build a
genai.Client and a Gemini Tool from the same TOOL_DEFINITIONS-style dicts
(JSON-Schema, lowercase types) used elsewhere in the codebase — this module
holds the one place that talks to the google-genai SDK so both copilots
stay in sync.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL = "gemini-flash-latest"

# Gemini's function-calling schema uses uppercase type names (its own
# Type enum), not the lowercase JSON-Schema convention our tools already
# use. Converting explicitly here is safer than relying on the SDK to
# coerce case for us.
_TYPE_MAP = {
    "object": "OBJECT",
    "string": "STRING",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
}


def get_client():
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        return None
    try:
        from google import genai

        return genai.Client(api_key=api_key)
    except ImportError:
        logger.warning("google-genai package not installed")
        return None


def _convert_schema(schema):
    if not isinstance(schema, dict):
        return schema
    converted = dict(schema)
    if "type" in converted:
        converted["type"] = _TYPE_MAP.get(converted["type"], converted["type"])
    if "properties" in converted:
        converted["properties"] = {
            key: _convert_schema(value) for key, value in converted["properties"].items()
        }
    if "items" in converted:
        converted["items"] = _convert_schema(converted["items"])
    if "required" in converted and not converted["required"]:
        converted.pop("required")
    return converted


def build_tool(tool_definitions):
    """Build a single genai Tool with one FunctionDeclaration per entry in
    tool_definitions (each a dict with name/description/parameters)."""
    from google.genai import types

    declarations = [
        types.FunctionDeclaration(
            name=t["name"],
            description=" ".join(t["description"].split()),
            parameters=_convert_schema(t["parameters"]),
        )
        for t in tool_definitions
    ]
    return types.Tool(function_declarations=declarations)
