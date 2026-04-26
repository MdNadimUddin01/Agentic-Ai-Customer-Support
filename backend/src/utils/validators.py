"""Input validation utilities."""
import re
from typing import Optional
from src.core.exceptions import ValidationException


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationException(f"Invalid email format: {email}")
    return True


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

    if not cleaned.isdigit() or len(cleaned) < 10:
        raise ValidationException(f"Invalid phone number format: {phone}")
    return True


def validate_customer_id(customer_id: str) -> bool:
    """
    Validate customer ID format.

    Args:
        customer_id: Customer ID

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    if not customer_id or len(customer_id) < 5:
        raise ValidationException(f"Invalid customer ID: {customer_id}")
    return True


def validate_order_id(order_id: str) -> bool:
    """
    Validate order ID format.

    Args:
        order_id: Order ID

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    if not order_id or len(order_id) < 5:
        raise ValidationException(f"Invalid order ID: {order_id}")
    return True


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    Sanitize user input.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Raises:
        ValidationException: If input is invalid
    """
    if not text or not text.strip():
        raise ValidationException("Input cannot be empty")

    # Remove excessive whitespace
    sanitized = " ".join(text.split())

    # Check length
    if len(sanitized) > max_length:
        raise ValidationException(f"Input too long (max {max_length} characters)")

    return sanitized


def validate_industry(industry: str) -> bool:
    """
    Validate industry type.

    Args:
        industry: Industry name

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    valid_industries = ["ecommerce", "saas", "telecom"]
    if industry.lower() not in valid_industries:
        raise ValidationException(
            f"Invalid industry: {industry}. Must be one of {valid_industries}"
        )
    return True
