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
- `fm create foss.localhost`
- `fm start` choose site as it shows in menu
- `fm shell` (enter into docker container shell and run further steps there)
- `bench get-app https://github.com/fossunited/fossunited.git`
- `bench install-app fossunited` - This will also install dashboard
- Also please configure frappe for server scripts and running tests
  - `bench set-config -g server_script_enabled true`

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
bench get-app https://github.com/frappe/newsletter
bench install-app newsletter
```

> Related discussion: [#1120](https://github.com/fossunited/fossunited/issues/1120)

##### Install FOSS United App

```sh
# Get the app
bench get-app https://github.com/fossunited/fossunited

# Create a new site
bench new-site test.localhost

# Install the app on the site
bench --site test.localhost install-app fossunited

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
- [Vale]((https://vale.sh)) is used for spell check and grammar check for docs content.


```sh
uv add pre-commit
pre-commit install
```

Or use [uv](https://github.com/astral-sh/uv) as an alternative Python package manager.

---

## Useful Links

* [FOSS United GitHub repo](https://github.com/fossunited/fossunited)
* [Frappe Docs](https://frappeframework.com/docs/)
* [Create a Site Guide](https://frappeframework.com/docs/user/en/tutorial/create-a-site)

---

Happy hacking! If you face issues, open a [GitHub issue](https://github.com/fossunited/fossunited/issues/) or join the [FOSS United community](https://forum.fossunited.org/) for help.
