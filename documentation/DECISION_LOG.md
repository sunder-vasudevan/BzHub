# BzHub — Decision Log

> Records key design and technical decisions made during development, including the reasoning and alternatives considered. This is the *why* behind the codebase.

---

## Format

```
### [DECISION-XXX] — Title
**Date:** YYYY-MM-DD
**Version:** vX.X.X
**Decision:** What was decided
**Alternatives considered:** What else was on the table
**Reasoning:** Why this option was chosen
**Trade-offs / known debt:** What we accepted by making this call
```

---

### [DECISION-001] — Desktop → Web Architecture Migration
**Date:** 2026-02-18
**Version:** v2.0
**Decision:** Migrated from Tkinter desktop app (v1.0) to Next.js web frontend + FastAPI backend
**Alternatives considered:** Electron desktop app, Flask + Jinja templates
**Reasoning:** Web-first enables multi-tenant SaaS end-goal; Next.js App Router + Tailwind give production-grade UI without custom CSS overhead
**Trade-offs / known debt:** FastAPI backend added infra complexity vs. a monolith; accepted as necessary for API-first architecture

---

### [DECISION-002] — SQLite → Supabase (PostgreSQL) Migration
**Date:** 2026-03-10
**Version:** v4.0
**Decision:** Replaced SQLite local DB with Supabase (PostgreSQL) + RLS
**Alternatives considered:** PlanetScale, Railway Postgres, Neon
**Reasoning:** Supabase free tier covers current scale; RLS enables multi-tenancy groundwork; Supabase client eliminates need for a separate ORM layer in Next.js
**Trade-offs / known debt:** RLS policies currently open (no user filtering) — tightens when Supabase Auth ships (FEAT-036)

---

### [DECISION-003] — UI Component System: shadcn/ui
**Date:** 2026-03-10
**Version:** v3.0
**Decision:** Adopted shadcn/ui as the component system over custom Tailwind components
**Alternatives considered:** Radix UI raw, MUI, Mantine
**Reasoning:** shadcn/ui gives accessible, composable components with full source ownership — no dependency lock-in; consistent with Tailwind-first approach
**Trade-offs / known debt:** Initial migration effort from custom components; accepted as one-time cost

---

### [DECISION-004] — Deployment: Vercel (frontend) + Supabase (DB)
**Date:** 2026-03-11
**Version:** v4.1.0
**Decision:** Deploy frontend on Vercel with CI/CD on push to main; DB on Supabase
**Alternatives considered:** Railway (full-stack), Render, Fly.io
**Reasoning:** Both free tier; Vercel + Next.js is purpose-built; zero config CI/CD; Supabase already chosen for DB
**Trade-offs / known debt:** No backend server (FastAPI removed at v4.0) — all DB calls via Supabase client directly from Next.js

---

### [DECISION-005] — Auth: Hardcoded for v1 (FEAT-036 deferred)
**Date:** 2026-03-11
**Version:** v4.1.x
**Decision:** Login hardcoded as admin/admin123 for demo/v1 scope
**Alternatives considered:** Supabase Auth (FEAT-036), Clerk, NextAuth
**Reasoning:** Auth adds multi-user complexity that blocks the core product build; demo-first strategy prioritises feature completeness over access control
**Trade-offs / known debt:** Not production-safe; RLS open; FEAT-036 (Supabase Auth) is Phase 3 blocker for multi-tenancy

---

## 2026-03-17 — v5.1.0 Session

### Decision: POS checkout creates one sale record per cart line
**Options considered:**
1. One sale record per transaction (aggregated)
2. One record per line item ← chosen

**Reason:** Existing `sales` table schema stores `item_name, quantity, sale_price` — no multi-item transaction structure. One row per item fits the schema without a migration and keeps Bills/Reports queries simple.

### Decision: Currency reactivity via custom DOM event (not context/state)
**Options considered:**
1. React context wrapping entire app
2. Custom `bzhub_currency_changed` window event ← chosen

**Reason:** Currency is already stored in localStorage. A custom event is the lightest-weight reactive bridge without refactoring the entire app to use a context provider. Consistent with how brand color is handled.

### Decision: Company name cached to localStorage (not fetched per-page)
**Options considered:**
1. Fetch from Supabase in AppLayout on every page load
2. Cache to localStorage on Settings load/save ← chosen

**Reason:** Avoids an extra Supabase call on every page. Settings already fetches it from Supabase — we piggyback on that. Known limitation: first-login on a fresh browser shows no company name until Settings is visited. Acceptable for v5.1.0; can be fixed in AppLayout later.

### Decision: FEAT-039 Offline-First deprioritized to last in Phase 2
**Reason:** Sunny Hayes's explicit direction. GST compliance and AI Insights deliver more immediate user value for the SMB target market than offline mode.
