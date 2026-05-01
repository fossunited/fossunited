#!/bin/bash

cd /home/frappe || exit 1

# Check for existence of the FOSS United Bench, if not create one
if [ -d "fossu-bench/Procfile" ]; then
    cd fossu-bench || exit 1
    bench start
    exit 0
else
    echo "FOSS United Bench not found, creating a new one..."
    /workspace/development/installer.py --site-name fossunited.localhost \
    --apps-json "/workspace/development/${APPS_JSON:-apps.json}" \
    --bench-name fossu-bench \
    --admin-password admin
    
    cd fossu-bench || exit 1
    
    # Build Dashboard if in demo mode
    if [ "$DEMO_MODE" = "1" ]; then
        echo "Building Dashboard..."
        cd apps/fossunited/dashboard || exit 1
        yarn install
        yarn build
        cd ../../../
    fi

    # Seed data if in demo mode
    if [ "$DEMO_MODE" = "1" ]; then
        echo "Seeding demo data..."
        bench --site fossunited.localhost execute fossunited.dev.seed.seed
    fi

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
