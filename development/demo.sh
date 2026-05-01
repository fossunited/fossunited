#!/bin/bash
export APPS_JSON=apps-local.json
export DEMO_MODE=1

echo "Starting Reviewer Workflow Demo..."
echo "This will setup a local Frappe bench, build the dashboard, and seed demo data."
echo "Access the site at: http://fossunited.localhost:8000"
echo "Login with: reviewer@example.com / password (see docs/docs/development.md for all credentials)"

podman-compose -f .devcontainer/docker-compose.yml up -d frappe mariadb redis-cache redis-queue
podman-compose -f .devcontainer/docker-compose.yml exec frappe /workspace/development/init.sh
