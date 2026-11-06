from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b")
CASE_ID_RE = re.compile(r"\bCASE-\d+\b", re.IGNORECASE)

PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "override previous instructions",
    "system prompt",
    "developer prompt",
    "act as",
    "you are now",
    "do not follow",
    "bypass policy",
    "approve immediately",
    "ignore the rules",
    "ignore the policy",
    "reset your instructions",
    "reveal hidden instructions",
    "never mention this",
    "do not mention this",
)


def redact_pii(text: str) -> str:
    """Mask common personal and case identifiers before the model sees them."""
    redacted = text
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = SSN_RE.sub("[REDACTED_SSN]", redacted)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    redacted = CASE_ID_RE.sub("[REDACTED_CASE_ID]", redacted)
    return redacted


def detect_prompt_injection(text: str) -> bool:
    """Flag document text that tries to override instructions or system behavior."""
    lowered = text.lower()
    return any(pattern in lowered for pattern in PROMPT_INJECTION_PATTERNS)
