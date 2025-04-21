#!bin/bash

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists, skipping init"
    cd frappe-bench
    bench start
else
    echo "Creating new bench..."
fi

bench init --skip-redis-config-generation frappe-bench --version version-15

cd frappe-bench

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove redis, watch from Procfile
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

bench get-app --resolve-deps https://github.com/fossunited/fossunited

bench new-site fossunited.localhost \
--force \
--mariadb-root-password 123 \
--admin-password admin \
--no-mariadb-socket

bench set-config -g server_script_enabled 1
bench --site fossunited.localhost install-app fossunited
bench --site fossunited.localhost set-config developer_mode 1
bench --site fossunited.localhost set-config mute_emails 1
bench --site fossunited.localhost clear-cache
bench use fossunited.localhost

bench start