"""OpenAI API client wrapper for circuit generation."""

from __future__ import annotations

import json
import ast
from typing import AsyncIterator

from openai import OpenAI
from pydantic import ValidationError

from src.ai.prompts import build_messages
from src.ai.schemas import CircuitSpec
from src.config import get_settings
from src.utils.logger import get_logger

log = get_logger("ai.client")


class AIClientError(Exception):
    """Raised when the AI client encounters an unrecoverable error."""


class AIClient:
    """Synchronous OpenAI wrapper that returns validated CircuitSpec objects."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        self._api_key = api_key or settings.openai_api_key
        self._model = model or settings.openai_model
        self._max_tokens = settings.openai_max_tokens
        self._temperature = settings.openai_temperature

        if not self._api_key:
            raise AIClientError(
                "OpenAI API key is not configured. "
                "Set OPENAI_API_KEY in your .env file or application settings."
            )

        base_url = settings.openai_base_url.strip() or None
        self._client = OpenAI(api_key=self._api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_circuit(self, description: str, current_spec: CircuitSpec | None = None) -> CircuitSpec:
        """Send a natural-language description and return a validated CircuitSpec.
        
        If current_spec is provided, the AI will iterate on the existing design.
        """
        if not description or not description.strip():
            raise AIClientError("Circuit description cannot be empty.")

        messages = build_messages(description.strip(), current_spec)
        
        mode_label = "Editing" if current_spec else "Generating"
        log.info("%s circuit for: %s", mode_label, description[:120])

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            log.error("OpenAI API error: %s", exc)
            raise AIClientError(f"OpenAI API request failed: {exc}") from exc

        raw = response.choices[0].message.content
        if not raw:
            raise AIClientError("AI returned an empty response.")

        log.debug("Raw AI response length: %d chars", len(raw))
        return self._parse_response(raw)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str) -> CircuitSpec:
        """Parse raw JSON string into a validated CircuitSpec."""
        text = raw.strip()

        # Extract JSON object by finding the outermost braces
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx : end_idx + 1]

        # Try multiple parsing strategies
        # 1. Standard JSON with relaxed control character handling
        try:
            data = json.loads(text, strict=False)
            return CircuitSpec.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            pass

        # 2. Fallback to ast.literal_eval for non-standard JSON (e.g. single quotes, trailing commas)
        try:
            # Note: ast.literal_eval does not handle 'null', 'true', 'false'
            # We try it as-is first for single-quote/trailing-comma cases
            data = ast.literal_eval(text)
            if isinstance(data, dict):
                return CircuitSpec.model_validate(data)
        except (ValueError, SyntaxError, ValidationError):
            pass

        # 3. Attempt a "pythonized" parse for cases with trailing commas AND null/true/false
        try:
            # This is risky but can save some AI responses
            # Replace common JSON keywords with Python equivalents
            # Use a simple approach that avoids replacing text inside quotes if possible
            # but for a fallback, we take the risk.
            import re
            pythonized = re.sub(r'\bnull\b', 'None', text)
            pythonized = re.sub(r'\btrue\b', 'True', pythonized)
            pythonized = re.sub(r'\bfalse\b', 'False', pythonized)
            data = ast.literal_eval(pythonized)
            if isinstance(data, dict):
                return CircuitSpec.model_validate(data)
        except (ValueError, SyntaxError, ValidationError):
            pass

        # If all else fails, log the failing text for debugging and raise
        log.error("All AI JSON parsing strategies failed. Raw text: %s", text)
        raise AIClientError(f"AI response is not valid JSON and could not be recovered: {text[:100]}...")
