# BizHub App: Classes & Architecture (Newbie-Friendly)

## What is BizHub?
BizHub is an all-in-one business management app. It helps companies manage customers, inventory, payroll, analytics, and more, all in one place.

## Main Class (Desktop)
- **BizHubDesktopApp**: The main class for the desktop app (built with Tkinter).
  - Handles the main window and navigation.
  - Manages user login, roles, and what features each user can access.
  - Connects to services for things like database, authentication, analytics, etc.
  - Shows different sections: Dashboard, Inventory, Sales, Reports, HR, Settings.

## Key Modules & Classes
- **Database Layer**
  - `SQLiteAdapter`: Handles all database operations.
  - `DatabaseAdapter`: The base class for database adapters.

- **Core Utilities (src/core)**
  - `CurrencyFormatter`, `HRCalculator`, `InventoryCalculator`, `POSCalculator`, `BillNameGenerator`, `DataValidator`: Helpers for calculations, formatting, and checking data.

- **Service Layer (src/services)**
  - `AuthService`, `InventoryService`, `POSService`, `HRService`, `VisitorService`, `EmailService`, `ActivityService`, `CompanyService`, `AnalyticsService`, `PayrollService`, `AppraisalService`, `SupabaseService`: Each class manages a specific business function (like authentication, inventory, payroll, analytics, or cloud sync).

## How the Architecture Works
- The UI (Tkinter) talks to service classes for business logic.
- Services talk to the database layer to store and get data.
- Core utilities provide shared logic for calculations and formatting.
- Cloud sync and multi-user support are handled by Supabase integration.

## Why is it Scalable?
- The code is modular, so you can add new features or services easily.
- You can switch from SQLite to a bigger database if needed.
- The web and desktop UIs can be developed separately but share backend logic.

---
This summary is for beginners. For more details, check the code or ask for a deep dive into any part!
