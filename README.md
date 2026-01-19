# Polymarket Kit

Polymarket Kit is a monitoring and analysis tool for Polymarket. It syncs market and trade data from Polymarket’s public APIs into SQLite and provides API endpoints plus a React dashboard to visualize smart money flows, whale activity, top profit rankings, and hot markets.

## Features

- Smart money monitoring
- Whale tracking
- Top profit rankings
- Hot markets list
- Automatic background data sync
- Manual sync endpoint

## Tech Stack

- Backend: FastAPI, SQLite, APScheduler
- Frontend: React, Vite, TypeScript
- Data Sources: Polymarket Gamma API and Data API

## Project Structure

```
ploymarket_kit/
├─ app/                 # FastAPI backend
├─ frontend/            # React frontend
├─ polymarket.db        # SQLite database (created at runtime)
├─ pyproject.toml
└─ requirements.txt
```

## Requirements

- Python 3.11+
- Node.js + npm
- uv (Python dependency manager)

## Backend Setup (uv)

From repository root:

```
uv sync
```

Run backend:

```
uv run uvicorn app.main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

## Frontend Setup

```
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:5173`

## Environment Variables

You can override defaults via environment variables:

| Variable | Description | Default |
|---------|-------------|---------|
| `DATABASE_URL` | SQLite path | `polymarket.db` |
| `POLYMARKET_GAMMA_URL` | Gamma base URL | `https://gamma-api.polymarket.com` |
| `POLYMARKET_DATA_URL` | Data base URL | `https://data-api.polymarket.com` |
| `VITE_API_BASE` | Frontend API base | `http://127.0.0.1:8000` |

## API Endpoints

- `GET /monitor/smart-money`
- `GET /monitor/whales`
- `GET /rankings/top-profit`
- `GET /markets/hot`
- `POST /admin/sync`
- `GET /demo`

## Manual Sync

Trigger a data pull from Polymarket:

```
curl -X POST http://127.0.0.1:8000/admin/sync
```

## Troubleshooting

### CORS
CORS is configured for `http://localhost:5173` and `http://127.0.0.1:5173`.
If your frontend runs on another port, update `app/main.py`.

### No Data
If the UI shows empty datasets, trigger manual sync:

```
curl -X POST http://127.0.0.1:8000/admin/sync
```

