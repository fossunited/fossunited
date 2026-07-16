#!/bin/bash
export APPS_JSON=apps-local.json
export DEMO_MODE=1

echo "Starting Reviewer Workflow Demo..."
echo "This will setup a local Frappe bench, build the dashboard, and seed demo data."
echo "Access the site at: http://fossunited.localhost:8000"
echo "Login with: reviewer@example.com / password (or create your own)"

if command -v podman-compose >/dev/null 2>&1; then
    COMPOSE="podman-compose"
else
    COMPOSE="docker compose"
fi

$COMPOSE -f .devcontainer/docker-compose.yml up -d frappe mariadb redis-cache redis-queue
$COMPOSE -f .devcontainer/docker-compose.yml exec frappe /workspace/development/init.sh
