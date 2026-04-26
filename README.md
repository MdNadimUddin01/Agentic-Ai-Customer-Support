# AI Agent Customer Support System

An intelligent customer support platform powered by AI agents, featuring intent-based routing, multi-agent orchestration, and real-time chat capabilities.

## 🚀 Features

- **Agentic Architecture**: Multiple specialized agents (account, query, technical, escalation)
- **Intent Classification**: Intelligent routing based on customer intent
- **Vector Store & Mini RAG**: Knowledge retrieval and augmented generation
- **Real-time Chat**: WebSocket-powered customer support interface
- **Admin Dashboard**: Customer lookup and support ticket management
- **Authentication**: Secure user and admin authentication
- **Multi-tier Support**: Escalation handling for complex issues

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── config/             # Configuration files
│   ├── src/
│   │   ├── agents/         # AI agents (account, query, technical, escalation)
│   │   ├── api/            # FastAPI routes and middleware
│   │   ├── core/           # Core utilities (database, security, vector store)
│   │   ├── integrations/   # Third-party integrations
│   │   ├── models/         # Database models
│   │   ├── tools/          # Agent tools
│   │   └── utils/          # Utilities and validators
│   ├── tests/              # Test suite
│   ├── scripts/            # Database initialization and seeding
│   └── docs/               # API and deployment docs
│
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── context/        # React context (auth)
│   │   ├── lib/            # Utility functions (API client, storage)
│   │   ├── services/       # API services
│   │   └── pages/          # Page components
│   └── public/             # Static assets
│
└── .gitignore              # Git ignore file
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLAlchemy ORM
- **AI/ML**: Gemini API, Vector embeddings
- **Task Queue**: (Optional) Celery for async tasks
- **Testing**: pytest

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS
- **State Management**: Context API
- **HTTP Client**: Fetch API / Custom API client

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn
- Git

## 🔧 Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment variables:
```bash
# Create .env file in backend/ directory
cp .env.example .env  # or create manually
```

Required environment variables:
```
GEMINI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
```

6. Initialize database:
```bash
python scripts/init_db.py
python scripts/seed_data.py  # Optional: seed sample data
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Configure environment variables:
```bash
# Create .env file in frontend/ directory
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Running the Application

### Start Backend

```bash
# From backend/ directory with venv activated
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend

```bash
# From frontend/ directory
npm run dev
# or
yarn dev
```

Frontend will be available at: `http://127.0.0.1:5173`
Backend API will be available at: `http://127.0.0.1:8000`
API Docs: `http://127.0.0.1:8000/docs`

### Using VS Code Tasks

Pre-configured tasks are available:

```bash
# Backend
task: backend-server-8000
task: backend-health-check

# Frontend
task: dev-frontend or dev-frontend-prefix
task: build-frontend or build-frontend-prefix
```

## 📡 API Routes

See [API Documentation](backend/docs/API.md) for detailed endpoint information.

### Main Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `GET /api/health` - Health check
- `POST /api/chat` - Send message to chat
- `GET /api/admin/customers` - List customers (admin)
- `POST /api/webhook` - Webhook receiver

## 🤖 Agents

The system uses multiple specialized agents:

- **Intent Classifier**: Routes customer requests to appropriate agent
- **Query Agent**: Handles general inquiries
- **Account Agent**: Manages account-related requests
- **Technical Agent**: Resolves technical issues
- **Escalation Agent**: Handles complex issues requiring human intervention

See [Agents Documentation](backend/docs/AGENTS.md) for details.

## 🧪 Testing

```bash
# Run tests
pytest

# Run specific test file
pytest tests/unit/test_agents.py

# Run with coverage
pytest --cov=src tests/
```

## 📦 Building for Production

### Backend
```bash
pip install gunicorn
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
npm run build
```

Production build will be in `frontend/dist/`

## 🐳 Docker Support

Build and run with Docker:
```bash
docker-compose up --build
```

See [Deployment Documentation](backend/docs/DEPLOYMENT.md) for details.

## 📝 Environment Variables

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key_here
DEBUG=False
LOG_LEVEL=INFO
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## 📜 License

MIT License - see LICENSE file for details

## 👥 Support

For issues or questions, please open an issue on GitHub or contact the team.

---

**Built with ❤️ using FastAPI, React, and AI Agents**
