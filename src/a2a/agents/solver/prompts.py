"""Prompts integration for the solver agent.

This module shows how to call the model and post-process its textual output
using the jsonfy utility. It deliberately does NOT ask the model to emit JSON;
instead it asks for a textual explanation which is parsed and normalized.

Adapt the call_model(...) function to your project's model API.
"""
from typing import Any
from co_tutor.utils.jsonfy import jsonfy, validate_and_normalize
import logging

logger = logging.getLogger(__name__)


def call_model(prompt: str, **kwargs) -> str:
    """Placeholder for the project's model invocation.

    Replace this with the actual model call (OpenAI, local LLM, etc.) that
    returns the model's textual response.
    """
    # Example placeholder; in real code call your LLM and return its text.
    raise NotImplementedError("Replace call_model with actual model invocation")


def process_model_response(model_response_text: str) -> dict:
    """Take a model textual response and convert it to the normalized JSON schema.

    Raises ValueError on failure to parse/validate.
    """
    try:
        parsed = jsonfy(model_response_text)
    except ValueError as e:
        logger.error("jsonfy failed: %s", e)
        raise

    try:
        normalized = validate_and_normalize(parsed)
    except ValueError as e:
        logger.error("Validation failed: %s", e)
        raise

    return normalized


# Example higher level usage:
# def run_solver(question: str):
#     prompt = build_prompt(question)  # explain the desired format in plain text
#     text = call_model(prompt)
#     return process_model_response(text)
