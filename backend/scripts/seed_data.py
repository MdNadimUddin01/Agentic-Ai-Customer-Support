"""
Sample data seeding script.

Seeds the database with:
- SaaS knowledge base entries
- Sample customers
- Sample subscriptions
- Sample orders
- Sample conversations
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import logger
from src.core.database import connect_db, disconnect_db, get_collection
from src.core.constants import (
    COLLECTION_KNOWLEDGE_BASE,
    COLLECTION_CUSTOMERS,
    COLLECTION_SUBSCRIPTIONS,
    COLLECTION_CONVERSATIONS,
    COLLECTION_ORDERS,
    COLLECTION_TICKETS,
)
from src.core.vector_store import vector_store
from src.core.security import hash_password
from src.models.customer import Customer, Subscription
from src.models.conversation import Conversation
from src.models.order import Order
from src.models.ticket import Ticket
from config.industry_configs import Priority
from src.core.constants import (
    SubscriptionPlan,
    SubscriptionStatus,
    Channel,
    MessageRole,
    ConversationStatus,
    OrderStatus,
    PaymentStatus,
    TicketCategory,
    TicketStatus,
)


# SaaS Knowledge Base Content
KNOWLEDGE_BASE_ENTRIES = [
    # Authentication
    {
        "content": """
Login Issues - Invalid Credentials:
If you're seeing an 'invalid credentials' error, try these steps:
1. Verify you're using the correct email address
2. Check if Caps Lock is on
3. Try resetting your password using the 'Forgot Password' link
4. Clear your browser cache and cookies
5. Try logging in using an incognito/private window
6. If you recently changed your password, make sure you're using the new one

If none of these work, your account may be locked due to multiple failed attempts. Wait 15 minutes and try again, or contact support.
        """,
        "category": "authentication",
        "industry": "saas"
    },
    {
        "content": """
Two-Factor Authentication (2FA) Setup:
To enable 2FA for enhanced security:
1. Go to Settings > Security
2. Click 'Enable Two-Factor Authentication'
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code from your app
5. Save your backup codes in a secure location

To disable 2FA, go to Settings > Security > Disable 2FA (requires password confirmation).
        """,
        "category": "authentication",
        "industry": "saas"
    },
    {
        "content": """
Password Reset Instructions:
1. Click 'Forgot Password' on the login page
2. Enter your email address
3. Check your inbox for the reset link (check spam folder)
4. Click the link (valid for 1 hour)
5. Enter your new password (min 8 characters, must include uppercase, lowercase, and number)
6. Confirm your new password
7. You'll be automatically logged in

If you don't receive the email within 5 minutes, check that you're using the correct email address registered with your account.
        """,
        "category": "authentication",
        "industry": "saas"
    },
    # API Integration
    {
        "content": """
API Authentication - 401 Unauthorized Error:
A 401 error means your authentication failed. Common causes:

1. Missing Authorization Header:
   - Include: Authorization: Bearer YOUR_API_KEY
   - Not: Authorization: YOUR_API_KEY (missing 'Bearer')

2. Invalid API Key:
   - Check your API key in Settings > API Keys
   - Keys are case-sensitive
   - Ensure no extra spaces

3. Expired API Key:
   - API keys expire after 90 days
   - Rotate keys regularly for security

4. Incorrect API Endpoint:
   - Use: https://api.yourservice.com/v1/
   - Not: https://yourservice.com/api/ (wrong URL)

Test your API key:
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.yourservice.com/v1/test
        """,
        "category": "api_integration",
        "industry": "saas"
    },
    {
        "content": """
API Rate Limits:
Our API has the following rate limits by plan:

Free: 1,000 requests/day, 10 requests/minute
Basic: 10,000 requests/day, 100 requests/minute
Pro: 100,000 requests/day, 1,000 requests/minute
Enterprise: Custom limits

Rate limit headers in responses:
- X-RateLimit-Limit: Your limit
- X-RateLimit-Remaining: Requests remaining
- X-RateLimit-Reset: Time when limit resets (Unix timestamp)

When rate limited (429 error):
- Wait for the reset time
- Implement exponential backoff
- Cache responses when possible
- Batch requests to reduce API calls

To request higher limits, contact support or upgrade your plan.
        """,
        "category": "api_integration",
        "industry": "saas"
    },
    # Billing
    {
        "content": """
Subscription Plans and Pricing:

FREE Plan (₹0/month):
- 1 user
- 1,000 API calls/month
- 1GB storage
- Email support
- Basic features

BASIC Plan (₹29/month):
- 5 users
- 10,000 API calls/month
- 10GB storage
- Email support
- Standard features
- API access

PRO Plan (₹99/month):
- Unlimited users
- 100,000 API calls/month
- 100GB storage
- Priority email + chat support
- Advanced features
- Webhooks
- Custom integrations

ENTERPRISE Plan (Custom):
- Unlimited everything
- Dedicated support
- SLA guarantee
- Custom features
- On-premise option
- Training included

Annual billing: Save 20% (2 months free)
        """,
        "category": "billing",
        "industry": "saas"
    },
    {
        "content": """
Updating Payment Method:
1. Log in to your account
2. Go to Settings > Billing
3. Click 'Update Payment Method'
4. Enter new card details (we accept Visa, Mastercard, Amex, Discover)
5. Click 'Save'

Your new payment method will be used for the next billing cycle. We don't charge until your next renewal date.

Failed Payment Recovery:
If your payment fails:
- We'll retry automatically after 3 days, 5 days, and 7 days
- You'll receive email notifications
- Update your payment method to avoid service interruption
- After 7 days, your account may be suspended

To avoid payment failures, ensure:
- Card has sufficient funds
- Card hasn't expired
- Billing address matches your bank records
        """,
        "category": "billing",
        "industry": "saas"
    },
    # Account Management
    {
        "content": """
Upgrading Your Subscription:
To upgrade your plan:
1. Go to Settings > Subscription
2. Click 'Upgrade Plan'
3. Select your desired plan (Basic, Pro, or Enterprise)
4. Review the new features and pricing
5. Click 'Confirm Upgrade'

Changes take effect immediately:
- New features activated instantly
- Prorated charge for the remaining billing period
- Next invoice reflects the new price
- No data migration needed

Downgrading:
- Changes take effect at next billing cycle
- You keep current features until then
- May need to reduce users/storage to fit new plan limits
- No refunds for partial periods
        """,
        "category": "account_management",
        "industry": "saas"
    },
    {
        "content": """
Canceling Your Subscription:
To cancel:
1. Go to Settings > Subscription
2. Click 'Cancel Subscription'
3. Select a reason (helps us improve)
4. Confirm cancellation

What happens after cancellation:
- You keep access until the end of your billing period
- No refunds for remaining time
- Your data is retained for 30 days
- You can reactivate anytime within 30 days
- After 30 days, data is permanently deleted (per our data retention policy)

Export your data before canceling:
- Go to Settings > Data Export
- Select 'Export All Data'
- Receive download link via email

We're sad to see you go! Contact support if we can help resolve any issues.
        """,
        "category": "account_management",
        "industry": "saas"
    },
    # Data Export
    {
        "content": """
Data Export Guide:
To export your data:
1. Go to Settings > Data Export
2. Select data type:
   - All Data (complete export)
   - Specific records (date range, filters)
3. Choose format: CSV, JSON, or XML
4. Click 'Start Export'

Export process:
- Small exports (< 100MB): Ready in seconds
- Large exports (> 100MB): Processed in background
- Email notification when ready
- Download link valid for 7 days

Export limits:
- Free: 1 export/week, max 100MB
- Basic: 5 exports/week, max 500MB
- Pro: Unlimited exports, max 5GB per export
- Enterprise: No limits

Common issues:
- Export stuck: Try smaller date range
- Too large: Filter data or export in chunks
- Timeout: Large exports need time; wait for email
        """,
        "category": "data_export",
        "industry": "saas"
    },
    # Troubleshooting
    {
        "content": """
Common Error Messages and Solutions:

500 Internal Server Error:
- Temporary server issue
- Try again in a few minutes
- If persists, contact support with request ID

403 Forbidden:
- Your account lacks permissions
- Admin needs to grant access
- Check if your subscription includes this feature

404 Not Found:
- Resource doesn't exist or was deleted
- Check the URL/ID
- May have been moved or renamed

429 Too Many Requests:
- You've hit rate limits
- Wait before making more requests
- Implement exponential backoff

504 Gateway Timeout:
- Request took too long
- Try simplifying your query
- Break large operations into smaller chunks
        """,
        "category": "troubleshooting",
        "industry": "saas"
    },
    # Features
    {
        "content": """
Team Collaboration Features:

User Management:
- Invite team members via Settings > Team
- Assign roles: Admin, Member, Viewer
- Admins can manage billing and settings
- Members have full access to features
- Viewers have read-only access

Sharing and Permissions:
- Share projects with specific team members
- Set permissions: Can Edit, Can View, Can Comment
- Real-time collaboration on documents
- Activity log shows who changed what

Notifications:
- Customize what notifications you receive
- Email, in-app, or both
- Set quiet hours (no notifications)
- Get notified when:
  * Someone mentions you
  * Changes to items you're watching
  * Important system updates
        """,
        "category": "features",
        "industry": "saas"
    },
    {
        "content": """
Product Catalog (SaaS Add-ons):

AI Analytics Add-on:
- Price: ₹19/month
- Includes anomaly detection and weekly insights emails
- Available on Basic, Pro, and Enterprise plans

Priority Support Add-on:
- Price: ₹49/month
- Includes 24/7 live chat and 2-hour SLA response
- Available on Pro and Enterprise plans only

Advanced API Pack:
- Price: ₹29/month
- Includes webhook retries, event replay, and higher throughput
- Best for integration-heavy teams
        """,
        "category": "product_catalog",
        "industry": "saas"
    },
    {
        "content": """
SaaS Feature Availability by Plan:

FREE:
- Basic dashboard
- 1 workspace
- Community support

BASIC:
- Everything in Free
- API access
- Team members up to 5

PRO:
- Everything in Basic
- Webhooks
- SSO login
- Priority support option

ENTERPRISE:
- Everything in Pro
- Dedicated account manager
- Custom SLA
- Audit logs and advanced compliance
        """,
        "category": "product_catalog",
        "industry": "saas"
    }
]


# Sample Customers
SAMPLE_CUSTOMERS = [
    {
        "customer_id": "cust_001",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1234567890",
        "seed_password": "Pass@1234",
        "industry": "saas",
        "preferences": {"notification_email": True}
    },
    {
        "customer_id": "cust_002",
        "name": "Sarah Johnson",
        "email": "sarah.j@techcorp.com",
        "phone": "+1234567891",
        "seed_password": "Pass@1234",
        "industry": "saas",
        "preferences": {"notification_email": True}
    },
    {
        "customer_id": "cust_003",
        "name": "Mike Davis",
        "email": "mike.davis@startup.io",
        "phone": "+1234567892",
        "seed_password": "Pass@1234",
        "industry": "saas",
        "preferences": {"notification_email": False}
    },
    {
        "customer_id": "cust_qa_001",
        "name": "QA Tester",
        "email": "qa.tester@example.com",
        "phone": "+1234567999",
        "seed_password": "QaTest@123",
        "industry": "saas",
        "preferences": {"notification_email": True},
        "metadata": {"role": "qa", "purpose": "llm-testing"}
    },
    {
        "customer_id": "cust_004",
        "name": "Priya Patel",
        "email": "priya.patel@scaleops.ai",
        "phone": "+1234567893",
        "seed_password": "Pass@1234",
        "industry": "saas",
        "preferences": {"notification_email": True, "weekly_report": True},
        "metadata": {"segment": "enterprise", "company": "ScaleOps AI"}
    },
    {
        "customer_id": "cust_005",
        "name": "Luis Romero",
        "email": "luis.romero@growthstack.io",
        "phone": "+1234567894",
        "seed_password": "Pass@1234",
        "industry": "saas",
        "preferences": {"notification_email": True, "sms_alerts": False},
        "metadata": {"segment": "growth", "company": "GrowthStack"}
    }
]


# Sample Subscriptions
SAMPLE_SUBSCRIPTIONS = [
    {
        "customer_id": "cust_001",
        "plan": SubscriptionPlan.BASIC,
        "status": SubscriptionStatus.ACTIVE,
        "start_date": datetime.utcnow() - timedelta(days=60),
        "renewal_date": datetime.utcnow() + timedelta(days=30),
        "monthly_price": 29.00,
        "features": {
            "users": 5,
            "storage_gb": 10,
            "api_calls": 10000
        }
    },
    {
        "customer_id": "cust_002",
        "plan": SubscriptionPlan.PRO,
        "status": SubscriptionStatus.ACTIVE,
        "start_date": datetime.utcnow() - timedelta(days=120),
        "renewal_date": datetime.utcnow() + timedelta(days=10),
        "monthly_price": 99.00,
        "features": {
            "users": -1,  # unlimited
            "storage_gb": 100,
            "api_calls": 100000
        }
    },
    {
        "customer_id": "cust_003",
        "plan": SubscriptionPlan.FREE,
        "status": SubscriptionStatus.ACTIVE,
        "start_date": datetime.utcnow() - timedelta(days=30),
        "monthly_price": 0.00,
        "features": {
            "users": 1,
            "storage_gb": 1,
            "api_calls": 1000
        }
    },
    {
        "customer_id": "cust_qa_001",
        "plan": SubscriptionPlan.PRO,
        "status": SubscriptionStatus.ACTIVE,
        "start_date": datetime.utcnow() - timedelta(days=14),
        "renewal_date": datetime.utcnow() + timedelta(days=16),
        "monthly_price": 99.00,
        "features": {
            "users": 25,
            "storage_gb": 100,
            "api_calls": 100000
        },
        "usage": {
            "api_calls_used": 18240,
            "storage_used_gb": 22
        }
    },
    {
        "customer_id": "cust_004",
        "plan": SubscriptionPlan.ENTERPRISE,
        "status": SubscriptionStatus.ACTIVE,
        "start_date": datetime.utcnow() - timedelta(days=240),
        "renewal_date": datetime.utcnow() + timedelta(days=20),
        "monthly_price": 499.00,
        "features": {
            "users": -1,
            "storage_gb": 1000,
            "api_calls": 1000000,
            "sla": "99.95%"
        },
        "usage": {
            "api_calls_used": 712340,
            "storage_used_gb": 418
        }
    },
    {
        "customer_id": "cust_005",
        "plan": SubscriptionPlan.BASIC,
        "status": SubscriptionStatus.TRIAL,
        "start_date": datetime.utcnow() - timedelta(days=5),
        "renewal_date": datetime.utcnow() + timedelta(days=9),
        "monthly_price": 29.00,
        "features": {
            "users": 5,
            "storage_gb": 10,
            "api_calls": 10000
        },
        "usage": {
            "api_calls_used": 840,
            "storage_used_gb": 1.3
        }
    }
]


# Sample Orders (for end-to-end and prompt testing)
SAMPLE_ORDERS = [
    {
        "order_id": "ORD-10001",
        "customer_id": "cust_001",
        "items": [
            {"product_id": "addon-analytics", "name": "AI Analytics Add-on", "quantity": 1, "price": 19.0}
        ],
        "subtotal": 19.0,
        "tax": 1.9,
        "shipping": 0.0,
        "total": 20.9,
        "status": OrderStatus.DELIVERED,
        "payment_status": PaymentStatus.COMPLETED,
        "tracking_number": "TRK-10001",
        "courier": "FedEx",
        "notes": "Digital activation completed"
    },
    {
        "order_id": "ORD-10002",
        "customer_id": "cust_002",
        "items": [
            {"product_id": "addon-priority-support", "name": "Priority Support Add-on", "quantity": 1, "price": 49.0}
        ],
        "subtotal": 49.0,
        "tax": 4.9,
        "shipping": 0.0,
        "total": 53.9,
        "status": OrderStatus.SHIPPED,
        "payment_status": PaymentStatus.COMPLETED,
        "tracking_number": "TRK-10002",
        "courier": "UPS",
        "notes": "Provisioning in progress"
    },
    {
        "order_id": "ORD-10003",
        "customer_id": "cust_qa_001",
        "items": [
            {"product_id": "addon-api-pack", "name": "Advanced API Pack", "quantity": 1, "price": 29.0}
        ],
        "subtotal": 29.0,
        "tax": 2.9,
        "shipping": 0.0,
        "total": 31.9,
        "status": OrderStatus.PROCESSING,
        "payment_status": PaymentStatus.PROCESSING,
        "tracking_number": "TRK-10003",
        "courier": "DHL",
        "notes": "QA test order for chatbot scenarios"
    },
    {
        "order_id": "ORD-10004",
        "customer_id": "cust_004",
        "items": [
            {"product_id": "security-review", "name": "Security Review Package", "quantity": 1, "price": 149.0}
        ],
        "subtotal": 149.0,
        "tax": 14.9,
        "shipping": 0.0,
        "total": 163.9,
        "status": OrderStatus.DELIVERED,
        "payment_status": PaymentStatus.COMPLETED,
        "tracking_number": "TRK-10004",
        "courier": "FedEx",
        "notes": "Enterprise enablement package delivered"
    },
    {
        "order_id": "ORD-10005",
        "customer_id": "cust_005",
        "items": [
            {"product_id": "onboarding-setup", "name": "White-glove Onboarding", "quantity": 1, "price": 79.0}
        ],
        "subtotal": 79.0,
        "tax": 7.9,
        "shipping": 0.0,
        "total": 86.9,
        "status": OrderStatus.CANCELLED,
        "payment_status": PaymentStatus.REFUNDED,
        "tracking_number": "TRK-10005",
        "courier": "UPS",
        "notes": "Cancelled during trial evaluation; refunded in full"
    }
]


SAMPLE_CONVERSATIONS = [
    {
        "conversation_id": "conv_demo_login_001",
        "customer_id": "cust_001",
        "channel": Channel.WEB,
        "status": ConversationStatus.RESOLVED,
        "created_at": datetime.utcnow() - timedelta(days=3, hours=5),
        "updated_at": datetime.utcnow() - timedelta(days=3, hours=5, minutes=-12),
        "context": {
            "seed_source": "demo_seed",
            "topic": "login_reset",
            "sentiment": "frustrated"
        },
        "messages": [
            (MessageRole.USER, "I can't login to my account. It says invalid credentials even after resetting my password."),
            (MessageRole.ASSISTANT, "I can help with that. Please confirm whether you changed your password in the last hour."),
            (MessageRole.USER, "Yes, I changed it about 10 minutes ago."),
            (MessageRole.ASSISTANT, "Thanks — the reset can take a few minutes to sync. Please try again in an incognito window using the new password."),
        ],
    },
    {
        "conversation_id": "conv_demo_api_002",
        "customer_id": "cust_002",
        "channel": Channel.API,
        "status": ConversationStatus.ESCALATED,
        "created_at": datetime.utcnow() - timedelta(hours=14),
        "updated_at": datetime.utcnow() - timedelta(hours=13, minutes=25),
        "context": {
            "seed_source": "demo_seed",
            "topic": "api_outage",
            "sentiment": "urgent"
        },
        "messages": [
            (MessageRole.USER, "Our production API calls are failing with 401 and 503 errors intermittently."),
            (MessageRole.ASSISTANT, "I found authentication guidance, but the 503 errors suggest a deeper incident. I'm escalating this to engineering."),
        ],
    },
    {
        "conversation_id": "conv_demo_billing_003",
        "customer_id": "cust_004",
        "channel": Channel.WEB,
        "status": ConversationStatus.ESCALATED,
        "created_at": datetime.utcnow() - timedelta(days=1, hours=4),
        "updated_at": datetime.utcnow() - timedelta(days=1, hours=3, minutes=40),
        "context": {
            "seed_source": "demo_seed",
            "topic": "invoice_dispute",
            "sentiment": "concerned"
        },
        "messages": [
            (MessageRole.USER, "We were charged twice for our enterprise renewal and need this fixed today."),
            (MessageRole.ASSISTANT, "I understand the urgency. I'm creating a billing escalation so our finance team can review the duplicate charge immediately."),
        ],
    },
    {
        "conversation_id": "conv_demo_order_004",
        "customer_id": "cust_qa_001",
        "channel": Channel.WEB,
        "status": ConversationStatus.ACTIVE,
        "created_at": datetime.utcnow() - timedelta(hours=6),
        "updated_at": datetime.utcnow() - timedelta(hours=5, minutes=45),
        "context": {
            "seed_source": "demo_seed",
            "topic": "order_tracking",
            "sentiment": "neutral"
        },
        "messages": [
            (MessageRole.USER, "Can you check where my Advanced API Pack order is right now?"),
            (MessageRole.ASSISTANT, "I found your order and it's currently processing. I can also share the tracking details once it ships."),
        ],
    },
]


SAMPLE_TICKETS = [
    {
        "ticket_id": "TKT-DEMO-1001",
        "conversation_id": "conv_demo_api_002",
        "customer_id": "cust_002",
        "priority": Priority.URGENT,
        "category": TicketCategory.TECHNICAL,
        "title": "Production API authentication and outage incident",
        "description": "Enterprise customer reports intermittent 401 and 503 errors from the production API during peak usage.",
        "agent_summary": "AI identified mixed auth and availability symptoms, then escalated to engineering for incident triage.",
        "status": TicketStatus.IN_PROGRESS,
        "assigned_to": "eng_oncall",
        "metadata": {
            "confidence_score": 0.54,
            "source_intent": "technical_support",
            "escalation_reason": "Low confidence combined with outage-like symptoms",
            "demo_seed": True
        },
        "created_at": datetime.utcnow() - timedelta(hours=13, minutes=50),
        "updated_at": datetime.utcnow() - timedelta(hours=13, minutes=10),
    },
    {
        "ticket_id": "TKT-DEMO-1002",
        "conversation_id": "conv_demo_billing_003",
        "customer_id": "cust_004",
        "priority": Priority.HIGH,
        "category": TicketCategory.BILLING,
        "title": "Duplicate enterprise renewal charge",
        "description": "Customer reports being invoiced twice for the same enterprise renewal period.",
        "agent_summary": "AI gathered billing context and routed the case to finance operations due to duplicate-charge risk.",
        "status": TicketStatus.WAITING_CUSTOMER,
        "assigned_to": "finance_ops",
        "metadata": {
            "confidence_score": 0.71,
            "source_intent": "billing_query",
            "escalation_reason": "Duplicate billing requires finance review",
            "demo_seed": True
        },
        "created_at": datetime.utcnow() - timedelta(days=1, hours=3, minutes=55),
        "updated_at": datetime.utcnow() - timedelta(hours=20),
    },
    {
        "ticket_id": "TKT-DEMO-1003",
        "conversation_id": "conv_demo_order_004",
        "customer_id": "cust_qa_001",
        "priority": Priority.MEDIUM,
        "category": TicketCategory.ORDER,
        "title": "QA order tracking verification",
        "description": "Internal QA account is validating order-tracking flows for the Advanced API Pack purchase.",
        "agent_summary": "AI shared the current order state and left the case open for manual verification in the showcase demo.",
        "status": TicketStatus.OPEN,
        "assigned_to": "support_queue",
        "metadata": {
            "confidence_score": 0.88,
            "source_intent": "order_tracking",
            "escalation_reason": "Manual QA validation requested",
            "demo_seed": True
        },
        "created_at": datetime.utcnow() - timedelta(hours=5, minutes=50),
        "updated_at": datetime.utcnow() - timedelta(hours=5, minutes=35),
    },
    {
        "ticket_id": "TKT-DEMO-1004",
        "conversation_id": "conv_demo_login_001",
        "customer_id": "cust_001",
        "priority": Priority.LOW,
        "category": TicketCategory.ACCOUNT,
        "title": "Password reset sync delay",
        "description": "Customer needed help after a password reset did not take effect immediately across sessions.",
        "agent_summary": "AI resolved the issue with browser/session troubleshooting and documented the fix for QA.",
        "status": TicketStatus.RESOLVED,
        "assigned_to": "support_triage",
        "resolution": "Password reset completed successfully after session refresh and retry in a private window.",
        "metadata": {
            "confidence_score": 0.93,
            "source_intent": "account_management",
            "escalation_reason": "Tracked for demo completeness",
            "demo_seed": True
        },
        "created_at": datetime.utcnow() - timedelta(days=3, hours=5),
        "updated_at": datetime.utcnow() - timedelta(days=3, hours=4, minutes=48),
        "resolved_at": datetime.utcnow() - timedelta(days=3, hours=4, minutes=48),
    },
]


def seed_knowledge_base():
    """Seed knowledge base with sample entries."""
    logger.info("Seeding knowledge base...")

    vector_store.delete_documents({"metadata.source": "seed_script"})

    count = 0
    for entry in KNOWLEDGE_BASE_ENTRIES:
        vector_store.add_document(
            content=entry["content"].strip(),
            metadata={
                "category": entry["category"],
                "industry": entry["industry"],
                "source": "seed_script"
            }
        )
        count += 1

    logger.info(f"✓ Added {count} knowledge base entries")


def seed_customers():
    """Seed sample customers."""
    logger.info("Seeding customers...")

    customers_coll = get_collection(COLLECTION_CUSTOMERS)

    count = 0
    for cust_data in SAMPLE_CUSTOMERS:
        payload = dict(cust_data)
        seed_password = payload.pop("seed_password")
        payload["password_hash"] = hash_password(seed_password)
        customer = Customer(**payload)
        customers_coll.update_one(
            {"customer_id": customer.customer_id},
            {"$set": customer.to_dict()},
            upsert=True
        )
        count += 1

    logger.info(f"✓ Added {count} customers")


def seed_subscriptions():
    """Seed sample subscriptions."""
    logger.info("Seeding subscriptions...")

    subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)

    count = 0
    for sub_data in SAMPLE_SUBSCRIPTIONS:
        subscription = Subscription(**sub_data)
        subscriptions_coll.update_one(
            {"customer_id": subscription.customer_id},
            {"$set": subscription.to_dict()},
            upsert=True
        )
        count += 1

    logger.info(f"✓ Added {count} subscriptions")


def seed_orders():
    """Seed sample orders."""
    logger.info("Seeding sample orders...")

    orders_coll = get_collection(COLLECTION_ORDERS)

    count = 0
    for order_data in SAMPLE_ORDERS:
        order = Order(**order_data)
        orders_coll.update_one(
            {"order_id": order.order_id},
            {"$set": order.to_dict()},
            upsert=True
        )
        count += 1

    logger.info(f"✓ Added {count} orders")


def seed_conversations():
    """Seed sample conversations."""
    logger.info("Seeding sample conversations...")

    conversations_coll = get_collection(COLLECTION_CONVERSATIONS)

    count = 0
    for conversation_data in SAMPLE_CONVERSATIONS:
        conversation = Conversation(
            conversation_id=conversation_data["conversation_id"],
            customer_id=conversation_data["customer_id"],
            channel=conversation_data["channel"],
            industry="saas",
            context=conversation_data.get("context", {}),
            status=conversation_data["status"],
            created_at=conversation_data["created_at"],
            updated_at=conversation_data["updated_at"],
        )

        for role, content in conversation_data["messages"]:
            conversation.add_message(role, content)

        conversation.status = conversation_data["status"]
        conversation.updated_at = conversation_data["updated_at"]

        conversations_coll.update_one(
            {"conversation_id": conversation.conversation_id},
            {"$set": conversation.to_dict()},
            upsert=True,
        )
        count += 1

    logger.info(f"✓ Added {count} sample conversations")


def seed_tickets():
    """Seed sample tickets for the admin dashboard showcase."""
    logger.info("Seeding support tickets...")

    tickets_coll = get_collection(COLLECTION_TICKETS)

    count = 0
    for ticket_data in SAMPLE_TICKETS:
        ticket = Ticket(**ticket_data)
        tickets_coll.update_one(
            {"ticket_id": ticket.ticket_id},
            {"$set": ticket.to_dict()},
            upsert=True,
        )
        count += 1

    logger.info(f"✓ Added {count} support tickets")


def main():
    """Main seeding function."""
    logger.info("=" * 60)
    logger.info("AI Customer Support System - Data Seeding")
    logger.info("=" * 60)
    logger.info("")

    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        connect_db()
        logger.info("✓ Connected")
        logger.info("")

        # Seed data
        seed_knowledge_base()
        seed_customers()
        seed_subscriptions()
        seed_orders()
        seed_conversations()
        seed_tickets()

        logger.info("")
        logger.info("=" * 60)
        logger.info("Data seeding completed successfully!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Sample data added:")
        logger.info(f"- Knowledge base: {len(KNOWLEDGE_BASE_ENTRIES)} SaaS support articles")
        logger.info(f"- Customers: {len(SAMPLE_CUSTOMERS)} sample customers")
        logger.info(f"- Subscriptions: {len(SAMPLE_SUBSCRIPTIONS)} active subscriptions")
        logger.info(f"- Orders: {len(SAMPLE_ORDERS)} sample orders")
        logger.info(f"- Conversations: {len(SAMPLE_CONVERSATIONS)} sample conversations")
        logger.info(f"- Tickets: {len(SAMPLE_TICKETS)} support tickets")
        logger.info("")
        logger.info("Test login accounts:")
        logger.info("- john.smith@example.com / Pass@1234")
        logger.info("- sarah.j@techcorp.com / Pass@1234")
        logger.info("- mike.davis@startup.io / Pass@1234")
        logger.info("- qa.tester@example.com / QaTest@123")
        logger.info("- priya.patel@scaleops.ai / Pass@1234")
        logger.info("- luis.romero@growthstack.io / Pass@1234")
        logger.info("")
        logger.info("You can now start the API server:")
        logger.info("uvicorn src.api.main:app --reload")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        disconnect_db()


if __name__ == "__main__":
    main()
