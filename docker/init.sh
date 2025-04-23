#!/bin/bash
# This script uses the user's original logic flow but adds robustness checks
# and ensures commands run in the correct directory.
# v3: Removed 'rm -rf' attempt on the volume mount point.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration Variables ---
BENCH_DIR_NAME="frappe-bench" # The name of the bench directory
BENCH_DIR_PATH="/home/frappe/${BENCH_DIR_NAME}"
PROCFILE_PATH="${BENCH_DIR_PATH}/Procfile" # Define path to Procfile for checking
SITE_NAME="fossunited.localhost"
APP_NAME="fossunited"
APP_REPO="${APP_REPO:-https://github.com/fossunited/fossunited}"
BRANCH_NAME="${BRANCH_NAME:-develop}"
ADMIN_PASSWORD="admin"
MARIADB_ROOT_PASSWORD="123" # Should match docker-compose environment

echo "--- Frappe Bench Initialization Script ---"

# Check if the Procfile exists within the bench directory.
# This is a better indicator that 'bench init' has completed successfully.
if [ -f "${PROCFILE_PATH}" ]; then
    echo "Procfile found at '${PROCFILE_PATH}'. Assuming bench is initialized, skipping init."

    # Navigate into the bench directory before starting
    cd "${BENCH_DIR_PATH}"
    echo "Current directory: $(pwd)"
    echo "Starting bench services..."
    bench start

else
    echo "Procfile not found at '${PROCFILE_PATH}'. Creating new bench..."

    # Navigate to the parent directory to run 'bench init'
    cd /home/frappe
    echo "Current directory before init: $(pwd)"

    # If the directory exists (due to volume mount) but Procfile is missing,
    # bench init should populate it. We no longer try to remove it.
    if [ -d "${BENCH_DIR_PATH}" ]; then
        echo "WARN: Bench directory '${BENCH_DIR_PATH}' exists but Procfile is missing. Proceeding with bench init to populate it."
    fi

    # 'set -e' will stop the script if bench init fails.
    echo "Running 'bench init ${BENCH_DIR_NAME}'..."
    bench init --ignore-exist --skip-redis-config-generation "${BENCH_DIR_NAME}"
    echo "Bench init completed."

    # Navigate into the newly created/populated bench directory
    cd "${BENCH_DIR_PATH}"
    echo "Current directory after cd into bench: $(pwd)"

    # Verify Procfile exists now before proceeding
    if [ ! -f "./Procfile" ]; then
        echo "ERROR: Procfile still not found after bench init in $(pwd)! Aborting."
        ls -la # Show directory contents for debugging
        exit 1
    fi
    echo "Procfile successfully created by bench init."

    echo "Setting container-specific hosts (inside ${BENCH_DIR_PATH})..."
    # Use service names from docker-compose
    bench set-mariadb-host mariadb
    bench set-redis-cache-host redis://redis:6379
    bench set-redis-queue-host redis://redis:6379
    bench set-redis-socketio-host redis://redis:6379

    echo "Modifying Procfile (inside ${BENCH_DIR_PATH})..."
    # Remove redis and watch services as they are handled by separate containers/compose setup
    sed -i '/redis/d' ./Procfile || true # Using /redis/ should catch all redis entries
    sed -i '/watch/d' ./Procfile || true

    echo "Getting custom app '${APP_NAME}' from ${APP_REPO} (inside ${BENCH_DIR_PATH})..."
    bench get-app --resolve-deps "${APP_REPO}" --branch ${BRANCH_NAME}

    # Check if the site already exists (idempotency)
    if [ -d "sites/${SITE_NAME}" ]; then
        echo "Site '${SITE_NAME}' directory already exists, skipping 'bench new-site'."
        # Ensure the site is added to sites.txt if it exists but wasn't added before
        # Check if sites.txt exists first
        if [ -f "sites/sites.txt" ] && ! grep -qF "${SITE_NAME}" sites/sites.txt; then
            echo "${SITE_NAME}" >> sites/sites.txt
            echo "Added existing site ${SITE_NAME} to sites.txt"
        elif [ ! -f "sites/sites.txt" ]; then
             echo "${SITE_NAME}" > sites/sites.txt # Create sites.txt if it doesn't exist
             echo "Created sites.txt and added site ${SITE_NAME}"
        fi
    else
        echo "Creating new site '${SITE_NAME}' (inside ${BENCH_DIR_PATH})..."
        bench new-site "${SITE_NAME}" \
            --force \
            --mariadb-root-password "${MARIADB_ROOT_PASSWORD}" \
            --admin-password "${ADMIN_PASSWORD}" \
            --no-mariadb-socket
    fi

    echo "Applying site configurations (inside ${BENCH_DIR_PATH})..."
    bench set-config -g server_script_enabled 1

    # Check if app is already installed (idempotency)
    if bench --site "${SITE_NAME}" list-apps | grep -q "^${APP_NAME}$"; then
       echo "App '${APP_NAME}' already installed on site '${SITE_NAME}'."
    else
       echo "Installing app '${APP_NAME}' on site '${SITE_NAME}'..."
       bench --site "${SITE_NAME}" install-app "${APP_NAME}"
    fi

    bench --site "${SITE_NAME}" set-config developer_mode 1
    bench --site "${SITE_NAME}" set-config mute_emails 1
    bench --site "${SITE_NAME}" clear-cache

    echo "Setting default site to '${SITE_NAME}' (inside ${BENCH_DIR_PATH})..."
    bench use "${SITE_NAME}"

    echo "Bench initialization and site setup complete."
    echo "Starting bench services (inside ${BENCH_DIR_PATH})..."
    bench start
fi

