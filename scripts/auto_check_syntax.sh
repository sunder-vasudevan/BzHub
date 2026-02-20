#!/bin/bash
# Auto-check Python syntax and indentation after every file change

changed_file="$1"

if [[ "$changed_file" == *.py ]]; then
    python -m py_compile "$changed_file"
    if [[ $? -ne 0 ]]; then
        echo "Syntax or indentation error detected in $changed_file"
        exit 1
    fi
fi
