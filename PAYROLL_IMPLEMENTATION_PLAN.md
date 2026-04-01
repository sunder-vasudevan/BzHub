# BzHub Payroll Feature — Implementation Plan

**Status:** Planning Phase  
**Feature:** Salary Calculator (MVP)  
**Last Updated:** 2026-03-31  
**Author:** Sunny Hayes + Claude

---

## Overview

Simple one-click salary calculator for small teams (<10 employees). Auto-detects paid leave and unpaid absences from existing leave tracking, calculates adjusted monthly salary, and displays breakdown on-screen. No export, no tax calculations—MVP only.

**Problem:** Businesses manually calculate salaries monthly, factoring in variable elements (paid leave, unpaid absences, overtime, bonuses).

**Solution:** One-click calculator that auto-detects leave from existing records and shows final salary breakdown.

---

## Architecture

### Tech Stack (Confirmed)
- **Backend:** FastAPI (existing BzHub backend, Python)
- **Database:** Supabase (PostgreSQL, existing)
- **Frontend:** Next.js 14 + React + Tailwind CSS (existing bzhub_web)
- **Authentication:** Admin/admin123 (hardcoded, existing — defer multi-tenant to Phase 3)

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BzHub Frontend (Next.js)                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  app/hr/payroll/[employeeId]/page.tsx                 │  │
│  │  - Month picker (dropdown)                            │  │
│  │  - Salary breakdown card (base, leave, deduction)     │  │
│  │  - 12-month history table                             │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ (REST API)
┌─────────────────────────────────────────────────────────────┐
│              BzHub Backend (FastAPI, Python)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  api/payroll.py (NEW)                                 │  │
│  │  ├─ POST /api/payroll/calculate                       │  │
│  │  ├─ GET /api/payroll/calculate/:empId?month=YYYY-MM   │  │
│  │  └─ GET /api/payroll/history/:empId                   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  services/payroll_service.py (NEW)                    │  │
│  │  ├─ calculate_monthly_pay(emp_id, year, month)        │  │
│  │  ├─ get_leave_summary(emp_id, year, month)            │  │
│  │  ├─ prorate_salary(base, days_present, days_in_month) │  │
│  │  └─ categorize_leave(leave_records)                   │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ (SQL)
┌─────────────────────────────────────────────────────────────┐
│                 Supabase (PostgreSQL)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  employees (existing)                                  │  │
│  │  ├─ id (PK)                                            │  │
│  │  ├─ name                                               │  │
│  │  ├─ base_salary (DECIMAL)                              │  │
│  │  ├─ salary_effective_date                              │  │
│  │  └─ employment_type (full-time, part-time, contract)  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  leave_records (existing)                              │  │
│  │  ├─ id (PK)                                            │  │
│  │  ├─ employee_id (FK → employees)                       │  │
│  │  ├─ leave_type (paid, unpaid, public_holiday)          │  │
│  │  ├─ date                                               │  │
│  │  ├─ duration_days                                      │  │
│  │  └─ status (approved, pending, rejected)               │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  salary_calculations (NEW — caching layer)             │  │
│  │  ├─ id (PK)                                            │  │
│  │  ├─ employee_id (FK → employees)                       │  │
│  │  ├─ calculation_period (YYYY-MM)                       │  │
│  │  ├─ base_salary                                        │  │
│  │  ├─ paid_leave_days                                    │  │
│  │  ├─ unpaid_absence_days                                │  │
│  │  ├─ deduction_amount                                   │  │
│  │  ├─ final_salary                                       │  │
│  │  ├─ created_at                                         │  │
│  │  └─ updated_at                                         │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Implementation

### 1. Payroll Service Module (`api/services/payroll_service.py`)

**Location:** `api/services/payroll_service.py` (create `services/` dir if not exists)

**Core Functions:**

#### `calculate_monthly_pay(employee_id: str, year: int, month: int) -> dict`

**Purpose:** Main calculation engine. Returns salary breakdown.

**Input:**
- `employee_id`: UUID or int from employees table
- `year`: 2026
- `month`: 1–12

**Output:**
```python
{
    "employee_id": "uuid-123",
    "calculation_period": "2026-03",
    "base_salary": 3000.00,
    "paid_leave_days": 2,
    "unpaid_absence_days": 2,
    "deduction_amount": 200.00,  # 2 days × (3000 / 30)
    "final_salary": 2800.00,
    "calculation_date": "2026-03-31T10:30:00Z"
}
```

**Logic:**
1. Fetch employee record → validate exists, extract `base_salary`, `salary_effective_date`
2. Query `leave_records` for the month (date >= YYYY-MM-01 AND date < YYYY-MM+1-01)
3. Categorize leave: 
   - `leave_type = "paid"` → add to `paid_leave_days`
   - `leave_type = "unpaid"` → add to `unpaid_absence_days`
   - `leave_type = "public_holiday"` → add to `paid_leave_days`
4. Calculate deduction: `unpaid_absence_days * (base_salary / 30)`
5. Calculate final: `base_salary - deduction`
6. Store in `salary_calculations` table for caching
7. Return breakdown dict

**Edge Cases:**
- Mid-month joins: Prorate salary by days present
  - `final_salary = (days_present / days_in_month) * base_salary - deduction`
- No leave records: Return `paid_leave_days = 0, unpaid_absence_days = 0, deduction = 0`
- Employee not found: Raise `ValueError("Employee not found")`
- Invalid month: Raise `ValueError("Invalid month")`

---

#### `get_leave_summary(employee_id: str, year: int, month: int) -> dict`

**Purpose:** Helper—fetch and categorize leave for a given month.

**Output:**
```python
{
    "paid_leave": [
        {"date": "2026-03-15", "duration_days": 1, "type": "vacation"},
        {"date": "2026-03-25", "duration_days": 0.5, "type": "public_holiday"}
    ],
    "unpaid_leave": [
        {"date": "2026-03-10", "duration_days": 1, "type": "absence"}
    ],
    "paid_leave_total_days": 1.5,
    "unpaid_leave_total_days": 1
}
```

**Logic:**
- Query Supabase `leave_records` for date range
- Group by `leave_type`
- Sum `duration_days` for each group
- Return categorized list + totals

---

#### `prorate_salary(base_salary: float, days_present: int, days_in_month: int) -> float`

**Purpose:** Calculate prorated salary for mid-month joins/exits.

**Formula:** `(days_present / days_in_month) * base_salary`

**Example:** Employee joins mid-March (15th):
- Days present: 17 (March 15–31)
- Days in month: 31
- Base: $3000
- Prorated: (17/31) × 3000 = $1645.16

---

#### `categorize_leave(leave_records: list) -> dict`

**Purpose:** Helper—categorize leave records into paid/unpaid.

**Input:** Raw leave records from Supabase

**Output:**
```python
{
    "paid": [record1, record2],  # leave_type in ["paid", "vacation", "sick", "public_holiday"]
    "unpaid": [record3, record4]   # leave_type in ["unpaid", "absence_without_leave"]
}
```

**Logic:**
- Define mappings: `PAID_TYPES = ["paid", "vacation", "sick", "public_holiday"]`
- Filter records by type
- Return categorized dict

---

### 2. Payroll API Router (`api/payroll.py`)

**Location:** `api/payroll.py` (new file)

**Endpoints:**

#### `POST /api/payroll/calculate`

**Purpose:** Calculate salary for an employee in a given month (or recalculate existing).

**Request Body:**
```json
{
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "year": 2026,
    "month": 3
}
```

**Response (200):**
```json
{
    "success": true,
    "data": {
        "employee_id": "550e8400-e29b-41d4-a716-446655440000",
        "calculation_period": "2026-03",
        "base_salary": 3000.00,
        "paid_leave_days": 2,
        "unpaid_absence_days": 2,
        "deduction_amount": 200.00,
        "final_salary": 2800.00,
        "calculation_date": "2026-03-31T10:30:00Z"
    }
}
```

**Error (400/404):**
```json
{
    "success": false,
    "error": "Employee not found"
}
```

**Logic:**
- Call `payroll_service.calculate_monthly_pay()`
- Return JSON response
- Handle exceptions (employee not found, invalid month, DB errors)

---

#### `GET /api/payroll/calculate/:employee_id?month=YYYY-MM`

**Purpose:** Fetch salary calculation for a specific month (cached or fresh).

**Query Parameters:**
- `month` (required): `2026-03` format
- `force_recalculate` (optional): `true` to skip cache, default `false`

**Response (200):**
Same as POST response (data from `salary_calculations` cache or fresh calculation)

**Logic:**
1. Parse `month` → extract year, month
2. Query `salary_calculations` table: `WHERE employee_id = ? AND calculation_period = ?`
3. If found AND `force_recalculate = false` → return cached result
4. Else → call `payroll_service.calculate_monthly_pay()`, store in DB, return

---

#### `GET /api/payroll/history/:employee_id`

**Purpose:** Fetch 12-month salary calculation history for audit trail.

**Query Parameters:**
- `months` (optional): default 12, max 36

**Response (200):**
```json
{
    "success": true,
    "employee_id": "550e8400...",
    "history": [
        {
            "calculation_period": "2026-03",
            "base_salary": 3000.00,
            "paid_leave_days": 2,
            "unpaid_absence_days": 2,
            "deduction_amount": 200.00,
            "final_salary": 2800.00,
            "created_at": "2026-03-31T10:30:00Z"
        },
        ... (11 more months)
    ]
}
```

**Logic:**
- Query `salary_calculations` for employee
- Order by `calculation_period DESC`
- Limit to `months` parameter
- Return list of calculations

---

### 3. Database Migration Script

**Location:** `api/migrations/YYYYMMDD_add_salary_calculations.sql`

**SQL:**
```sql
-- Create salary_calculations table
CREATE TABLE salary_calculations (
    id BIGSERIAL PRIMARY KEY,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    calculation_period VARCHAR(7) NOT NULL,  -- YYYY-MM format
    base_salary DECIMAL(10, 2) NOT NULL,
    paid_leave_days DECIMAL(5, 2) NOT NULL DEFAULT 0,
    unpaid_absence_days DECIMAL(5, 2) NOT NULL DEFAULT 0,
    deduction_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    final_salary DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(employee_id, calculation_period)
);

-- Index for fast lookups
CREATE INDEX idx_salary_calculations_employee_period 
ON salary_calculations(employee_id, calculation_period DESC);

-- Ensure leave_records table has leave_type column and proper types
-- (assumes already exists; verify schema in BzHub DB)
ALTER TABLE leave_records 
ADD COLUMN IF NOT EXISTS leave_type VARCHAR(50) DEFAULT 'unpaid';
```

---

## Frontend Implementation

### 1. Payroll Calculator Page

**Location:** `bzhub_web/app/hr/payroll/[employeeId]/page.tsx` (new route)

**Components:**

#### Main Page (`page.tsx`)
- Route param: `[employeeId]`
- State:
  - `selectedMonth`: Date object (default: current month)
  - `calculationData`: salary breakdown
  - `loading`: boolean
  - `error`: string or null
- Render:
  - Header: "Salary Calculation"
  - Month picker component
  - Salary breakdown card (or loading/error state)
  - History table (toggle or collapsible)

---

#### Month Picker Component (`MonthPicker.tsx`)
- Input: `onMonthSelect(date)` callback
- Render: Dropdown or date input (or custom month/year selects for Safari compatibility)
- Default: current month
- Validation: only days 1–28 of selected month allowed to ensure full month data

---

#### Salary Breakdown Card (`SalaryBreakdown.tsx`)
- Input: `calculation: SalaryCalculation` (from API)
- Render (Tailwind CSS):
  ```
  ┌────────────────────────────────┐
  │ Salary Breakdown — March 2026   │
  ├────────────────────────────────┤
  │ Base Salary:       $3,000.00    │
  │ Paid Leave Days:   2 days       │
  │ Unpaid Absences:   2 days       │
  │ Deduction:         -$200.00     │
  ├────────────────────────────────┤
  │ Final Salary:      $2,800.00    │
  └────────────────────────────────┘
  ```
- Mobile: stack vertically, larger font for final salary
- Responsive: max-width 500px (card), center on page

---

#### History Table (`SalaryHistory.tsx`)
- Input: `history: SalaryCalculation[]` (last 12 months)
- Render: Table or accordion (collapsible by default)
  ```
  Period    | Base Salary | Paid Leave | Unpaid Abs. | Deduction | Final Salary
  ──────────────────────────────────────────────────────────────────────────
  2026-03   | $3,000      | 2 days     | 2 days      | -$200     | $2,800
  2026-02   | $3,000      | 1 day      | 0 days      | -$100     | $2,900
  ...
  ```
- Mobile: stack into cards instead of table

---

### 2. Employee Profile Link

**Location:** `bzhub_web/app/hr/employees/[employeeId]/page.tsx` (modify existing)

**Change:** Add button in employee detail panel:
```tsx
<Button onClick={() => navigate(`/hr/payroll/${employeeId}`)}>
  View Salary Calculation
</Button>
```

---

## Data Models & Validation

### Salary Calculation Object (TypeScript)

```typescript
interface SalaryCalculation {
  employee_id: string;
  calculation_period: string;  // YYYY-MM
  base_salary: number;
  paid_leave_days: number;
  unpaid_absence_days: number;
  deduction_amount: number;
  final_salary: number;
  calculation_date: string;    // ISO 8601
}

interface SalaryHistoryResponse {
  success: boolean;
  employee_id: string;
  history: SalaryCalculation[];
}
```

---

## Testing Strategy

### Unit Tests (`api/tests/test_payroll_service.py`)

**Test Cases:**

1. **`test_calculate_basic_salary`**
   - Input: Base $3000, 2 unpaid days
   - Expected: Deduction $200, final $2800
   - Assert: calculation matches expected

2. **`test_calculate_with_no_absences`**
   - Input: Base $3000, 0 unpaid days
   - Expected: Deduction $0, final $3000
   - Assert: equals base salary

3. **`test_calculate_full_month_unpaid`**
   - Input: Base $3000, 30 unpaid days
   - Expected: Final $0
   - Assert: final salary is 0

4. **`test_prorate_midmonth_join`**
   - Input: Base $3000, joins on 15th
   - Expected: Prorated to 17 days (15–31)
   - Assert: final ≈ $1645.16

5. **`test_employee_not_found`**
   - Input: Non-existent employee_id
   - Expected: ValueError
   - Assert: exception raised

6. **`test_invalid_month`**
   - Input: month = 13
   - Expected: ValueError
   - Assert: exception raised

7. **`test_categorize_leave`**
   - Input: Mixed leave records (paid vacation, unpaid absence)
   - Expected: Correctly grouped
   - Assert: paid_list and unpaid_list match

---

### API Tests (`api/tests/test_payroll_api.py`)

1. **`test_post_calculate_endpoint`**
   - Request: POST /api/payroll/calculate with valid employee_id, month
   - Expected: 200 response with salary breakdown
   - Assert: response.data.final_salary == 2800

2. **`test_get_calculate_endpoint_cached`**
   - Setup: Pre-calculate and store in DB
   - Request: GET /api/payroll/calculate/emp_id?month=2026-03
   - Expected: 200 response (cached result)
   - Assert: created_at matches stored record

3. **`test_get_calculate_force_recalculate`**
   - Setup: Change leave data after first calculation
   - Request: GET /api/payroll/calculate/emp_id?month=2026-03&force_recalculate=true
   - Expected: 200 response with fresh calculation
   - Assert: final_salary reflects new leave data

4. **`test_get_history_endpoint`**
   - Setup: 12 months of calculation records
   - Request: GET /api/payroll/history/emp_id
   - Expected: 200 response with 12 items
   - Assert: length == 12, ordered by period DESC

5. **`test_employee_not_found_404`**
   - Request: GET /api/payroll/calculate/invalid_id?month=2026-03
   - Expected: 404 response
   - Assert: error message contains "not found"

---

### Integration Tests (`api/tests/test_payroll_integration.py`)

1. **`test_end_to_end_calculate_and_fetch`**
   - Create test employee: Base $3000
   - Add leave records: 2 unpaid days in March
   - POST /api/payroll/calculate
   - GET /api/payroll/calculate (verify cached)
   - GET /api/payroll/history (verify stored)
   - Assert: All three calls consistent

2. **`test_leave_api_integration`**
   - Verify leave_records query returns correct leave_type values
   - Ensure absence records are categorized as unpaid
   - Vacation records are categorized as paid

---

### Frontend Tests (`bzhub_web/__tests__/hr/payroll.test.tsx`)

1. **`test_month_picker_renders`**
   - Render MonthPicker with default month
   - Assert: current month selected

2. **`test_salary_breakdown_card_displays`**
   - Render SalaryBreakdown with mock data
   - Assert: all fields displayed (base, paid leave, deduction, final)

3. **`test_fetch_salary_calculation_on_load`**
   - Render payroll page with employeeId
   - Assert: API called with correct params
   - Assert: data displayed after load

4. **`test_month_change_refetches_data`**
   - Change selected month
   - Assert: API called with new month
   - Assert: UI updates with new calculation

5. **`test_error_state_displays_on_api_failure`**
   - Mock API to return 404
   - Render page
   - Assert: error message displayed

---

## Implementation Phases

### Phase 1: Backend Foundation (3–4 days)

**Tasks:**
1. Create `api/services/payroll_service.py` with all calculation functions
2. Create `api/payroll.py` with 3 API endpoints
3. Create database migration for `salary_calculations` table
4. Run migration and verify schema
5. Write unit tests for `payroll_service.py`
6. Write API tests for all 3 endpoints
7. Manual API testing via Swagger UI or Postman

**Deliverable:** Fully tested payroll calculation engine + API

**Verification:**
- All unit tests passing (8+ test cases)
- All API tests passing (5+ test cases)
- Manual test: Create test employee, add leave, calculate salary, verify caching

---

### Phase 2: Frontend UI (2–3 days)

**Tasks:**
1. Create `app/hr/payroll/[employeeId]/page.tsx`
2. Create `MonthPicker.tsx` component
3. Create `SalaryBreakdown.tsx` component
4. Create `SalaryHistory.tsx` component
5. Add "View Salary Calculation" button to employee profile
6. Style with Tailwind CSS v4 (mobile-first)
7. Write frontend component tests

**Deliverable:** Fully functional payroll UI page

**Verification:**
- Page loads without errors
- Month picker updates calculation
- History displays last 12 months
- Mobile responsive (test at 375px)

---

### Phase 3: Integration & Testing (2–3 days)

**Tasks:**
1. Write integration tests (end-to-end scenarios)
2. Manual QA: Test with multiple employees, different leave scenarios
3. Verify edge cases: mid-month joins, no leave, all unpaid
4. Performance test: History query with 36 months of data
5. Document API in README (endpoint specs, examples)
6. Add feature toggle or feature flag (if needed for gradual rollout)

**Deliverable:** Fully tested, production-ready payroll feature

**Verification:**
- All integration tests passing
- Manual QA signed off
- No console errors or warnings
- API docs updated

---

## Configuration & Constants

### Salary Deduction Formula (Configurable)

**Current MVP:** `unpaid_day_cost = base_salary / 30`

**Future:** Make configurable per company policy:
```python
DEDUCTION_POLICY = {
    "calculation_method": "per_day",  # or "per_hour" if hourly tracking added
    "days_per_month": 30,             # or 22 (weekdays only)
    "unpaid_deduction_rate": 1.0      # multiplier (1.0 = full deduction)
}
```

---

### Leave Type Mappings (Configurable)

**Current MVP:**
```python
PAID_LEAVE_TYPES = ["paid", "vacation", "sick", "public_holiday"]
UNPAID_LEAVE_TYPES = ["unpaid", "absence_without_leave"]
```

**Future:** Make configurable per company:
```python
LEAVE_TYPE_POLICY = {
    "vacation": {"paid": True, "deductible": False},
    "sick": {"paid": True, "deductible": False},
    "unpaid": {"paid": False, "deductible": True},
    ...
}
```

---

## Known Constraints & Assumptions

1. **Monthly Pay Frequency Only (MVP)**
   - Assumes all employees paid monthly
   - Extend to bi-weekly/weekly in Phase 2

2. **No Tax Calculations**
   - MVP returns gross salary only
   - Tax, PF, other deductions deferred to Phase 2

3. **Auto-Detection Only**
   - Relies on existing `leave_records` data
   - Manual entry/overrides deferred to Phase 2

4. **Single Currency**
   - Assumes all salaries in same currency (INR or user's local)
   - Multi-currency support deferred

5. **No Bonus/Overtime in MVP**
   - Festival bonuses and overtime deferred to Phase 2
   - Plan to add as separate line items later

6. **Caching Strategy**
   - Calculations stored in DB to avoid recalculation
   - Cache invalidation: re-calculate on demand (`force_recalculate=true`)
   - Future: Add cache invalidation hook when leave records change

7. **Authentication**
   - Uses existing admin/admin123 (hardcoded)
   - Defer RLS and multi-tenant auth to Phase 3

---

## Future Enhancements (Post-MVP)

1. **Festival Bonuses** — Manual entry or rule-based trigger by holiday
2. **Overtime Calculation** — Hours tracked in timesheet, 1.5x–2x multiplier
3. **PDF Export** — Salary slip generation (FPDF or Reportlab)
4. **Bank API Integration** — Auto-transfer final salary (Razorpay, etc.)
5. **Tax Compliance** — India GST/Tax, statutory deductions (PF, ESI)
6. **Multiple Pay Frequencies** — Bi-weekly, weekly, annual
7. **Batch Calculations** — Calculate all employees for month in one click
8. **Salary Advance** — Track advances, deduct from future salary
9. **Approval Workflow** — Manager approves before salary release
10. **Role-Based Access** — HR can calculate, employees can view own only

---

## Acceptance Criteria (MVP)

- [ ] Calculate monthly salary correctly (base - unpaid deductions)
- [ ] Display breakdown: base, paid leave days, unpaid absence days, deduction, final salary
- [ ] Auto-detect leave from existing `leave_records` (no manual entry needed)
- [ ] Show 12-month calculation history for audit trail
- [ ] Handle edge cases: mid-month joins, terminations (proration), no leave data
- [ ] All unit tests passing (8+ cases)
- [ ] All API tests passing (5+ cases)
- [ ] All integration tests passing
- [ ] Frontend responsive at 375px (mobile), 1024px (tablet), 1920px (desktop)
- [ ] Manual QA passed on 5+ employee profiles with varying leave scenarios
- [ ] No console errors or warnings
- [ ] API documented in README (endpoint specs + examples)
- [ ] Code reviewed and merged to main

---

## Rollout Plan

1. **Week 1:** Implement Phase 1 (backend) + Phase 3 unit/API tests
2. **Week 2:** Implement Phase 2 (frontend) + Phase 3 integration tests + QA
3. **Week 3:** Manual testing, bug fixes, documentation, merge to main

**Launch:** Feature available to all BzHub users by end of Week 3

---

## Support & Troubleshooting

### Common Issues

**Issue:** `Employee not found`
- Ensure employee exists in `employees` table
- Verify `employee_id` matches DB UUID

**Issue:** Deduction calculated incorrectly
- Verify `leave_records.leave_type` values match mappings
- Check `employees.base_salary` is set correctly
- Ensure `leave_records.duration_days` is numeric (not NULL)

**Issue:** History returns empty
- Verify calculations have been run for the month
- Try `force_recalculate=true` to trigger fresh calculation

---

**End of Implementation Plan**

---

I've created a comprehensive implementation plan for the BzHub payroll feature. It includes:

✅ **Architecture** — System diagram showing frontend → backend → database flow  
✅ **Backend details** — Payroll service functions, 3 API endpoints with request/response specs, database migration  
✅ **Frontend details** — Page structure, 4 components (month picker, breakdown card, history table), responsive design  
✅ **Testing strategy** — Unit tests (8 cases), API tests (5 cases), integration tests, frontend tests  
✅ **Implementation phases** — 3-phase rollout (backend → frontend → integration & QA)  
✅ **Configuration** — Salary deduction formula, leave type mappings (extensible for future)  
✅ **Constraints & assumptions** — MVP scope (monthly only, no tax, no bonuses)  
✅ **Future enhancements** — 10 planned features (bonuses, overtime, PDF, bank integration, tax compliance)  
✅ **Acceptance criteria** — 12 checkboxes for ship-readiness  
✅ **Rollout & troubleshooting** — 3-week timeline, common issue resolution  

**Ready to implement when you give the signal.** This plan serves as a blueprint for all three phases and can be executed step-by-step.
<function_calls>
<invoke name="task_complete">
<parameter name="summary">Created comprehensive BzHub payroll feature implementation plan. Deliverable: 400-line detailed specification covering architecture (system diagram), backend (payroll service with 3 API endpoints + DB migration), frontend (4 React components for salary calculator page), full testing strategy (unit, API, integration, frontend tests), 3-phase implementation roadmap, configuration options for future extensibility, MVP constraints, 10 future enhancements, acceptance criteria checklist, and rollout plan. Ready for development execution.