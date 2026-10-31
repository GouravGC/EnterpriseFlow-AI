"""Lightweight deterministic input/output guardrails for EnterpriseFlow AI.

These checks are defense-in-depth, not a complete prompt-injection detector.
"""

import re

from pydantic import BaseModel, Field, ValidationError


class InputGuardrailError(ValueError):
    """Raised when a request violates an input safety rule."""


class OutputGuardrailError(ValueError):
    """Raised when generated text fails output validation."""


class GuardrailedOutput(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)


_INJECTION_PATTERNS = (
    re.compile(
        r"\b(ignore|disregard|bypass)\b.{0,60}"
        r"\b(previous|prior|system|developer)\b.{0,30}"
        r"\b(instruction|prompt|rule)s?\b",
        re.I,
    ),
    re.compile(
        r"\b(reveal|print|show|repeat|expose)\b.{0,50}"
        r"\b(system prompt|developer message|hidden instruction)s?\b",
        re.I,
    ),
    re.compile(
        r"\b(you are now|act as|pretend to be)\b.{0,50}"
        r"\b(unrestricted|jailbreak|DAN)\b",
        re.I,
    ),
    re.compile(r"<\s*\|\s*(system|assistant)\s*\|\s*>", re.I),
)


def validate_user_question(question: str) -> str:
    """Normalize and reject obvious instruction-override attempts."""
    if not isinstance(question, str):
        raise InputGuardrailError("Question must be plain text.")

    normalized = question.strip()

    if len(normalized) < 3:
        raise InputGuardrailError(
            "Question must contain at least 3 characters."
        )

    if len(normalized) > 2000:
        raise InputGuardrailError(
            "Question exceeds the 2,000-character limit."
        )

    if any(
        pattern.search(normalized)
        for pattern in _INJECTION_PATTERNS
    ):
        raise InputGuardrailError(
            "The question contains an instruction-override pattern. "
            "Please ask a task-focused question instead."
        )

    return normalized


def validate_generated_answer(answer: str) -> str:
    """Validate model output shape and enforce a bounded response size."""
    try:
        validated = GuardrailedOutput(
            answer=answer.strip() if isinstance(answer, str) else ""
        )
    except (ValidationError, AttributeError) as exc:
        raise OutputGuardrailError(
            "The generated answer did not pass output validation."
        ) from exc

    return validated.answer