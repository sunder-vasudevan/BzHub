# IdeaBoard

Realtime idea board for small teams (2–3 people). Share a board code, add ideas, and pick up exactly where you left off.

## Stack

- Next.js (App Router)
- TypeScript + Tailwind CSS
- Supabase (Postgres + Realtime)

## Setup

1) Install dependencies

```
npm install
```

2) Create a Supabase project and add the table + policies below.

3) Copy .env.local.example to .env.local and fill in your Supabase keys.

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

4) Start the dev server

```
npm run dev
```

## Database schema

Run this in the Supabase SQL editor:

```
create extension if not exists "uuid-ossp";

create table if not exists public.ideas (
	id uuid primary key default uuid_generate_v4(),
	board_id text not null,
	"column" text not null check ("column" in ('backlog', 'in_progress', 'done')),
	title text not null,
	detail text,
	created_at timestamp with time zone default now(),
	updated_at timestamp with time zone default now()
);

alter table public.ideas enable row level security;

create policy "Ideas are readable" on public.ideas
	for select
	using (true);

create policy "Ideas are writable" on public.ideas
	for all
	using (true)
	with check (true);
```

## Notes

- Board codes are stored in localStorage so teammates can return later.
- No authentication is required by default. Lock it down by replacing the RLS policies.
