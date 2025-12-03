"""
Custom guardrails for HEARTSIGHT RAG + chat flows.

This module implements:
- Input validation (PII redaction + prompt injection heuristics)
- Output moderation (block medication dosages / unsafe advice, basic toxicity filter)
- Structured logging of guardrail events
- Optional integration with Prometheus metrics (if available)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict


logger = logging.getLogger("heartsight.guardrails")


try:  # Optional Prometheus integration
    from src.monitoring.prometheus_metrics import record_guardrail_event
except Exception:  # pragma: no cover - metrics are optional

    def record_guardrail_event(*args, **kwargs):  # type: ignore[no-redef]
        return None


# -------------------------------------------------------------------
# Data models
# -------------------------------------------------------------------


@dataclass
class GuardrailEvent:
    """Structured event describing a guardrail decision."""

    stage: str  # "input" or "output"
    rule: str
    severity: str  # "info" | "warning" | "blocking"
    message: str
    original_text_sample: str
    sanitized_text_sample: str
    endpoint: Optional[str] = None


@dataclass
class GuardrailResult:
    """Result returned from guardrail checks."""

    text: str
    events: List[GuardrailEvent]


# -------------------------------------------------------------------
# Core guardrail engine
# -------------------------------------------------------------------


PII_PATTERNS = [
    # Very simple patient-name style patterns
    re.compile(
        r"(patient\s*name\s*:\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", re.IGNORECASE
    ),
    re.compile(r"(mr\.|mrs\.|ms\.)\s+[A-Z][a-z]+", re.IGNORECASE),
]

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore (all )?previous instructions", re.IGNORECASE),
    re.compile(r"disregard the above", re.IGNORECASE),
    re.compile(r"you are now (?:an?|the)", re.IGNORECASE),
    re.compile(r"act as (?:an?|the)", re.IGNORECASE),
]

DOSAGE_PATTERN = re.compile(
    r"\b(?:take|give|administer)\s+\d+\s*(?:mg|milligram|mcg|g)\b.*",
    re.IGNORECASE,
)

TOXICITY_KEYWORDS = [
    "idiot",
    "stupid",
    "useless",
    "kill yourself",
]


class GuardrailsEngine:
    """Lightweight policy engine for input validation and output moderation."""

    def __init__(self, endpoint: Optional[str] = None) -> None:
        self.endpoint = endpoint or "unknown"

    # -----------------------------
    # Input Validation
    # -----------------------------
    def validate_input(self, text: str) -> GuardrailResult:
        """Redact obvious PII and detect prompt injection patterns."""

        events: List[GuardrailEvent] = []
        sanitized = text

        # PII redaction (very basic heuristics for names)
        for pattern in PII_PATTERNS:
            match = pattern.search(sanitized)
            if not match:
                continue

            before = sanitized
            sanitized = pattern.sub(r"\1[REDACTED]", sanitized)
            event = GuardrailEvent(
                stage="input",
                rule="pii_redaction",
                severity="warning",
                message="Detected possible patient-identifying information. Redacted.",
                original_text_sample=before[:120],
                sanitized_text_sample=sanitized[:120],
                endpoint=self.endpoint,
            )
            events.append(event)
            self._log_event(event)

        # Prompt-injection heuristics
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(sanitized):
                event = GuardrailEvent(
                    stage="input",
                    rule="prompt_injection_heuristic",
                    severity="warning",
                    message="Detected prompt-injection style instruction in user input.",
                    original_text_sample=sanitized[:120],
                    sanitized_text_sample=sanitized[:120],
                    endpoint=self.endpoint,
                )
                events.append(event)
                self._log_event(event)

        return GuardrailResult(text=sanitized, events=events)

    # -----------------------------
    # Output Moderation
    # -----------------------------
    def moderate_output(self, text: str) -> GuardrailResult:
        """Moderate LLM output for unsafe medical advice / toxicity."""

        events: List[GuardrailEvent] = []
        sanitized = text

        # Block explicit dosage instructions and replace with safe guidance
        dosage_match = DOSAGE_PATTERN.search(sanitized)
        if dosage_match:
            before = sanitized
            # Replace the entire sentence containing the dosage with safe advice
            unsafe_segment = dosage_match.group(0)
            safe_advice = (
                "For any medications or dosages, please consult a cardiologist or your "
                "treating physician for personalized guidance."
            )
            sanitized = sanitized.replace(unsafe_segment, safe_advice)

            event = GuardrailEvent(
                stage="output",
                rule="block_medication_dosage",
                severity="blocking",
                message=(
                    "Blocked explicit medication dosage advice and replaced it with "
                    "safe cardiologist consultation guidance."
                ),
                original_text_sample=before[:200],
                sanitized_text_sample=sanitized[:200],
                endpoint=self.endpoint,
            )
            events.append(event)
            self._log_event(event)

        # Very lightweight toxicity keyword scan
        lowered = sanitized.lower()
        if any(keyword in lowered for keyword in TOXICITY_KEYWORDS):
            before = sanitized
            sanitized = (
                "I'm sorry, but I cannot respond in that way. "
                "Let's focus on helpful, respectful information about your heart health. "
                "Please consult your cardiologist for personalized medical advice."
            )

            event = GuardrailEvent(
                stage="output",
                rule="toxicity_filter",
                severity="blocking",
                message="Detected potentially toxic or abusive language; replaced with safe response.",
                original_text_sample=before[:200],
                sanitized_text_sample=sanitized[:200],
                endpoint=self.endpoint,
            )
            events.append(event)
            self._log_event(event)

        return GuardrailResult(text=sanitized, events=events)

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _log_event(self, event: GuardrailEvent) -> None:
        """Send guardrail events to logs and Prometheus (if available)."""

        log_payload: Dict[str, object] = {
            "event": asdict(event),
            "component": "guardrails",
        }

        if event.severity == "blocking":
            logger.warning("Guardrail blocking event: %s", log_payload)
        else:
            logger.info("Guardrail event: %s", log_payload)

        # Forward to Prometheus if exporter is enabled
        try:
            record_guardrail_event(
                endpoint=event.endpoint or self.endpoint,
                stage=event.stage,
                rule=event.rule,
            )
        except Exception:
            # Metrics are optional; never break request flow
            pass


# -------------------------------------------------------------------
# Convenience helpers (functional style)
# -------------------------------------------------------------------


def apply_guardrails_to_input(text: str, endpoint: str) -> GuardrailResult:
    engine = GuardrailsEngine(endpoint=endpoint)
    return engine.validate_input(text=text)


def apply_guardrails_to_output(text: str, endpoint: str) -> GuardrailResult:
    engine = GuardrailsEngine(endpoint=endpoint)
    return engine.moderate_output(text=text)
