-- ── Audit Log ────────────────────────────────────────────────
-- Tracks all create/update/delete actions across the app.
create table if not exists audit_logs (
  id          bigserial primary key,
  table_name  text not null,
  record_id   text not null,
  action      text not null,  -- 'create', 'update', 'delete'
  changed_by  text default 'admin',
  summary     text default '',
  created_at  timestamptz default now()
);

alter table audit_logs enable row level security;
create policy "open" on audit_logs for all using (true) with check (true);
