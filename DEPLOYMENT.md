# Deployment Guide — Render.com

This project is deployed as a single **Render Web Service** that serves both the Flask backend and all static frontend files.

## Render Setup

1. Go to [Render Dashboard](https://dashboard.render.com) and connect the GitHub repo.
2. Create a **Web Service** with these settings:

| Setting | Value |
|---|---|
| Name | `lumber-yard-restock-planner` (or whatever you prefer) |
| Runtime | Python |
| Build Command | `pip install -r server/requirements.txt` |
| Start Command | `python -m server.app` |
| Plan | Free |

3. Add **Environment Variables** on the service:

| Key | Value |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `ADMIN_TOKEN` | Secret token for admin routes |
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.11.0` |
| `OPENAI_MODEL` | *(optional)* default: `gpt-4o-mini` |

4. Deploy. Render will auto-deploy on every push to the connected branch.

## URLs

| URL | Page |
|---|---|
| `https://<service>.onrender.com/` | Lumber Yard Restock Planner (demo) |
| `https://<service>.onrender.com/portfolio` | Portfolio page |
| `https://<service>.onrender.com/health` | Health check |
| `https://<service>.onrender.com/metrics` | Prometheus metrics |
| `https://<service>.onrender.com/admin/chat-logs?token=…` | Chat logs |
| `https://<service>.onrender.com/admin/chat-stats?token=…` | Chat stats |

## `render.yaml` (Infrastructure as Code)

The repo includes a `render.yaml` that Render uses for automatic service configuration.
If you set up via the dashboard, the `render.yaml` is optional but keeps config in source control.

## Environment Variables Not Active?

If your env vars show "not active" on Render, it means the service hasn't been redeployed since they were added. Go to your service → **Manual Deploy** → **Deploy latest commit** and they'll take effect.

## Testing Locally

```bash
# Install deps
pip install -r server/requirements.txt

# Set env vars
export OPENAI_API_KEY="sk-..."
export ADMIN_TOKEN="your-secret"

# Run
python -m server.app
```

Open `http://localhost:5000/` (demo) or `http://localhost:5000/portfolio` (portfolio).

## Custom Domain (Optional)

1. In Render dashboard → your service → **Settings** → **Custom Domains**
2. Add your domain (e.g. `mitchellsoftware.dev`)
3. Update your DNS records as Render instructs
4. Render handles SSL automatically
