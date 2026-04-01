# BzHub-Specific Rules

Auto-loaded when working in `~/Daytona/BzHub/`

---

## Backend API

- FastAPI structure with Pydantic validation
- Response format: `{"success": true, "data": {...}}`
- Auth: Supabase Auth + JWT tokens

## Frontend

- **Framework:** Next.js App Router
- **Mobile-first:** Test at 375px (iPhone SE) minimum
- **Date inputs:** Use `<select>` dropdowns, never `<input type="date">`

## Deployment

- Vercel CI/CD: auto-deploy on push to main
- After `vercel --prod`: re-alias domain
- Environment variables via Vercel console (use `printf` not `echo` for values)

## Database

- Supabase PostgreSQL with RLS policies
- Migrations tracked in `migrations/` directory
- Connection pool: max 20

## Standards

- `black` (100 char) for Python
- `Prettier` (100 char) for TypeScript/JS
- `ruff` strict mode for Python linting
- `ESLint` Airbnb for JavaScript
