# MitchellSoftware — Portfolio + AI Chatbot

Full-stack portfolio site for Jason Mitchell featuring an interactive 3D lumber yard demo, AI recruiter chatbot, and real-time analytics.

## Project Structure

```
MitchellSoftware/
├── client/                  # Frontend (served by Flask)
│   ├── index.html           # Portfolio page
│   ├── styles.css           # Portfolio styles
│   ├── script.js            # Portfolio logic + analytics
│   ├── chat.js              # AI chatbot client
│   └── demo/                # Interactive demos
│       ├── pallet-builder.html
│       ├── pallet-builder.css
│       └── pallet-builder.js
│
├── server/                  # Flask backend
│   ├── app.py               # Main server — routes, PDF gen, chat API
│   └── requirements.txt     # Python dependencies
│
├── ai/                      # AI chatbot module
│   ├── __init__.py
│   ├── prompt.py            # System prompt builder
│   └── jason_profile.json   # Structured profile data
│
├── tests/                   # Test suites
│   ├── server/              # Server tests
│   └── ai/                  # AI module tests
│
├── render.yaml              # Render.com deployment config
├── DEPLOYMENT.md            # Deployment guide
└── README.md                # ← you are here
```

## Features

- **Portfolio** — Dark terminal-themed site with creative/professional mode toggle, typing animations, whiteboard overlay, and Prometheus analytics dashboard.
- **Lumber Yard Restock Planner** — 3D demo built with Three.js r128. Browse/flag bunks, generate PDF delivery orders with flatbed loading diagrams.
- **AI Recruiter Chatbot** — Floating chat bubble powered by OpenAI. Recruiters enter their name, optionally paste a job posting, and ask questions about Jason's experience. Includes safety guardrails, anti-jailbreak protections, and rate limiting (10 msg/min per IP).
- **Admin Dashboard** — Token-protected endpoints for viewing chat logs and conversation stats.
- **Real-Time Analytics** — Prometheus counters/gauges for page views, PDF generations, contact submissions, uptime, memory, and active sessions. Stats auto-refresh every 30 seconds.
- **CI/CD Pipeline** — GitHub Actions workflow runs 25 tests, validates imports, then triggers Render deploy via webhook.

## Quick Start

```bash
# 1. Install dependencies
pip install -r server/requirements.txt

# 2. Set environment variables
export OPENAI_API_KEY="sk-..."
export ADMIN_TOKEN="your-secret-token"

# 3. Run the server
python -m server.app
```

Open `http://localhost:5000/` for the portfolio, or `http://localhost:5000/demo` for the lumber yard demo.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for the chatbot |
| `ADMIN_TOKEN` | Yes | Secret token for `/admin/*` routes |
| `FLASK_ENV` | No | Set to `production` on Render |
| `OPENAI_MODEL` | No | LLM model name (default: `gpt-4o-mini`) |
| `PORT` | No | Server port (default: `5000`) |
| `CHAT_DB_DIR` | No | Persistent storage path for chat logs (default: project root) |

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

25 tests covering health/static routes, metrics, event tracking, chat validation, admin auth, rate limiting, AI prompt loading, and profile schema validation.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Portfolio page |
| `/demo` | GET | Lumber Yard Restock Planner |
| `/api/chat` | POST | AI chatbot messages |
| `/api/track` | POST | Analytics event tracking |
| `/api/stats` | GET | Live analytics stats |
| `/generate-pdf` | POST | PDF restock order generation |
| `/metrics` | GET | Prometheus metrics |
| `/admin/chat-logs?token=…` | GET | View all conversations |
| `/admin/chat-stats?token=…` | GET | Conversation statistics |
| `/health` | GET | Health check |

## Deployment

Deployed on **Render.com** as a single web service. 

## Tech Stack

**Frontend:** Vanilla JS, Three.js r128, CSS3, EmailJS  
**Backend:** Python, Flask, ReportLab, Prometheus  
**AI:** OpenAI API (gpt-4o-mini), SQLite  
**Deployment:** Render.com
