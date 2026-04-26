# Frontend - AI Customer Support System

React + Vite frontend integrated with the FastAPI backend.

## Features

- Landing page with product overview
- Agentic chat UI connected to `/api/chat`
- Backend health awareness via `/api/health`
- Admin dashboard using `/api/admin/stats`

## Prerequisites

- Node.js 18+
- Backend running on `http://127.0.0.1:8000`

## Setup

```bash
npm install
```

Create local env file:

```bash
cp .env.example .env
```

If you run backend on a different host/port, update `VITE_API_BASE_URL`.

## Run (development)

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Important Routes

- `/` - Home
- `/chat/cust_001` - Chatbot with seeded customer
- `/admin` - Live backend stats dashboard
