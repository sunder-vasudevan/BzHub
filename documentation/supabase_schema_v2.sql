-- ============================================================
-- BzHub v4.3 — Supabase Schema (v2 additions)
-- New tables: suppliers, goals, goal_checkins, appraisals,
--             skills, employee_skills
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- This file extends supabase_schema.sql (v4.0 base schema).
-- ============================================================

-- ── Suppliers ───────────────────────────────────────────────
-- Tracks vendor/supplier records for inventory sourcing.
create table if not exists suppliers (
  id             bigserial primary key,
  name           text not null,
  contact_person text default '',
  phone          text default '',
  email          text default '',
  notes          text default '',
  created_at     timestamptz default now()
);

-- ── Goals ───────────────────────────────────────────────────
-- Employee performance goals linked to the employees table.
create table if not exists goals (
  id           bigserial primary key,
  employee_id  bigint references employees(id) on delete cascade,
  title        text not null,
  description  text default '',
  due_date     text default '',
  status       text default 'Draft',
  created_at   timestamptz default now()
);

-- ── Goal Check-ins ──────────────────────────────────────────
-- Progress check-ins recorded against a specific goal.
create table if not exists goal_checkins (
  id           bigserial primary key,
  goal_id      bigint references goals(id) on delete cascade,
  progress_pct integer default 0,
  notes        text default '',
  checked_by   text default '',
  created_at   timestamptz default now()
);

-- ── Appraisals ──────────────────────────────────────────────
-- Annual / periodic performance appraisals for employees.
create table if not exists appraisals (
  id               bigserial primary key,
  employee_id      bigint references employees(id) on delete cascade,
  period           text not null,
  self_rating      numeric(3,1) default 0,
  manager_rating   numeric(3,1) default 0,
  self_comments    text default '',
  manager_comments text default '',
  status           text default 'Pending',
  created_at       timestamptz default now()
);

-- ── Skills ──────────────────────────────────────────────────
-- Global skill catalogue (e.g. "Python", category "Technical").
create table if not exists skills (
  id         bigserial primary key,
  name       text not null,
  category   text default '',
  created_at timestamptz default now()
);

-- ── Employee Skills ──────────────────────────────────────────
-- Junction table linking employees to skills with proficiency level.
create table if not exists employee_skills (
  id           bigserial primary key,
  employee_id  bigint references employees(id) on delete cascade,
  skill_id     bigint references skills(id) on delete cascade,
  proficiency  text default 'Beginner',
  created_at   timestamptz default now()
);

-- ── Leave Requests ───────────────────────────────────────────
-- Employee leave requests with manager approval workflow.
create table if not exists leave_requests (
  id           bigserial primary key,
  employee_id  bigint references employees(id) on delete cascade,
  leave_type   text not null default 'Annual',   -- Annual, Sick, Unpaid, Other
  start_date   date not null,
  end_date     date not null,
  reason       text default '',
  status       text default 'Pending',           -- Pending, Approved, Rejected
  reviewed_by  text default '',
  reviewed_at  timestamptz,
  created_at   timestamptz default now()
);

-- ── Purchase Orders ───────────────────────────────────────────
-- Purchase orders raised against suppliers, requiring manager approval.
create table if not exists purchase_orders (
  id                bigserial primary key,
  supplier_id       bigint references suppliers(id) on delete set null,
  supplier_name     text default '',
  order_date        date,
  expected_delivery date,
  total_amount      numeric(10,2) default 0,
  notes             text default '',
  status            text default 'Pending',      -- Pending, Approved, Rejected, Ordered, Delivered
  reviewed_by       text default '',
  reviewed_at       timestamptz,
  created_at        timestamptz default now()
);

-- ── Row Level Security ────────────────────────────────────────
-- For now: allow all (anon key). Tighten once auth is added.
alter table suppliers      enable row level security;
alter table goals          enable row level security;
alter table goal_checkins  enable row level security;
alter table appraisals     enable row level security;
alter table skills         enable row level security;
alter table employee_skills enable row level security;

-- Open policies (replace with auth.uid() checks when ready)
create policy "open" on suppliers       for all using (true) with check (true);
create policy "open" on goals           for all using (true) with check (true);
create policy "open" on goal_checkins   for all using (true) with check (true);
create policy "open" on appraisals      for all using (true) with check (true);
create policy "open" on skills          for all using (true) with check (true);
create policy "open" on employee_skills  for all using (true) with check (true);

alter table leave_requests   enable row level security;
alter table purchase_orders  enable row level security;

create policy "open" on leave_requests  for all using (true) with check (true);
create policy "open" on purchase_orders for all using (true) with check (true);

-- ══════════════════════════════════════════════════════════════
-- SEED DATA — Realistic sample data so the app isn't empty
-- ══════════════════════════════════════════════════════════════

-- ── Seed: Suppliers ──────────────────────────────────────────
insert into suppliers (name, contact_person, phone, email, notes) values
  ('TechSource Distributors',  'Marcus Webb',    '+1 415 555 0101', 'marcus@techsource.com',    'Primary electronics supplier. Net 30 payment terms.'),
  ('Global Hardware Co.',       'Priya Nair',     '+1 212 555 0182', 'priya@globalhardware.com', 'Cables, connectors, peripherals. Bulk discount above 500 units.'),
  ('Bright Office Supplies',    'Tom Ellison',    '+1 312 555 0247', 'tom@brightoffice.com',     'Stationery, packaging materials, printer consumables.'),
  ('FastShip Logistics',        'Sandra Ortiz',   '+1 305 555 0399', 'sandra@fastship.com',      'Same-day delivery available for urgent orders.'),
  ('ProParts Manufacturing',    'Kevin Lam',      '+1 650 555 0512', 'kevin@proparts.com',       'Custom hardware fabrication. Lead time 2–3 weeks.')
on conflict do nothing;

-- ── Seed: Skills Library ─────────────────────────────────────
-- Software skills
insert into skills (name, category) values
  ('Microsoft Excel',          'Software'),
  ('Microsoft Word',           'Software'),
  ('Google Sheets',            'Software'),
  ('PowerPoint / Slides',      'Software'),
  ('Python',                   'Software'),
  ('JavaScript',               'Software'),
  ('SQL',                      'Software'),
  ('Tableau / Power BI',       'Software'),
  ('QuickBooks / Xero',        'Software'),
  ('CRM Software',             'Software'),
  ('ERP Systems',              'Software'),
  ('Figma / Adobe XD',         'Software'),
  ('Slack / Teams',            'Software'),
  ('Project Management Tools', 'Software')
on conflict do nothing;

-- Hardware skills
insert into skills (name, category) values
  ('PC Assembly & Repair',     'Hardware'),
  ('Network Setup (LAN/WiFi)', 'Hardware'),
  ('POS System Setup',         'Hardware'),
  ('Printer & Scanner Setup',  'Hardware'),
  ('CCTV & Security Systems',  'Hardware'),
  ('Server Maintenance',       'Hardware'),
  ('Mobile Device Management', 'Hardware')
on conflict do nothing;

-- Soft skills
insert into skills (name, category) values
  ('Communication',            'Soft Skills'),
  ('Teamwork',                 'Soft Skills'),
  ('Problem Solving',          'Soft Skills'),
  ('Time Management',          'Soft Skills'),
  ('Leadership',               'Soft Skills'),
  ('Negotiation',              'Soft Skills'),
  ('Customer Service',         'Soft Skills'),
  ('Conflict Resolution',      'Soft Skills'),
  ('Adaptability',             'Soft Skills'),
  ('Presentation Skills',      'Soft Skills')
on conflict do nothing;

-- Domain knowledge
insert into skills (name, category) values
  ('Inventory Management',     'Domain Knowledge'),
  ('Sales & Marketing',        'Domain Knowledge'),
  ('Accounting & Finance',     'Domain Knowledge'),
  ('HR & Recruitment',         'Domain Knowledge'),
  ('Supply Chain',             'Domain Knowledge'),
  ('Quality Control',          'Domain Knowledge'),
  ('Health & Safety',          'Domain Knowledge'),
  ('Retail Operations',        'Domain Knowledge'),
  ('E-commerce',               'Domain Knowledge'),
  ('Data Analysis',            'Domain Knowledge')
on conflict do nothing;
