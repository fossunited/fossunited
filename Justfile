# Justfile for FOSS United CFP Review Workflow

# Container Engine Autodetection
DOCKER := `command -v podman >/dev/null 2>&1 && echo podman || echo docker`

# docker-compose binary — override with COMPOSE_BIN env var if needed
COMPOSE_BIN := env_var_or_default("COMPOSE_BIN", `command -v podman-compose >/dev/null 2>&1 && echo "podman-compose" || echo "docker compose"`)
COMPOSE_CMD := COMPOSE_BIN + " -f .devcontainer/docker-compose.yml"

# Default recipe: list all available recipes
default:
    @just --list

# Start the {{DOCKER}} compose services in the background.
# Self-heals from the netavark stale-namespace error that occurs after a reboot/sleep:
# if `up` fails, stuck containers and the stale network are removed and `up` is retried once.
up:
    #!/usr/bin/env bash
    set -euo pipefail
    COMPOSE="{{ COMPOSE_CMD }}"
    if ! $COMPOSE up -d 2>&1; then
        echo "⚠️  compose up failed — cleaning up stale containers and network, then retrying..."
        # Force-remove any containers that failed to clean their network namespace
        {{ DOCKER }} ps -a --format '{{{{.Names}}}}' \
            | grep '^devcontainer-' \
            | xargs {{ DOCKER }} rm -f 2>/dev/null || true
        # Remove the stale bridge network
        {{ DOCKER }} network rm devcontainer_default 2>/dev/null || true
        echo "🔄  Retrying compose up..."
        $COMPOSE up -d
    fi

# Stop the {{DOCKER}} compose services
down:
    {{ COMPOSE_CMD }} down

# Initialize or reset the local Frappe site from the mounted workspace.
# Also installs setuptools<80 to restore pkg_resources on Python 3.14.
setup: up
    #!/usr/bin/env bash
    set -euo pipefail
    COMPOSE="{{ COMPOSE_CMD }}"
    BENCH_DIR="/workspace/development/fossu-bench"

    echo "⏳ Waiting for MariaDB to be ready..."
    until $COMPOSE exec -T mariadb \
            mariadb -u root -p123 -e "SELECT 1" &>/dev/null; do
        sleep 2
    done
    echo "✅ MariaDB is ready."

    if ! $COMPOSE exec -T frappe \
            test -d "$BENCH_DIR/apps/frappe/frappe" -a -f "$BENCH_DIR/sites/common_site_config.json"; then
        echo "🛠️  Creating Frappe bench..."
        $COMPOSE exec -T -u root frappe bash -c '
            if [ -e /workspace/development/fossu-bench ]; then
                mv /workspace/development/fossu-bench \
                    "/tmp/fossu-bench.incomplete.$(date +%s)"
            fi
            mkdir -p /workspace/development/fossu-bench
            chown frappe:frappe /workspace/development/fossu-bench
        '
        $COMPOSE exec -T -w /workspace/development frappe bash -lc '
            bench init --ignore-exist --frappe-branch version-15 --skip-redis-config-generation fossu-bench
        '
    fi

    $COMPOSE exec -T -u root frappe chown -R frappe:frappe "$BENCH_DIR"
    $COMPOSE exec -T -w "$BENCH_DIR" frappe bash -lc '
        set -euo pipefail
        bench set-config -g db_type mariadb
        bench set-config -g db_host mariadb
        bench set-config -g redis_cache redis://redis-cache:6379
        bench set-config -g redis_queue redis://redis-queue:6379
        bench set-config -g redis_socketio redis://redis-queue:6379
        bench set-config -gp developer_mode 1
        env/bin/pip install "setuptools<80" --quiet

        # Keep a small physical app directory for Bench asset builds. esbuild resolves
        # app-root symlinks and breaks fossunited imports that reference sibling apps.
        if [ -L apps/fossunited ]; then
            unlink apps/fossunited
        elif [ -e apps/fossunited ] && [ ! -d apps/fossunited/fossunited ]; then
            mv apps/fossunited "apps/fossunited.incomplete.$(date +%s)"
        fi
        mkdir -p apps/fossunited/fossunited
        env/bin/pip install --quiet --editable /workspace
        touch sites/apps.txt
        grep -qx fossunited sites/apps.txt || echo fossunited >> sites/apps.txt
        if [ ! -d apps/frappe_factory_bot ]; then
            bench get-app --skip-assets --branch main https://github.com/harshtandiya/frappe_factory_bot
        fi

        if [ -f sites/fossunited.localhost/site_config.json ]; then
            bench --site fossunited.localhost reinstall --mariadb-root-password 123 --admin-password admin --yes
        else
            bench new-site fossunited.localhost \
                --db-root-password 123 \
                --admin-password admin \
                --mariadb-user-host-login-scope=%
        fi

        for app in frappe_factory_bot fossunited; do
            if ! bench --site fossunited.localhost list-apps --format text | grep -qx "$app"; then
                bench --site fossunited.localhost install-app "$app"
            fi
        done
        bench --site fossunited.localhost migrate
    '
    # Older branches may still need the local schema compatibility patch.
    if $COMPOSE exec -T frappe test -f /workspace/development/patch_schema.py; then
        $COMPOSE exec -T -w "$BENCH_DIR/sites" frappe \
            ../env/bin/python /workspace/development/patch_schema.py
    fi

# Seed demo data into the site.
# Uses a standalone Python script to bypass `bench execute`'s eval() namespace bug
# on Python 3.14 where dotted module paths like fossunited.dev.seed.seed fail to resolve.
seed:
    {{ COMPOSE_CMD }} exec -T -w /workspace/development/fossu-bench/sites frappe \
        ../env/bin/python /workspace/development/run_seed.py

# Build the dashboard frontend and flush Frappe's asset cache.
# Builds the dashboard from the mounted workspace, then mirrors public sources for Bench's asset compiler.
build-dashboard:
    #!/usr/bin/env bash
    set -euo pipefail
    COMPOSE="{{ COMPOSE_CMD }}"
    $COMPOSE exec -T -u root -w /workspace frappe bash -lc '
        set -euo pipefail
        export NVM_DIR=/home/frappe/.nvm
        . "$NVM_DIR/nvm.sh"
        yarn install --frozen-lockfile
        yarn --cwd dashboard vite build \
            --base=/assets/fossunited/dashboard/ \
            --outDir=/workspace/fossunited/public/dashboard \
            --emptyOutDir
        cp /workspace/fossunited/public/dashboard/index.html \
            /workspace/fossunited/www/dashboard.html
    '
    # Mirror public sources into a physical app path so Frappe's esbuild can resolve sibling apps.
    $COMPOSE exec -T -u root -w /workspace/development/fossu-bench frappe bash -lc '
        mkdir -p apps/fossunited/fossunited/public
        cp -a /workspace/fossunited/public/. apps/fossunited/fossunited/public/
        if [ -L apps/fossunited/node_modules ]; then
            unlink apps/fossunited/node_modules
        fi
        mkdir -p apps/fossunited/node_modules/@knadh
        cp -a /workspace/node_modules/@knadh/. apps/fossunited/node_modules/@knadh/
        if [ -L /workspace/fossunited/public/node_modules ]; then
            unlink /workspace/fossunited/public/node_modules
        fi
        chown -R frappe:frappe apps/fossunited
    '
    # Keep the root install out of Frappe's asset copy; the app shim has its required dependency.
    NODE_MODULES_HOLD="/workspace/.node_modules.just-build.$$"
    $COMPOSE exec -T -u root frappe \
        mv /workspace/node_modules "$NODE_MODULES_HOLD"
    restore_node_modules() {
        $COMPOSE exec -T -u root frappe \
            mv "$NODE_MODULES_HOLD" /workspace/node_modules
    }
    trap restore_node_modules EXIT
    $COMPOSE exec -T -w /workspace/development/fossu-bench frappe \
        bash -lc 'CI=1 bench build --hard-link --app fossunited'
    restore_node_modules
    trap - EXIT
    $COMPOSE exec -T -w /workspace/development/fossu-bench frappe bench --site fossunited.localhost clear-cache

# Clear Frappe's server-side cache (run after any backend change)
clear-cache:
    {{ COMPOSE_CMD }} exec -T -w /workspace/development/fossu-bench frappe bench --site fossunited.localhost clear-cache

# Start the Frappe bench (runs in foreground)
# Kills any stale socketio process on :9000 first (left over from a previous unclean stop)
start:
    -{{ COMPOSE_CMD }} exec -T frappe pkill -f 'realtime/index' 2>/dev/null
    {{ COMPOSE_CMD }} exec -w /workspace/development/fossu-bench frappe bench start

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
    {{ COMPOSE_CMD }} exec frappe bash

# Install the git pre-commit hook and run all checks against every file
lint:
    pre-commit install
    pre-commit run --all-files

# View container logs
logs:
    {{ COMPOSE_CMD }} logs -f

# Serve the Zensical docs site locally (see package.json for the actual command)
docs:
    yarn docs

# Run the Bruno API test collection
alias bruno := bru
bru:
    yarn bru

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
