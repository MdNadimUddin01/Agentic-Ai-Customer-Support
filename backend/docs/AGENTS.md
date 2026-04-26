# Agent Architecture Guide

## Overview

The AI Customer Support System uses a multi-agent architecture built on LangChain, where specialized agents handle different types of customer requests.

## Architecture Diagram

```
User Message
     ↓
Orchestrator Agent (Intent Classification)
     ↓
┌────────┴────────┬────────────┬─────────────┐
│                 │            │             │
Technical Agent   Account      Query       Escalation
                  Agent        Agent       Agent
     ↓               ↓            ↓             ↓
   Tools          Tools        Tools         Ticket
(Knowledge,    (Subscription,  (Knowledge,   Generation
Diagnostic)     Billing)       Search)
```

## Agent Types

### 1. Orchestrator Agent

**Purpose:** Routes incoming messages to the appropriate specialized agent.

**How it works:**
1. Receives user message
2. Analyzes message content and conversation history
3. Classifies intent using LLM
4. Routes to specialized agent

**Intent Categories:**
- `technical_support`: Login issues, errors, bugs, API problems
- `account_management`: Subscriptions, billing, plan changes
- `order_tracking`: Order status, shipping (e-commerce)
- `payment_issues`: Failed payments, refunds
- `general_query`: General questions, how-to queries

**Configuration:**
- Temperature: 0.3 (low for consistent classification)
- No tools (classification only)

**Example:**
```python
from src.agents.orchestrator import orchestrator

intent = orchestrator.classify_intent(
    message="I can't login to my account",
    industry="saas"
)
# Returns: IntentCategory.TECHNICAL_SUPPORT

agent_type = orchestrator.route_to_agent(intent)
# Returns: AgentType.TECHNICAL
```

---

### 2. Technical Agent

**Purpose:** Handle technical issues, troubleshooting, and support.

**Available Tools:**
- `search_knowledge_base`: Search documentation for solutions
- `verify_account`: Check account status
- `run_diagnostic`: Execute diagnostic checks
- `check_service_status`: Verify system health
- `create_ticket`: Escalate to human support

**Workflow:**
1. Receive technical issue description
2. Search knowledge base for relevant solutions
3. If needed, run diagnostics
4. Provide step-by-step guidance
5. Escalate if confidence low or max attempts reached

**Escalation Logic:**
- Escalates after 3 attempts
- Escalates if confidence < threshold (0.6)
- Auto-escalates for critical keywords (data loss, security breach)

**Example:**
```python
from src.agents.technical_agent import TechnicalAgent
from src.tools import KnowledgeSearchTool, RunDiagnosticTool

agent = TechnicalAgent(tools=[
    KnowledgeSearchTool(industry="saas"),
    RunDiagnosticTool()
])

result = agent.handle_issue(
    message="I'm getting a 401 error from the API",
    customer_id="cust_123",
    industry="saas"
)

print(result["response"])
print(f"Should escalate: {result['should_escalate']}")
print(f"Confidence: {result['confidence']}")
```

**Configuration:**
- Temperature: 0.7
- Max Iterations: 5
- Escalation Threshold: 3 attempts

---

### 3. Account Agent

**Purpose:** Manage subscriptions, billing, and account settings.

**Available Tools:**
- `get_subscription`: Retrieve subscription details
- `update_subscription`: Change plan (upgrade/downgrade)
- `check_billing`: View billing history
- `verify_account`: Check account configuration
- `create_ticket`: Escalate complex issues

**Workflow:**
1. Receive account-related request
2. Fetch current subscription/billing info
3. For changes: confirm with user before executing
4. Execute approved changes
5. Confirm completion

**Confirmation Required For:**
- Plan upgrades/downgrades
- Cancellations
- Payment method updates
- Account deletions

**Example:**
```python
from src.agents.account_agent import AccountAgent

agent = AccountAgent(tools=[
    GetSubscriptionTool(),
    UpdateSubscriptionTool()
])

result = agent.handle_request(
    message="I want to upgrade to Pro plan",
    customer_id="cust_123"
)

print(f"Response: {result['response']}")
print(f"Requires confirmation: {result['requires_confirmation']}")
print(f"Action taken: {result['action_taken']}")
```

**Configuration:**
- Temperature: 0.5 (moderate for account operations)
- Max Iterations: 5

---

### 4. Query Agent

**Purpose:** Answer general questions using knowledge base (RAG).

**Available Tools:**
- `search_knowledge_base`: Semantic search over documentation
- `create_ticket`: Escalate if answer not found

**Workflow:**
1. Receive question
2. Search knowledge base using vector similarity
3. Retrieve top-k relevant documents
4. Generate answer based on retrieved context
5. If no relevant docs found, escalate

**RAG (Retrieval Augmented Generation):**
- Uses sentence-transformers for embeddings
- Cosine similarity matching
- Top-5 results by default
- Minimum relevance score: 0.7

**Example:**
```python
from src.agents.query_agent import QueryAgent

agent = QueryAgent(tools=[KnowledgeSearchTool()])

result = agent.answer_query(
    message="How do I export my data?",
    customer_id="cust_123",
    industry="saas"
)

print(result["response"])
print(f"Found answer: {result['found_answer']}")
print(f"Sources: {result['sources']}")
```

**Configuration:**
- Temperature: 0.7
- Vector Search Top-K: 5

---

### 5. Escalation Agent

**Purpose:** Create support tickets when AI cannot resolve issues.

**Triggered When:**
- Agent cannot resolve after max attempts
- User explicitly requests human agent
- Confidence score below threshold
- Critical issues (security, data loss)
- High-value transactions

**Workflow:**
1. Collect issue details
2. Determine priority based on keywords and context
3. Categorize issue (technical, billing, etc.)
4. Generate ticket with:
   - Issue description
   - What AI agent tried
   - Customer context
   - Priority level
5. Notify customer with ticket ID and expected response time

**Priority Levels:**
- **Urgent** (60 min response): Service outage, data loss, security
- **High** (2 hour response): Can't access account, payment failures
- **Medium** (4 hour response): General technical issues
- **Low** (8 hour response): General inquiries

**Example:**
```python
from src.agents.escalation_agent import EscalationAgent
from src.core.constants import TicketCategory

agent = EscalationAgent()

result = agent.create_ticket(
    conversation_id="conv_123",
    customer_id="cust_123",
    issue_description="Data export stuck at 50% for 2 hours",
    agent_attempts="Suggested restart. Ran diagnostics. No clear issue found.",
    category=TicketCategory.TECHNICAL,
    industry="saas"
)

print(f"Ticket ID: {result['ticket_id']}")
print(f"Priority: {result['priority']}")
print(result['message'])  # Customer-facing message
```

---

## Agent Memory

All agents inherit memory management from `BaseAgent`:

**Short-term Memory:**
- Uses LangChain `ConversationBufferWindowMemory`
- Stores last 10 messages
- Provides context for current conversation

**Long-term Memory:**
- Full conversation history in MongoDB
- Retrievable for context in future conversations

**Example:**
```python
# Load conversation history into agent
agent.load_memory_from_conversation(messages=[
    {"role": "user", "content": "I need help"},
    {"role": "assistant", "content": "How can I assist?"}
])

# Clear memory
agent.clear_memory()
```

---

## Tools

### Knowledge Search Tool

RAG-based semantic search over documentation.

```python
tool = KnowledgeSearchTool(industry="saas")
result = tool.execute(query="login issues", category="authentication")
```

### Account Tools

```python
# Get subscription
tool = GetSubscriptionTool()
result = tool.execute(customer_id="cust_123")

# Update subscription
tool = UpdateSubscriptionTool()
result = tool.execute(customer_id="cust_123", new_plan="pro")
```

### Diagnostic Tools

```python
# Run diagnostic
tool = RunDiagnosticTool()
result = tool.execute(issue_type="login")

# Check service status
tool = CheckServiceStatusTool()
result = tool.execute(service_name="api")
```

---

## Adding New Agents

To create a new specialized agent:

1. **Inherit from BaseAgent:**
```python
from src.agents.base_agent import BaseAgent
from src.core.constants import AgentType

class MyCustomAgent(BaseAgent):
    def __init__(self, tools=None):
        super().__init__(
            agent_type=AgentType.CUSTOM,
            tools=tools or [],
            temperature=0.7
        )

    def get_system_prompt(self, **kwargs):
        return "You are a custom agent that..."
```

2. **Add to orchestrator routing:**
```python
# In orchestrator.py
routing_map = {
    IntentCategory.MY_NEW_INTENT: AgentType.CUSTOM,
    ...
}
```

3. **Create tools for the agent:**
```python
from src.tools.base_tool import BaseSupportTool

class MyCustomTool(BaseSupportTool):
    name = "my_tool"
    description = "Does something specific"

    def execute(self, **kwargs):
        # Tool logic here
        return "Result"
```

---

## Configuration

Agent behavior can be configured in `config/settings.py`:

```python
# Agent settings
MAX_AGENT_ITERATIONS = 5
AGENT_TIMEOUT = 30
ESCALATION_CONFIDENCE_THRESHOLD = 0.6
MAX_CONVERSATION_HISTORY = 10

# Gemini configuration
GEMINI_MODEL = "gemini-1.5-pro"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 2048
```

Industry-specific rules in `config/industry_configs.py`:

```python
ESCALATION_RULES = {
    "saas": {
        "auto_escalate_keywords": [...],
        "escalate_after_attempts": 3,
        "escalate_if_confidence_below": 0.6
    }
}
```

---

## Best Practices

1. **Tool Selection:** Give agents only relevant tools
2. **Prompt Engineering:** Clear, specific system prompts
3. **Escalation:** Don't hesitate to escalate complex issues
4. **Memory Management:** Clear memory for new conversations
5. **Testing:** Test agents with various edge cases
6. **Monitoring:** Track success rate, escalation rate, response times

---

## Troubleshooting

**Agent not using tools:**
- Verify tool is in agent's tools list
- Check tool description is clear
- Ensure LLM has sufficient context

**High escalation rate:**
- Review knowledge base coverage
- Adjust confidence thresholds
- Improve agent prompts

**Slow responses:**
- Reduce max iterations
- Optimize tool execution
- Cache frequent queries
