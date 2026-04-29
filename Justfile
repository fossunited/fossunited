# Justfile for FOSS United CFP Review Workflow

# Default recipe: list all available recipes
default:
    @just --list

# Start the podman compose services in the background.
# Self-heals from the netavark stale-namespace error that occurs after a reboot/sleep:
# if `up` fails, stuck containers and the stale network are removed and `up` is retried once.
up:
    #!/usr/bin/env bash
    set -euo pipefail
    COMPOSE="/home/linuxbrew/.linuxbrew/bin/docker-compose -f .devcontainer/docker-compose.yml"
    if ! $COMPOSE up -d 2>&1; then
        echo "⚠️  compose up failed — cleaning up stale containers and network, then retrying..."
        # Force-remove any containers that failed to clean their network namespace
        podman ps -a --format '{{{{.Names}}' \
            | grep '^devcontainer-' \
            | xargs -r podman rm -f 2>/dev/null || true
        # Remove the stale bridge network
        podman network rm devcontainer_default 2>/dev/null || true
        echo "🔄  Retrying compose up..."
        $COMPOSE up -d
    fi

# Stop the podman compose services
down:
    /home/linuxbrew/.linuxbrew/bin/docker-compose -f .devcontainer/docker-compose.yml down

# Initialize the Frappe site: fix permissions, reinstall DB, register & install the fossunited app.
# Also installs setuptools<80 to restore pkg_resources on Python 3.14.
setup:
    podman exec -u root devcontainer-frappe-1 chown -R frappe:frappe /workspace/development/fossu-bench
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench --site fossunited.localhost reinstall --mariadb-root-password 123 --admin-password admin --yes
    # Ensure fossunited is in the bench app registry (bench reinstall wipes sites/apps.txt)
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 \
        bash -c "grep -qx fossunited sites/apps.txt 2>/dev/null || printf 'frappe\nfossunited\n' > sites/apps.txt"
    # Python 3.14 dropped pkg_resources from setuptools 80+; pin to a version that still has it
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 \
        bash -c "env/bin/pip install 'setuptools<80' --quiet 2>/dev/null || true"
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench --site fossunited.localhost install-app fossunited
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench --site fossunited.localhost migrate
    # Patch: migrate doesn't add parent/parentfield/parenttype to FOSS Event CFP Review
    # because it is both a standalone and a child doctype (see development/patch_schema.py).
    podman exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/development/patch_schema.py

# Seed demo data into the site.
# Uses a standalone Python script to bypass `bench execute`'s eval() namespace bug
# on Python 3.14 where dotted module paths like fossunited.dev.seed.seed fail to resolve.
seed:
    podman exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/development/run_seed.py

# Build the dashboard frontend and flush Frappe's asset cache.
# IMPORTANT: builds from /workspace/dashboard (host repo with our edits).
# The bench has a stale separate copy at apps/fossunited/ — do NOT build from there.
build-dashboard:
    # Use root inside to map to host user (james) for correct ownership
    podman exec -u root -w /workspace/dashboard devcontainer-frappe-1 yarn install
    podman exec -u root -w /workspace/dashboard devcontainer-frappe-1 yarn build
    # vite outputs to fossunited/public/dashboard/ (package-relative).
    # Sync entry point to www/ (also owned by host user).
    podman exec -u root devcontainer-frappe-1 \
        bash -c "mkdir -p /workspace/www /workspace/fossunited/public/dist/js && \
                 cp /workspace/fossunited/public/dashboard/index.html \
                    /workspace/www/dashboard.html"
    # Rebuild Frappe's website bundle and flush caches
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench build --app fossunited
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench --site fossunited.localhost clear-cache

# Clear Frappe's server-side cache (run after any backend change)
clear-cache:
    podman exec -w /workspace/development/fossu-bench devcontainer-frappe-1 bench --site fossunited.localhost clear-cache

# Start the Frappe bench (runs in foreground)
# Kills any stale socketio process on :9000 first (left over from a previous unclean stop)
start:
    -podman exec devcontainer-frappe-1 pkill -f 'realtime/index' 2>/dev/null
    podman exec -it -w /workspace/development/fossu-bench devcontainer-frappe-1 bench start

# Day-to-day dev startup: bring up containers, open the dashboard, start the bench.
# Safe to run at any time — 'up' is a no-op if containers are already running.
# Use 'just demo' first if you need a full reset with fresh seed data.
dev: up
    @xdg-open http://fossunited.localhost:8000/dashboard 2>/dev/null || true
    just start

# Alias for dev
launch: dev

# Open a shell inside the frappe container
shell:
    podman exec -it devcontainer-frappe-1 bash

# View container logs
logs:
    /home/linuxbrew/.linuxbrew/bin/docker-compose -f .devcontainer/docker-compose.yml logs -f

# Complete demo setup: up → setup → seed → build-dashboard → ready to start
# This is the one-click local demo deploy. Run 'just start' (or 'just launch') afterwards.
demo: up
    just setup
    just seed
    just build-dashboard
    @echo ""
    @echo "✅ Demo setup complete! Run 'just start' to launch the bench."
    @echo ""
    @echo "Demo accounts (all passwords: 'password'):"
    @echo "  Reviewer      mock-reviewer@example.com"
    @echo "  Chapter leads mock-bangalore-lead@example.com"
    @echo "                mock-mumbai-lead@example.com"
    @echo "                mock-kochi-lead@example.com"
    @echo "                mock-campus-lead@example.com"
    @echo "  Speakers      mock-speaker-1@example.com"
    @echo "                mock-speaker-2@example.com"
    @echo "  Attendees     mock-attendee-1@example.com"
    @echo "                mock-attendee-2@example.com"
    @echo "  Admin         Administrator / admin"
