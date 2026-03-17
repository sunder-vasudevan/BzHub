# BzHub — Test Log

> Records test results per feature. No feature is marked done until tested and logged here.

---

## Format

```
### [TEST-XXX] — Feature Name (FEAT-ID)
**Date:** YYYY-MM-DD
**Version:** vX.X.X
**Tested by:** Sunder
**Test type:** Manual / Automated / Both
**Environment:** Local / Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| | | | ✅ Pass / ❌ Fail / ⚠️ Partial |

**Known gaps:**
**Blocked on:**
```

---

### [TEST-001] — Approval Workflows (FEAT-034)
**Date:** 2026-03-12
**Version:** v4.4.0
**Tested by:** Sunder
**Test type:** Manual
**Environment:** Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| Submit leave request | Status → Pending | Pending shown in list | ✅ Pass |
| Manager approves leave | Status → Approved | Updated correctly | ✅ Pass |
| Manager rejects leave | Status → Rejected | Updated correctly | ✅ Pass |
| Purchase Order approval flow | PO → Pending → Approved | Worked end-to-end | ✅ Pass |
| Appraisal sign-off | Appraisal → Signed | Signed state persisted | ✅ Pass |

**Known gaps:** No email notification on approval (FEAT-802 scope)

---

### [TEST-002] — Employee Self-Service Portal (FEAT-035)
**Date:** 2026-03-12
**Version:** v4.5.0
**Tested by:** Sunder
**Test type:** Manual
**Environment:** Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| My Goals tab loads | Employee goals displayed | Loaded correctly | ✅ Pass |
| My Appraisals tab | Appraisals visible | Loaded correctly | ✅ Pass |
| My Leave tab | Leave requests visible + submit new | Working | ✅ Pass |
| My Skills tab | Skills displayed | Loaded correctly | ✅ Pass |

**Known gaps:** All employees see same data (no auth filtering until FEAT-036)

---

### [TEST-003] — Industry Templates (FEAT-038)
**Date:** 2026-03-12
**Version:** v4.7.0
**Tested by:** Sunder
**Test type:** Manual
**Environment:** Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| Retail template applies | Settings pre-filled for Retail | Applied correctly | ✅ Pass |
| Clinic template applies | Settings pre-filled for Clinic | Applied correctly | ✅ Pass |
| Restaurant template applies | Settings pre-filled for Restaurant | Applied correctly | ✅ Pass |
| Distributor template applies | Settings pre-filled for Distributor | Applied correctly | ✅ Pass |

**Known gaps:** None

---

### [TEST-004] — Dynamic Brand Color (v4.7.1)
**Date:** 2026-03-12
**Version:** v4.7.1
**Tested by:** Sunder
**Test type:** Manual
**Environment:** Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| Change brand color in Settings | Entire app theme updates via CSS vars | Updated across 24 files | ✅ Pass |
| Color persists on refresh | Saved to Supabase, reloads correctly | Persisted | ✅ Pass |

**Known gaps:** None

---

### [TEST-005] — Custom Fields Builder (FEAT-041 Phase 2.5a)
**Date:** 2026-03-13
**Version:** v5.0.0
**Tested by:** Sunder
**Test type:** Manual
**Environment:** Vercel (prod)

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| Create custom field | Field saved to Supabase | Saved correctly | ✅ Pass |
| Field appears in target module | Custom field rendered in form | Rendered | ✅ Pass |
| Delete custom field | Field removed | Removed correctly | ✅ Pass |

**Known gaps:** Custom fields not yet exported in CSV (FEAT-406 scope)

---

## v5.1.0 — 2026-03-17

### FEAT-POS-V2 — POS Overhaul
| Test | Result |
|------|--------|
| Add item to cart | ✅ Item appears in cart with qty 1 |
| Add same item again | ✅ Qty increments, no duplicate line |
| − button reduces qty | ✅ Qty decreases; item removed at 0 |
| + button capped at stock | ✅ Cannot exceed item.quantity |
| Out-of-stock item | ✅ Card shows overlay, click disabled |
| Payment method selection | ✅ Cash/Card/UPI selector toggles correctly |
| Checkout creates sale records | ✅ Verified via Supabase (one row per cart line) |
| Checkout deducts inventory | ✅ Inventory quantities updated in Supabase |
| Receipt modal appears | ✅ Shows itemized list, total, payment method |
| Print button | ✅ Triggers window.print() |
| Inventory reloads after checkout | ✅ Product cards reflect new stock |
| Empty cart checkout disabled | ✅ Checkout button disabled when cart empty |
| Checkout error handling | ✅ Toast error shown on failure |

### BUG-VERSION-SYNC
| Test | Result |
|------|--------|
| Login page version | ✅ Shows v5.0.0 |
| Sidebar footer | ✅ Shows v5.0.0 |
| Help page footer | ✅ Shows v5.0.0 |

### BUG-CURRENCY-REACTIVITY
| Test | Result |
|------|--------|
| Change currency in Settings → save | ✅ All pages update without reload |
| Refresh page after change | ✅ Symbol persists from localStorage |

### BUG-COMPANY-NAME
| Test | Result |
|------|--------|
| Save company name in Settings | ✅ Sidebar updates live |
| Reload page after save | ✅ Company name still shown (localStorage) |
| No company name set | ✅ Sidebar shows BzHub only (no empty subtitle) |
