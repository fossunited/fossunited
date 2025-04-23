#!/bin/bash
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

