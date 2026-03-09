# BizHub Web Frontend

Next.js + TypeScript + Tailwind CSS web interface for the BizHub ERP system.

## Prerequisites

- Node.js 18+
- BizHub API running (see below)

## Setup

```bash
# 1. Copy environment file
cp bzhub_web/.env.local.example bzhub_web/.env.local

# 2. Edit .env.local and set your API URL (default: http://localhost:8000)

# 3. Install dependencies (if node_modules not present)
cd bzhub_web
npm install

# 4. Start the dev server
npm run dev
```

The app will be available at **http://localhost:3000**

## Requires BizHub API

The web frontend connects to the BizHub FastAPI backend. Start it with:

```bash
# From the project root
python bizhub.py --api
```

API docs available at: http://localhost:8000/docs

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | BizHub API base URL |

## Pages

| Route | Description |
|-------|-------------|
| `/` | Login page |
| `/dashboard` | KPI dashboard with sales trend |
| `/operations` | Operations hub (Contacts, CRM, Inventory, POS, Bills) |
| `/crm` | Full-screen CRM Kanban pipeline |

## Tech Stack

- **Next.js 14** — App Router
- **TypeScript** — Type safety
- **Tailwind CSS** — Styling (primary: #6D28D9)
- **Fetch API** — BizHub REST API client (`src/lib/api.ts`)
