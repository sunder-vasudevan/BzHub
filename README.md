# Bzhub

Bzhub is a complete ERP suite for small businesses, offering modules for inventory, POS, HR, CRM, analytics, and more. It is designed for easy deployment as a desktop app (Tkinter) with future support for web and API modes.

## Features
- Inventory, POS, HR, CRM, and analytics modules
- Modern Tkinter desktop UI
- Modular, extensible architecture
- Roadmap for web, API, and cloud support

## Installation
1. Clone this repository:
   ```sh
  git clone https://github.com/sunder-vasudevan/BzHub.git
  cd BzHub
   ```
2. (Recommended) Create and activate a Python virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the App
- **Desktop (Tkinter) mode:**
  ```sh
  python bizhub.py
  ```
- **Web/API modes:**
  (Planned for future releases)

## Configuration
- The default database is `inventory.db` (SQLite). You can specify a different database file with:
  ```sh
  python bizhub.py --db mydb.db
  ```

## Contributing
Pull requests and feature suggestions are welcome! See the documentation and feature tracker for details.

## License
MIT License
