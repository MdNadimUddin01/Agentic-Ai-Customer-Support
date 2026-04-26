# AI-Powered Customer Support System

An enterprise-grade agentic AI customer support system built with LangChain, Google Gemini, and MongoDB. The system autonomously resolves complex customer issues across SaaS, e-commerce, and telecom industries.

## Features

- **Intelligent Agent Framework**: LangChain agents with specialized capabilities
- **Multi-Industry Support**: SaaS (primary), e-commerce, telecom
- **Autonomous Resolution**: Handles technical troubleshooting, account management, order tracking
- **Smart Escalation**: Automatic ticket generation when human intervention needed
- **Multi-Channel**: WhatsApp, Web Chat, REST API
- **Vector Search**: Semantic search over knowledge base using MongoDB
- **Conversation Memory**: Context-aware responses with Redis caching

## Architecture

```
Multi-Channel Layer (WhatsApp, Web, API)
        ↓
Agent Orchestrator (Intent Classification & Routing)
        ↓
Specialized Agents (Technical, Account, Order, Payment, Escalation)
        ↓
Agent Tools (Knowledge Search, CRM, Payments, Shipping, Tickets)
        ↓
MongoDB (Data + Vector Store) + Redis (Cache)
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **AI Framework**: LangChain 0.1.x, Google Gemini
- **Database**: MongoDB 7.0+ (with vector search)
- **Cache**: Redis 7.2+
- **Embeddings**: Sentence Transformers
- **Integrations**: Twilio (WhatsApp), Stripe, Mock APIs

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Google Gemini API key

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd nadim-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Start Infrastructure

```bash
# Start MongoDB and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database initialization
python scripts/init_db.py

# Seed sample data
python scripts/seed_data.py
```

### 5. Run the Application

```bash
# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Project Structure

```
nadim-project/
├── config/              # Configuration files
├── src/
│   ├── core/           # Database, vector store, utilities
│   ├── agents/         # LangChain agents
│   ├── tools/          # Agent tools
│   ├── integrations/   # External service integrations
│   ├── models/         # Data models
│   ├── api/            # FastAPI application
│   └── utils/          # Helper utilities
├── tests/              # Test suite
├── scripts/            # Database scripts
├── docs/               # Documentation
└── docker-compose.yml  # Docker services
```

## Usage Examples

### Web Chat API

```bash
# Send a message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I cant login to my account",
    "customer_id": "cust_12345",
    "channel": "web"
  }'
```

### Sample Conversations

**Technical Support:**
```
User: "I'm getting a 401 error when calling your API"
Agent: → Searches knowledge base
      → Finds authentication docs
      → Provides solution with correct header format
```

**Account Management:**
```
User: "I want to upgrade to Pro plan"
Agent: → Retrieves current subscription
      → Shows Pro plan details
      → Processes upgrade
      → Confirms changes
```

**Escalation:**
```
User: "My data export has been stuck for 2 hours"
Agent: → Attempts basic troubleshooting
      → Runs diagnostics
      → Cannot resolve → Creates ticket
      → Notifies support team
```

## Configuration

Key environment variables (see `.env.example`):

- `GOOGLE_API_KEY`: Your Gemini API key
- `MONGODB_URI`: MongoDB connection string
- `REDIS_HOST`: Redis host
- `ENABLE_WHATSAPP`: Enable WhatsApp integration
- `ENABLE_REAL_INTEGRATIONS`: Use real vs mock APIs

## Development

```bash
# Run tests
pytest tests/ -v --cov=src

# Code formatting
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## Documentation

- [API Documentation](docs/API.md)
- [Agent Architecture](docs/AGENTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Industry-Specific Features

### SaaS (Primary Focus)
- Technical troubleshooting with RAG
- API integration support
- Account and subscription management
- Billing queries

### E-commerce
- Order tracking
- Payment recovery
- Shipping status

### Telecom
- Service status checks
- Plan management
- Billing support

## Monitoring

The system logs all interactions and provides metrics:

- Agent success rate
- Escalation rate
- Average resolution time
- Response times

Logs are available in `logs/` directory.

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
