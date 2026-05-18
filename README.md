# Insurance Quote Comparison Tool

A demo full-stack application for comparing mock insurance quotes. Users enter basic applicant information (age, ZIP/state, coverage type, income, home ownership, and prior claims) and receive ranked carrier quotes based on price, coverage quality, and a transparent Python risk-scoring model.

## Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL (via Docker Compose locally; Vercel Postgres/Neon/Supabase in production)

## Features

- Applicant intake form for quote comparison
- Python risk scoring model with explainable factors and tiers
- Mock carrier quote engine ranked by value score
- PostgreSQL persistence for customer profiles and generated quotes
- FastAPI OpenAPI docs at `http://localhost:8000/docs` locally or `/api/docs` on Vercel

## Run locally with Docker

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`

## Deploy to Vercel

This repository includes `vercel.json` plus an `api/index.py` serverless entrypoint, so the frontend and FastAPI backend can deploy from the repo root.

1. Create a PostgreSQL database (Vercel Postgres, Neon, Supabase, or another hosted Postgres provider).
2. In Vercel, import the repository and keep the project root as the repository root.
3. Add a `DATABASE_URL` environment variable using SQLAlchemy's psycopg URL format, for example:

   ```text
   postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
   ```

4. Deploy. Vercel runs `cd frontend && npm install`, `cd frontend && npm run build`, serves the Vite build, and routes `/api/*` requests to the FastAPI serverless function.

The frontend defaults to `/api` in production and `http://localhost:8000` during local Vite development. You can override either with `VITE_API_URL`.

## Backend development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

## Frontend development

```bash
cd frontend
npm install
npm run dev
npm run build
```
