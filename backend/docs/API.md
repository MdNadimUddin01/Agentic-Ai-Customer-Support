# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for development. In production, implement JWT-based authentication.

## Endpoints

### Health Check

**GET** `/api/health`

Check API and database health.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development"
}
```

---

### Chat

**POST** `/api/chat`

Send a message to the AI support system.

**Request Body:**
```json
{
  "message": "I can't login to my account",
  "customer_id": "cust_12345",
  "channel": "web",
  "conversation_id": "conv_abc123def456",
  "industry": "saas"
}
```

**Parameters:**
- `message` (required): User message (1-5000 characters)
- `customer_id` (required): Customer identifier
- `channel` (optional): Communication channel (web, whatsapp, api). Default: "web"
- `conversation_id` (optional): Existing conversation ID. If not provided, creates new conversation
- `industry` (optional): Industry context (saas, ecommerce, telecom). Default: "saas"

**Response:**
```json
{
  "response": "I'll help you with that login issue. Let me verify your account status...",
  "conversation_id": "conv_abc123def456",
  "timestamp": "2026-04-08T10:30:00Z",
  "agent_type": "technical",
  "escalated": false,
  "ticket_id": null
}
```

**Response Fields:**
- `response`: AI agent's response message
- `conversation_id`: Conversation identifier
- `timestamp`: Response timestamp (UTC)
- `agent_type`: Type of agent that handled the request
- `escalated`: Whether issue was escalated to human support
- `ticket_id`: Support ticket ID if escalated

---

### Get Conversation

**GET** `/api/conversation/{conversation_id}`

Retrieve conversation history.

**Path Parameters:**
- `conversation_id`: Conversation identifier

**Response:**
```json
{
  "conversation_id": "conv_abc123def456",
  "customer_id": "cust_12345",
  "channel": "web",
  "industry": "saas",
  "messages": [
    {
      "role": "user",
      "content": "I can't login",
      "timestamp": "2026-04-08T10:30:00Z",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Let me help you...",
      "timestamp": "2026-04-08T10:30:05Z",
      "metadata": {
        "agent_type": "technical",
        "intent": "technical_support"
      }
    }
  ],
  "status": "active",
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T10:30:05Z"
}
```

---

## Admin Endpoints

### Add Knowledge Entry

**POST** `/api/admin/knowledge`

Add entry to knowledge base (creates vector embedding).

**Request Body:**
```json
{
  "content": "Login troubleshooting guide: ...",
  "category": "authentication",
  "industry": "saas"
}
```

**Response:**
```json
{
  "entry_id": "507f1f77bcf86cd799439011",
  "category": "authentication",
  "status": "added"
}
```

---

### List Tickets

**GET** `/api/admin/tickets`

List support tickets with optional filters.

**Query Parameters:**
- `status_filter` (optional): Filter by status (open, assigned, resolved, closed)
- `priority` (optional): Filter by priority (low, medium, high, urgent)
- `limit` (optional): Maximum tickets to return (default: 50, max: 100)

**Response:**
```json
[
  {
    "ticket_id": "T-A1B2C3D4",
    "customer_id": "cust_12345",
    "priority": "high",
    "category": "technical",
    "status": "open",
    "title": "Data export stuck at 50%",
    "created_at": "2026-04-08T10:00:00Z"
  }
]
```

---

### Get Ticket

**GET** `/api/admin/tickets/{ticket_id}`

Get detailed ticket information.

**Response:**
```json
{
  "ticket_id": "T-A1B2C3D4",
  "conversation_id": "conv_abc123def456",
  "customer_id": "cust_12345",
  "priority": "high",
  "category": "technical",
  "title": "Data export stuck",
  "description": "User's data export has been stuck at 50% for 2 hours",
  "agent_summary": "Suggested restart and file size check. Diagnostics show no clear issue.",
  "status": "open",
  "assigned_to": null,
  "created_at": "2026-04-08T10:00:00Z"
}
```

---

### Get Statistics

**GET** `/api/admin/stats`

Get system statistics and metrics.

**Response:**
```json
{
  "conversations": {
    "total": 150,
    "active": 12,
    "escalated": 8
  },
  "tickets": {
    "total": 25,
    "open": 8,
    "resolved": 17
  },
  "metrics": {
    "escalation_rate": 5.33,
    "resolution_rate": 68.0
  },
  "timestamp": "2026-04-08T10:30:00Z"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Rate Limiting

- Default: 100 requests per minute per IP
- Burst: 20 requests per second
- Headers returned:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

---

## Example Usage

### cURL

```bash
# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I cant login to my account",
    "customer_id": "cust_12345",
    "channel": "web"
  }'

# Get conversation
curl http://localhost:8000/api/conversation/conv_abc123def456
```

### Python

```python
import requests

# Send chat message
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "I want to upgrade my plan",
        "customer_id": "cust_12345"
    }
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Agent: {data['agent_type']}")
```

### JavaScript

```javascript
// Send chat message
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "I'm getting a 401 API error",
    customer_id: 'cust_12345'
  })
});

const data = await response.json();
console.log('Response:', data.response);
```

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints.
