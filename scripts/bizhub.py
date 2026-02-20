#!/usr/bin/env python3
"""Bzhub - Complete ERP Suite for Small Businesses.

Usage:
    python bizhub.py          # Run desktop Tkinter app (default)
    python bizhub.py --web    # Run web interface (future)
    python bizhub.py --help   # Show help
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from src.config import MODE, APP_NAME, APP_VERSION


def main():
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION} - Complete ERP Suite for Small Businesses"
    )
    parser.add_argument('--web', action='store_true', help='Run web interface (future)')
    parser.add_argument('--api', action='store_true', help='Run API server (future)')
    parser.add_argument('--db', default='inventory.db', help='Database file path')
    parser.add_argument('--version', action='version', version=f"{APP_NAME} {APP_VERSION}")
    
    args = parser.parse_args()
    
    try:
        if args.api:
            print("API mode not yet implemented")
            sys.exit(1)
        elif args.web:
            print("Web mode not yet implemented")
            sys.exit(1)
        else:
            # Desktop mode (default)
            import tkinter as tk
            from src.ui.desktop.bizhub_desktop import BizHubDesktopApp
            
            root = tk.Tk()
            app = BizHubDesktopApp(root, db_file=args.db)
            root.mainloop()
    
    except Exception as e:
        print(f"Error starting {APP_NAME}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
