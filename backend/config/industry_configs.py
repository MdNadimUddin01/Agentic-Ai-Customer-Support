"""
Industry-specific configurations and business rules.
"""
from typing import Dict, List, Any
from enum import Enum


class Industry(str, Enum):
    """Supported industries."""
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    TELECOM = "telecom"


class Priority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Industry-specific escalation rules
ESCALATION_RULES: Dict[str, Dict[str, Any]] = {
    "saas": {
        "auto_escalate_keywords": [
            "data loss",
            "security breach",
            "can't access account",
            "payment not processing",
            "downtime",
            "outage"
        ],
        "high_priority_issues": [
            "api down",
            "login broken",
            "billing error",
            "data export failed"
        ],
        "escalate_after_attempts": 3,
        "escalate_if_confidence_below": 0.6,
        "urgent_response_time_minutes": 60,
        "high_value_threshold": 1000,  # Dollar amount for high-value customers
    },
    "ecommerce": {
        "auto_escalate_keywords": [
            "wrong item",
            "damaged goods",
            "refund",
            "fraud",
            "chargeback"
        ],
        "high_priority_issues": [
            "payment failed",
            "order not received",
            "missing items"
        ],
        "escalate_after_attempts": 3,
        "escalate_if_confidence_below": 0.7,
        "urgent_response_time_minutes": 120,
        "high_value_threshold": 500,
    },
    "telecom": {
        "auto_escalate_keywords": [
            "no service",
            "network down",
            "billing error",
            "unauthorized charges",
            "port number"
        ],
        "high_priority_issues": [
            "service outage",
            "billing dispute",
            "number porting"
        ],
        "escalate_after_attempts": 2,
        "escalate_if_confidence_below": 0.65,
        "urgent_response_time_minutes": 90,
        "high_value_threshold": 200,
    }
}


# Agent intent classification for routing
INTENT_CATEGORIES: Dict[str, List[str]] = {
    "technical_support": [
        "can't login",
        "not working",
        "error",
        "broken",
        "bug",
        "integration issue",
        "api problem",
        "connection failed",
        "timeout",
        "crash"
    ],
    "account_management": [
        "subscription",
        "plan",
        "upgrade",
        "downgrade",
        "cancel",
        "billing",
        "invoice",
        "payment method",
        "account settings"
    ],
    "order_tracking": [
        "where is my order",
        "track order",
        "shipping status",
        "delivery",
        "tracking number",
        "when will it arrive"
    ],
    "payment_issues": [
        "payment failed",
        "card declined",
        "refund",
        "charge",
        "transaction",
        "payment not processed"
    ],
    "general_query": [
        "how do i",
        "what is",
        "tell me about",
        "explain",
        "help with",
        "information about"
    ]
}


# SaaS-specific knowledge base categories
SAAS_KNOWLEDGE_CATEGORIES = [
    "authentication",
    "api_integration",
    "billing",
    "account_management",
    "features",
    "troubleshooting",
    "security",
    "performance",
    "data_export",
    "integrations"
]


# Response templates for common scenarios
RESPONSE_TEMPLATES: Dict[str, str] = {
    "greeting": "Hello! I'm your AI support assistant. How can I help you today?",
    "escalation": "I've created a support ticket (#{ticket_id}) for your issue. Our team will contact you within {response_time} minutes.",
    "resolved": "Great! I'm glad I could help resolve your issue. Is there anything else I can assist you with?",
    "not_understood": "I'm not sure I understand. Could you please provide more details about your issue?",
    "working_on_it": "I'm looking into this for you. One moment please...",
    "need_info": "To help you better, I need some additional information: {info_needed}",
}


def get_industry_config(industry: str) -> Dict[str, Any]:
    """Get configuration for specific industry."""
    return ESCALATION_RULES.get(industry, ESCALATION_RULES["saas"])


def should_escalate(
    industry: str,
    message: str,
    attempts: int,
    confidence: float
) -> tuple[bool, str]:
    """
    Determine if issue should be escalated.

    Returns:
        tuple: (should_escalate, reason)
    """
    config = get_industry_config(industry)

    # Check for auto-escalate keywords
    message_lower = message.lower()
    for keyword in config["auto_escalate_keywords"]:
        if keyword in message_lower:
            return True, f"Auto-escalate keyword detected: {keyword}"

    # Check attempt count
    if attempts >= config["escalate_after_attempts"]:
        return True, f"Max attempts reached: {attempts}"

    # Check confidence threshold
    if confidence < config["escalate_if_confidence_below"]:
        return True, f"Low confidence: {confidence:.2f}"

    return False, ""


def get_priority(industry: str, message: str) -> Priority:
    """Determine ticket priority based on content."""
    config = get_industry_config(industry)
    message_lower = message.lower()

    # Check for urgent keywords
    for keyword in config["auto_escalate_keywords"]:
        if keyword in message_lower:
            return Priority.URGENT

    # Check for high priority issues
    for issue in config["high_priority_issues"]:
        if issue in message_lower:
            return Priority.HIGH

    return Priority.MEDIUM
