-- Migration 002: Leave balances and deductions
-- leave_balances: per-employee per-year quota tracking
CREATE TABLE IF NOT EXISTS leave_balances (
  id              BIGSERIAL PRIMARY KEY,
  employee_id     BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  year            INT NOT NULL,
  sick_total      INT NOT NULL DEFAULT 10,
  sick_used       INT NOT NULL DEFAULT 0,
  personal_total  INT NOT NULL DEFAULT 10,
  personal_used   INT NOT NULL DEFAULT 0,
  personal_carried INT NOT NULL DEFAULT 0,  -- carried forward from prev year
  UNIQUE (employee_id, year)
);

CREATE INDEX IF NOT EXISTS idx_leave_balances_emp_year ON leave_balances(employee_id, year);

-- RLS: open (matches existing tables)
ALTER TABLE leave_balances ENABLE ROW LEVEL SECURITY;
CREATE POLICY "open" ON leave_balances USING (true) WITH CHECK (true);

-- leave_deductions: loss-of-pay records per leave request
CREATE TABLE IF NOT EXISTS leave_deductions (
  id              BIGSERIAL PRIMARY KEY,
  employee_id     BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  leave_request_id BIGINT REFERENCES leave_requests(id) ON DELETE SET NULL,
  year            INT NOT NULL,
  leave_type      TEXT NOT NULL,           -- 'Sick' | 'Personal'
  days            INT NOT NULL,
  amount          NUMERIC(10,2) NOT NULL,  -- days * rate (100 for testing)
  period          TEXT NOT NULL,           -- e.g. '2026-04'
  payroll_id      BIGINT REFERENCES payroll(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leave_deductions_emp ON leave_deductions(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_deductions_period ON leave_deductions(period);

ALTER TABLE leave_deductions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "open" ON leave_deductions USING (true) WITH CHECK (true);

-- Seed balances for all existing employees for current year
INSERT INTO leave_balances (employee_id, year, sick_total, sick_used, personal_total, personal_used, personal_carried)
SELECT id, EXTRACT(YEAR FROM NOW())::INT, 10, 0, 10, 0, 0
FROM employees
ON CONFLICT (employee_id, year) DO NOTHING;
