-- Migration: 001_custom_data
-- Purpose: Stores per-record values for admin-defined custom fields.
-- Run this in your Supabase SQL editor.

create table if not exists custom_data (
  id           uuid default gen_random_uuid() primary key,
  entity_type  text not null,   -- 'employee' | 'contact' | 'lead' | 'product'
  entity_id    text not null,   -- stringified record id
  data         jsonb not null default '{}',
  created_at   timestamptz default now(),
  updated_at   timestamptz default now(),
  unique (entity_type, entity_id)
);

-- GIN index for fast JSONB searches
create index if not exists custom_data_data_gin on custom_data using gin (data);
-- Index for per-record lookups
create index if not exists custom_data_entity_idx on custom_data (entity_type, entity_id);

-- Optional: enable RLS (add org_id when multi-tenancy is ready — FEAT-037)
-- alter table custom_data enable row level security;
