"""Confidence scoring utilities for Week 6 human-in-the-loop behavior."""
from typing import List, Dict, Any, Optional


UNCERTAINTY_PHRASES = [
    "i don't know",
    "i am not sure",
    "i'm not sure",
    "unable to",
    "cannot",
    "not enough information",
    "please contact support",
    "escalate",
]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def calculate_confidence_score(
    user_message: str,
    response: str,
    intent_label: str,
    agent_type: str,
    rag_results: Optional[List[Dict[str, Any]]] = None,
    agent_confidence_hint: Optional[float] = None,
    found_answer: Optional[bool] = None,
    escalated: bool = False,
) -> float:
    """
    Calculate response confidence score in [0, 1].

    Rule-based scoring to keep behavior deterministic and cheap.
    """
    score = 0.75

    # Prefer explicit model/tool confidence when available
    if agent_confidence_hint is not None:
        score = 0.45 + (0.5 * float(agent_confidence_hint))

    # RAG evidence strength
    results = rag_results or []
    if results:
        top_score = float(results[0].get("score", 0.0))
        if top_score >= 0.8:
            score += 0.12
        elif top_score >= 0.6:
            score += 0.07
        elif top_score < 0.35:
            score -= 0.08
    else:
        score -= 0.1

    # Query success signal
    if found_answer is False:
        score -= 0.2
    elif found_answer is True:
        score += 0.05

    # Linguistic uncertainty in response
    response_l = (response or "").lower()
    if any(phrase in response_l for phrase in UNCERTAINTY_PHRASES):
        score -= 0.18

    # Intent-based prior
    if intent_label in {"complaint", "payment_issue"}:
        score -= 0.08
    elif intent_label == "greeting":
        score += 0.08

    # Escalated outcomes are low-confidence by nature
    if escalated:
        score -= 0.22

    # Very short answers to complex user messages are lower confidence
    if len((user_message or "").strip()) > 100 and len((response or "").strip()) < 60:
        score -= 0.1

    return round(_clamp(score), 3)
