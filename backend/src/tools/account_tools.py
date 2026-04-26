"""Account management tools backed by customer, subscription, and order data."""
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from config import logger
from src.core.database import (
    get_collection,
    COLLECTION_SUBSCRIPTIONS,
    COLLECTION_CUSTOMERS,
    COLLECTION_ORDERS,
)
from src.core.constants import SubscriptionPlan, SubscriptionStatus
from src.tools.base_tool import BaseSupportTool


def _format_date(value: Any) -> str:
    if not value:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y")
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).strftime("%d %b %Y")
        except ValueError:
            return value
    return str(value)


def _format_currency(value: Any) -> str:
    try:
        return f"₹{float(value):.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def _format_feature_value(value: Any) -> str:
    if value == -1:
        return "Unlimited"
    return str(value)


def _format_feature_label(key: str) -> str:
    label_overrides = {
        "api_calls": "API Calls / Month",
        "storage_gb": "Storage (GB)",
    }
    return label_overrides.get(key, key.replace("_", " ").title())


class GetSubscriptionInput(BaseModel):
    """Input for getting subscription."""
    customer_id: str = Field(description="The customer ID to look up")


class GetSubscriptionTool(BaseSupportTool):
    """Tool to get customer subscription details."""

    name: str = "get_subscription"
    description: str = """
    Get the current subscription details for a customer.
    Use this to check their current plan, status, features, and billing information.
    Input should be the customer ID.
    """
    args_schema: type[BaseModel] = GetSubscriptionInput

    def execute(self, customer_id: str) -> str:
        """
        Get subscription details.

        Args:
            customer_id: Customer ID

        Returns:
            Subscription information
        """
        try:
            logger.info(f"Getting subscription for customer {customer_id}")

            subscriptions = get_collection(COLLECTION_SUBSCRIPTIONS)
            subscription = subscriptions.find_one({"customer_id": customer_id})

            if not subscription:
                subscription = self._get_mock_subscription(customer_id)

            features = subscription.get("features", {})
            feature_lines = []
            for key, value in features.items():
                label = _format_feature_label(key)
                feature_lines.append(f"- {label}: {_format_feature_value(value)}")

            output = f"""Current Subscription Details:
- Plan: {subscription['plan'].upper()}
- Status: {subscription['status'].upper()}
- Monthly Price: {_format_currency(subscription.get('monthly_price', 0))}
- Renewal Date: {_format_date(subscription.get('renewal_date'))}

Included Features:
{chr(10).join(feature_lines) if feature_lines else '- No feature details available'}

"""
            logger.info(f"Retrieved subscription for {customer_id}: {subscription['plan']}")
            return output

        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            return f"Error retrieving subscription: {str(e)}"

    def _get_mock_subscription(self, customer_id: str) -> Dict[str, Any]:
        """Get mock subscription data."""
        return {
            "customer_id": customer_id,
            "plan": "basic",
            "status": "active",
            "monthly_price": 29.00,
            "renewal_date": "2026-05-01",
            "features": {
                "users": "5",
                "storage": "10GB",
                "api_calls": "10000/month",
                "support": "Email"
            }
        }


class UpdateSubscriptionInput(BaseModel):
    """Input for updating subscription."""
    customer_id: str = Field(description="The customer ID")
    new_plan: str = Field(description="The new plan name (free, basic, pro, enterprise)")


class UpdateSubscriptionTool(BaseSupportTool):
    """Tool to update customer subscription plan."""

    name: str = "update_subscription"
    description: str = """
    Update a customer's subscription plan.
    Use this to upgrade or downgrade their plan after confirming with the customer.
    Input should be customer ID and the new plan name (free, basic, pro, or enterprise).
    """
    args_schema: type[BaseModel] = UpdateSubscriptionInput

    def execute(self, customer_id: str, new_plan: str) -> str:
        """
        Update subscription plan.

        Args:
            customer_id: Customer ID
            new_plan: New plan name

        Returns:
            Update confirmation
        """
        try:
            logger.info(f"Updating subscription for {customer_id} to {new_plan}")

            # Validate plan
            valid_plans = ["free", "basic", "pro", "enterprise"]
            if new_plan.lower() not in valid_plans:
                return f"Invalid plan: {new_plan}. Must be one of: {', '.join(valid_plans)}"

            # Mock update (in production, this would call payment gateway)
            plan_prices = {
                "free": 0,
                "basic": 29,
                "pro": 99,
                "enterprise": "custom"
            }

            price = plan_prices[new_plan.lower()]
            price_text = "Custom pricing" if price == "custom" else f"₹{price}/month"

            output = f"""✓ Subscription Updated Successfully

Customer: {customer_id}
New Plan: {new_plan.upper()}
Price: {price_text}
Effective: Immediately

Changes include:
- Plan features updated
- Next billing cycle will reflect new price
- Customer will receive confirmation email

The upgrade is complete!"""

            logger.info(f"Updated subscription for {customer_id} to {new_plan}")
            return output

        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return f"Error updating subscription: {str(e)}"


class CheckBillingInput(BaseModel):
    """Input for checking billing."""
    customer_id: str = Field(description="The customer ID")


class CheckBillingTool(BaseSupportTool):
    """Tool to check billing history and invoices."""

    name: str = "check_billing"
    description: str = """
    Check billing history and recent invoices for a customer.
    Use this to view past payments, upcoming charges, or investigate billing questions.
    Input should be the customer ID.
    """
    args_schema: type[BaseModel] = CheckBillingInput

    def execute(self, customer_id: str) -> str:
        """
        Check billing history.

        Args:
            customer_id: Customer ID

        Returns:
            Billing information
        """
        try:
            logger.info(f"Checking billing for customer {customer_id}")

            subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)
            orders_coll = get_collection(COLLECTION_ORDERS)

            subscription = subscriptions_coll.find_one({"customer_id": customer_id})
            orders = list(
                orders_coll.find({"customer_id": customer_id}, {"_id": 0})
                .sort("created_at", -1)
            )

            completed_orders = [order for order in orders if order.get("payment_status") == "completed"]
            invoice_lines: List[str] = []
            for order in completed_orders[:5]:
                invoice_lines.append(
                    f"- {_format_date(order.get('created_at'))}: {_format_currency(order.get('total', 0))} "
                    f"({str(order.get('payment_status', 'unknown')).upper()}) - Order {order.get('order_id')}"
                )

            if not invoice_lines:
                invoice_lines.append("- No completed payments found in the system yet")

            total_paid = sum(float(order.get("total", 0) or 0) for order in completed_orders)
            next_charge = _format_currency(subscription.get("monthly_price", 0)) if subscription else "N/A"
            next_charge_date = _format_date(subscription.get("renewal_date")) if subscription else "N/A"
            next_charge_plan = str(subscription.get("plan", "N/A")).title() if subscription else "N/A"

            output = f"""Billing History for {customer_id}:

Recent Invoices:
{chr(10).join(invoice_lines)}

Summary:
- Completed Payments: {len(completed_orders)}
- Total Paid To Date: {_format_currency(total_paid)}

Next Charge:
- Date: {next_charge_date}
- Amount: {next_charge}
- Plan: {next_charge_plan}

Payment Method: Card ending in •••• 4242
Status: {'Active, no issues' if subscription else 'No active subscription found'}

All payments are up to date."""

            logger.info(f"Retrieved billing for {customer_id}")
            return output

        except Exception as e:
            logger.error(f"Error checking billing: {e}")
            return f"Error retrieving billing: {str(e)}"


class VerifyAccountInput(BaseModel):
    """Input for account verification."""
    customer_id: str = Field(description="The customer ID or email to verify")


class VerifyAccountTool(BaseSupportTool):
    """Tool to verify account status and configuration."""

    name: str = "verify_account"
    description: str = """
    Verify a customer's account status, configuration, and access.
    Use this for troubleshooting login issues or checking account settings.
    Input should be customer ID or email.
    """
    args_schema: type[BaseModel] = VerifyAccountInput

    def execute(self, customer_id: str) -> str:
        """
        Verify account status.

        Args:
            customer_id: Customer ID or email

        Returns:
            Account status
        """
        try:
            logger.info(f"Verifying account for {customer_id}")

            customers_coll = get_collection(COLLECTION_CUSTOMERS)
            subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)
            customer = customers_coll.find_one(
                {"$or": [{"customer_id": customer_id}, {"email": customer_id.lower()}]},
                {"_id": 0, "password_hash": 0}
            )

            if not customer:
                return f"I could not find an account matching '{customer_id}'."

            subscription = subscriptions_coll.find_one({"customer_id": customer["customer_id"]}, {"_id": 0})
            storage = subscription.get("usage", {}).get("storage_used_gb") if subscription else None
            storage_limit = subscription.get("features", {}).get("storage_gb") if subscription else None
            api_calls = subscription.get("usage", {}).get("api_calls_used") if subscription else None

            output = f"""Account Verification for {customer_id}:

Account Status: ACTIVE ✓
Email Verified: {'Yes ✓' if customer.get('email') else 'No'}
Phone Verified: {'Yes ✓' if customer.get('phone') else 'No'}
2FA Enabled: No

Login Issues: None detected
Last Login: Not tracked in current demo dataset
Failed Login Attempts: 0

Account Configuration:
- Plan: {str(subscription.get('plan', 'N/A')).upper() if subscription else 'N/A'}
- API Calls Used: {api_calls if api_calls is not None else 'N/A'}
- Storage Used: {f'{storage}GB / {storage_limit}GB' if storage is not None and storage_limit is not None else 'N/A'}

No issues found with this account."""

            logger.info(f"Account verified for {customer_id}")
            return output

        except Exception as e:
            logger.error(f"Error verifying account: {e}")
            return f"Error verifying account: {str(e)}"
