# Release Notes - Version 2.0

## Summary
This release marks the official stable version 2.0 of BizHub Desktop. It restores the full tabbed interface with Dashboard, Inventory, POS, Reports, HR, and Visitors, and ensures all services are initialized before UI creation. Debug print statements are included for easier troubleshooting and future development.

## Key Changes
- Restored main tabbed interface (Dashboard, Inventory, POS, Reports, HR, Visitors)
- Fixed service initialization order to prevent AttributeErrors
- Added debug print statements for sidebar, topbar, content frame, and user info label creation
- Patched login flow to avoid referencing destroyed widgets
- Improved workflow comments for future development

## How to Use
- Login as usual; all main modules are available as tabs after login
- Use sidebar navigation for quick access to each module
- Debug output is available in the console for widget creation and UI flow

## Tag
This release is tagged as `v2.0` in the repository.

---
For any issues or feedback, please open an issue on the repository.
