-- Payroll Phase 1 Migration
-- Create payroll_records table for storing generated payslips
-- Create payroll_config table for system-wide deduction configuration

-- payroll_records: Main table for storing payslip records
CREATE TABLE IF NOT EXISTS payroll_records (
  id BIGSERIAL PRIMARY KEY,
  employee_id TEXT NOT NULL,
  gross_salary DECIMAL(10, 2) NOT NULL,
  deductions JSONB NOT NULL DEFAULT '{}',
  net_salary DECIMAL(10, 2) NOT NULL,
  period TEXT NOT NULL,
  status TEXT DEFAULT 'generated',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- payroll_config: System configuration for salary deductions
CREATE TABLE IF NOT EXISTS payroll_config (
  id BIGSERIAL PRIMARY KEY,
  tax_rate DECIMAL(5, 4) DEFAULT 0.1000,
  insurance DECIMAL(10, 2) DEFAULT 500.00,
  loan_emi DECIMAL(10, 2) DEFAULT 0.00,
  professional_tax DECIMAL(10, 2) DEFAULT 200.00,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default payroll configuration
INSERT INTO payroll_config (tax_rate, insurance, professional_tax)
VALUES (0.10, 500.00, 200.00)
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_payroll_records_employee_id ON payroll_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_records_period ON payroll_records(period);
CREATE INDEX IF NOT EXISTS idx_payroll_records_created_at ON payroll_records(created_at DESC);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_payroll_records_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payroll_records_update_timestamp
BEFORE UPDATE ON payroll_records
FOR EACH ROW
EXECUTE FUNCTION update_payroll_records_timestamp();
