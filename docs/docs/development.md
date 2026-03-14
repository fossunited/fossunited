# FOSS United Platform – Developer Guide

The **FOSS United Platform** is developed and maintained by the [FOSS United Foundation](https://fossunited.org/), with ongoing contributions from the community. Development takes place on [GitHub](https://github.com/fossunited/fossunited).

> **Note:** We welcome contributions from anyone. Join us by submitting issues, feature requests, or pull requests!

---

## Installation Guide

> **Recommended Frappe Version:** v15+

### Recommended: Setup & Quick-start
Our recommended setup is via [docker](https://www.docker.com/) + [frappe manager](https://github.com/rtCamp/Frappe-Manager).

- Install [`uv`](https://github.com/astral-sh/uv) python manager and `docker`
- `uv init` in a new directory
- `uv add frappe-manager`
- `uv run fm create foss.localhost`
- `uv run fm start` — choose site as it shows in menu
- `uv run fm shell` — enter into docker container shell and run further steps there
- `bench get-app https://github.com/fossunited/fossunited.git`
- `bench --site foss.localhost install-app fossunited` — this will also install dashboard
- Configure frappe for server scripts and developer mode:
  - `bench set-config -g server_script_enabled true`
  - `bench --site foss.localhost set-config developer_mode 1`
  - `bench --site foss.localhost migrate`

- To run tests please create new-site since it can have unintended DB changes.
  - `bench new-site break.site`
  - `bench --site break.site set-config allow_tests true`

- Open `foss.localhost` in your browser and start exploring!
- Dashboard page can be accessed via `foss.localhost/dashboard`

Note: Since dashboard is not running as live dev server, you'd need to `bench build --apps fossunited` for changes to update.

If you would prefer for manual method, please follow on below

### Manual Install

#### 1. Prerequisites
- Set up your environment using the [official Frappe installation guide](https://frappeframework.com/docs/).
- If you encounter a **MariaDB password issue**, refer to [this DigitalOcean guide](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password) to reset your root password.

If the `kill` command fails:
```sh
ps aux | grep mysqld
sudo kill -9 <pid_of_mysqld> <pid_of_mysql_safe>
```

Ensure MySQL processes are fully stopped before restarting.

---

#### 2. Setup Steps

```sh
# Create a new bench
bench init fossu-bench
cd fossu-bench
```

##### Install Newsletter App

For frappe >= v16, the **Newsletter** module has been moved as an separate app. Install it *before* `fossunited`:

```sh
bench new-site foss.localhost
bench get-app https://github.com/frappe/newsletter
bench --site foss.localhost install-app newsletter
```

> Related discussion: [#1120](https://github.com/fossunited/fossunited/issues/1120)

##### Install FOSS United App

```sh
# Get the app
bench get-app https://github.com/fossunited/fossunited

# Install the app on the site
bench --site foss.localhost install-app fossunited
bench --site foss.localhost set-config developer_mode 1
bench --site foss.localhost migrate

# Start development server
bench start
```

> To access the site in your browser, follow:
> [Access Site via Browser](https://frappeframework.com/docs/user/en/tutorial/create-a-site#access-site-in-your-browser)

---

### NixOS Setup

For those using **NixOS**, refer to this guide ==> [Issue #1068 – NixOS Setup Guide](https://github.com/fossunited/fossunited/issues/1068) to get going.

---

## FOSS United Dashboard

The **Dashboard** is an admin UI for volunteers to manage activities across FOSS Clubs and City Chapters.

### Dashboard Setup

```sh
# Go to the dashboard directory
cd fossunited/dashboard

# Install dependencies
yarn install
```

#### Required Configuration

In your `site_config.json`, add the following:

```json
{
  "ignore_csrf": 1
}
```

#### Run the Dashboard

```sh
yarn dev
```

The dashboard will be available at:
==> `http://<your-site-name>:8080`

---

## Pre-commit Hooks

To automatically run linters before commits:

- We use [ruff](https://docs.astral.sh/ruff/) for linting python files. It is recommended to use [prettier](https://prettier.io/) for formatting HTML, CSS & Vue files.
- [Vale](https://vale.sh) is used for spell check and grammar check for docs content.


```sh
uv add pre-commit
pre-commit install
```

Or use [uv](https://github.com/astral-sh/uv) as an alternative Python package manager.

---

## Troubleshooting

### Common Issues

- **MariaDB root password error** — follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password) to reset it
- **Site shows errors after install** — make sure you ran `bench --site foss.localhost migrate`
- **Server scripts not running** — verify `server_script_enabled` is set to `true`
- **`tatsu` crash during install** — a recent `tatsu` release is broken. Fix it by downgrading and using `--force`:

```bash
./env/bin/pip install "tatsu<5.10.0"
bench --site foss.localhost install-app --force fossunited
```

> See [#1320](https://github.com/fossunited/fossunited/issues/1320) for more context on this issue.

---

### macOS + Colima Setup

If you're using Colima instead of Docker Desktop, here are the fixes for the common errors you'll hit:

**1. Docker socket not found**
```bash
sudo ln -sfn ~/.colima/default/docker.sock /var/run/docker.sock
```

**2. Missing Compose plugin**
```bash
mkdir -p ~/.docker/cli-plugins
ln -sfn $(which docker-compose) ~/.docker/cli-plugins/docker-compose
```

**3. UID 1000 crash**
```bash
SITE_PKGS="$(uv run python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
find "$SITE_PKGS/frappe_manager" -type f -name "*.py" -exec sed -i '' 's/os.getuid()/1000/g' {} +
find "$SITE_PKGS/frappe_manager" -type f -name "*.py" -exec sed -i '' 's/os.getgid()/1000/g' {} +
```

**4. uv install failing (os error 1)**

Run these inside `fm shell` before `bench get-app`:
```bash
export UV_CACHE_DIR=/tmp/uv_cache
export UV_LINK_MODE=copy
```

**5. Dashboard build crash (exit code 137)**

Colima's default RAM is too low for the Vite build. Restart with more resources:
```bash
colima start --cpu 4 --memory 8
```

> Full discussion and all fixes: [#1320](https://github.com/fossunited/fossunited/issues/1320)

---

## Useful Links

* [FOSS United GitHub repo](https://github.com/fossunited/fossunited)
* [Frappe Docs](https://frappeframework.com/docs/)
* [Create a Site Guide](https://frappeframework.com/docs/user/en/tutorial/create-a-site)

---

Happy hacking! If you face issues, open a [GitHub issue](https://github.com/fossunited/fossunited/issues/) or join the [FOSS United community](https://forum.fossunited.org/) for help.
