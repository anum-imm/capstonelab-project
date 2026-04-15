from __future__ import annotations

import re
from enum import Enum
from typing import Iterable

from pydantic import BaseModel, Field, field_validator


FORBIDDEN_KEYWORDS = {
    "ignore all previous instructions",
    "dan",
    "do anything now",
    "bypass",
    "jailbreak",
    "disable safety",
    "delete database",
    "drop table",
    "rm -rf",
    "exfiltrate",
    "leak credentials",
    "system prompt",
}

SENSITIVE_OUTPUT_PATTERNS = [
    r"[A-Za-z]:\\[^\s]+",  # Windows file paths
    r"/[A-Za-z0-9_\-./]+",  # Unix-like file paths
    r"\b(api[_-]?key|secret|token|password)\b",
    r"\b(metadata|internal[_-]?id|debug[_-]?info)\b",
]


class SafetyLabel(str, Enum):
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"


class PromptValidationInput(BaseModel):
    """Deterministic validation for user prompts."""

    prompt: str = Field(..., min_length=1, max_length=4000)

    @field_validator("prompt")
    @classmethod
    def block_forbidden_keywords(cls, value: str) -> str:
        lowered = value.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in lowered:
                raise ValueError(f"Restricted phrase detected: '{keyword}'")
        return value


def normalize_text(text: str) -> str:
    """Normalize spacing to improve simple matching checks."""
    return re.sub(r"\s+", " ", text.strip())


def deterministic_input_check(prompt: str) -> tuple[SafetyLabel, str]:
    """Fast deterministic safety check using Pydantic + keyword checks."""
    try:
        normalized = normalize_text(prompt)
        PromptValidationInput(prompt=normalized)
        return SafetyLabel.SAFE, "No restricted patterns detected."
    except Exception as exc:  # noqa: BLE001 - safe user-facing reason
        return SafetyLabel.UNSAFE, str(exc)


def sanitize_output_text(text: str, patterns: Iterable[str] | None = None) -> str:
    """
    Remove sensitive patterns from final model output.
    Replaces detected values with [REDACTED].
    """
    rules = list(patterns or SENSITIVE_OUTPUT_PATTERNS)
    sanitized = text
    for pattern in rules:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized
