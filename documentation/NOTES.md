# Persistent Notes

Use this file to store anything you want me to remember between sessions.

## How to use
- Add items under **Notes** below.
- At the start of a new session, tell me: “Read documentation/NOTES.md first.”

## Notes

### v5.2.0 Leave Quota System (2026-04-02)
- **Leave tables applied to prod DB:** `leave_balances`, `leave_deductions` (migration 002)
- **23 employees seeded** with 2026 balances (10 Sick + 10 Personal each)
- **LOP rate:** ₹100/day for testing
- **Quota rules:** Sick and Personal cannot be clubbed; Sick expires annually; Personal carry-forward capped at 20
- **Payroll auto-loads LOP** deductions for the selected employee+period
- **Year-end payout button** in Leave tab (processes carry-forward + payout for excess personal)
- Real app is `bzhub_web/bzhub_web/src/` — NOT `frontend/` (Copilot scaffold)
- Data layer: `src/lib/db.ts` (direct Supabase) — NOT `api.ts` (backend proxy)
