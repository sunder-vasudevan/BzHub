#!/bin/bash
# Auto-activate venv and run BizHub app, ensuring supabase-py is available

# Activate venv if not already active
if [ -z "$VIRTUAL_ENV" ]; then
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  else
    echo "Virtual environment not found. Please create one with 'python3 -m venv .venv' and install requirements."
    exit 1
  fi
fi

# Check for supabase-py
if ! pip show supabase-py > /dev/null 2>&1 && ! pip show supabase > /dev/null 2>&1; then
  echo "supabase-py is not installed in the active environment. Please install it with 'pip install supabase-py'"
  exit 1
fi


# Run the app
python3 scripts/bizhub.py
