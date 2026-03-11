-- BzHub v4.0 — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query

-- ── Inventory ──────────────────────────────────────────────
create table if not exists inventory (
  id            bigint generated always as identity primary key,
  item_name     text unique not null,
  quantity      integer default 0,
  threshold     integer default 0,
  cost_price    numeric(12,2) default 0,
  sale_price    numeric(12,2) default 0,
  description   text,
  image_path    text,
  updated_at    timestamptz default now()
);

-- ── Sales ──────────────────────────────────────────────────
create table if not exists sales (
  id            bigint generated always as identity primary key,
  sale_date     date not null default current_date,
  item_name     text not null,
  quantity      integer not null,
  sale_price    numeric(12,2) not null,
  total_amount  numeric(12,2) not null,
  username      text not null default 'admin'
);

-- ── CRM Contacts ───────────────────────────────────────────
create table if not exists crm_contacts (
  id            bigint generated always as identity primary key,
  name          text not null,
  company       text default '',
  email         text default '',
  phone         text default '',
  source        text default '',
  status        text default 'active',
  notes         text default '',
  created_at    timestamptz default now()
);

-- ── CRM Leads ──────────────────────────────────────────────
create table if not exists crm_leads (
  id            bigint generated always as identity primary key,
  contact_id    bigint references crm_contacts(id) on delete set null,
  title         text not null,
  stage         text default 'New',
  value         numeric(12,2) default 0,
  probability   integer default 0,
  owner         text default '',
  notes         text default '',
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- ── CRM Activities ─────────────────────────────────────────
create table if not exists crm_activities (
  id            bigint generated always as identity primary key,
  lead_id       bigint references crm_leads(id) on delete cascade,
  type          text default 'note',
  note          text default '',
  due_date      text default '',
  done          boolean default false,
  created_at    timestamptz default now()
);

-- ── Employees ──────────────────────────────────────────────
create table if not exists employees (
  id                bigint generated always as identity primary key,
  emp_number        text unique,
  name              text not null,
  joining_date      text,
  designation       text,
  manager           text,
  team              text,
  email             text,
  phone             text,
  emergency_contact text,
  salary            numeric(12,2) default 0,
  is_active         boolean default true,
  created_at        timestamptz default now()
);

-- ── Payroll ────────────────────────────────────────────────
create table if not exists payroll (
  id            bigint generated always as identity primary key,
  employee_id   bigint references employees(id) on delete cascade,
  period        text,
  basic         numeric(12,2) default 0,
  allowances    numeric(12,2) default 0,
  deductions    numeric(12,2) default 0,
  net           numeric(12,2) default 0,
  status        text default 'Draft',
  paid_date     text,
  created_at    timestamptz default now()
);

-- ── Company Info ───────────────────────────────────────────
create table if not exists company_info (
  id            bigint primary key default 1,
  company_name  text,
  address       text,
  phone         text,
  email         text,
  tax_id        text,
  bank_details  text,
  currency      text default 'INR',
  currency_symbol text default '₹'
);

-- Seed a default company_info row so upsert works
insert into company_info (id) values (1) on conflict (id) do nothing;

-- ── Row Level Security ────────────────────────────────────
-- For now: allow all (anon key). Tighten once auth is added.
alter table inventory       enable row level security;
alter table sales           enable row level security;
alter table crm_contacts    enable row level security;
alter table crm_leads       enable row level security;
alter table crm_activities  enable row level security;
alter table employees       enable row level security;
alter table payroll         enable row level security;
alter table company_info    enable row level security;

-- Open policies (replace with auth.uid() checks when ready)
create policy "allow all" on inventory       for all using (true) with check (true);
create policy "allow all" on sales           for all using (true) with check (true);
create policy "allow all" on crm_contacts    for all using (true) with check (true);
create policy "allow all" on crm_leads       for all using (true) with check (true);
create policy "allow all" on crm_activities  for all using (true) with check (true);
create policy "allow all" on employees       for all using (true) with check (true);
create policy "allow all" on payroll         for all using (true) with check (true);
create policy "allow all" on company_info    for all using (true) with check (true);
