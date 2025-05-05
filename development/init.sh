#!/bin/bash

# Check for existence of the FOSS United Bench, if not create one
if [ -d "fossu-bench/Procfile" ]; then
    cd fossu-bench
    bench start
    exit 0
else
    echo "FOSS United Bench not found, creating a new one..."
    ./installer.py --site-name fossunited.localhost \
    --apps-json apps.json \
    --bench-name fossu-bench \
    --admin-password admin
    cd fossu-bench
    code -a fossu-bench/apps/fossunited
    bench start
    exit 0
fi

# check if pre-commit is installed and enabled at .git/hooks/pre-commit
if ! command -v pre-commit &> /dev/null; then
    pip install pre-commit
fi

if [ -f ".git/hooks/pre-commit" ]; then
    echo "pre-commit is already installed"
else
    echo "Installing pre-commit..."
    pre-commit install
fi
