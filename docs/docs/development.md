# FOSS United Platform – Developer Guide

The **FOSS United Platform** is developed and maintained by the [FOSS United Foundation](https://fossunited.org/), with ongoing contributions from the community. Development takes place on [GitHub](https://github.com/fossunited/fossunited).

> **Note:** We welcome contributions from developers. Join us by submitting issues, feature requests, or pull requests!

---

## Installation Guide

> **Recommended Frappe Version:** v15+

### 1. Prerequisites
- Set up your environment using the [official Frappe installation guide](https://frappeframework.com/docs/).
- If you encounter a **MariaDB password issue**, refer to [this DigitalOcean guide](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password) to reset your root password.

If the `kill` command fails:
```sh
ps aux | grep mysqld
sudo kill -9 <pid_of_mysqld> <pid_of_mysql_safe>
```

Ensure MySQL processes are fully stopped before restarting.

---

### 2. Setup Steps

```sh
# Create a new bench
bench init fossu-bench
cd fossu-bench
```

#### Install Newsletter App

The **Newsletter** module is now a separate app. Install it *before* `fossunited`:

```sh
bench get-app https://github.com/frappe/newsletter
bench install-app newsletter
```

> Related discussion: [#1120](https://github.com/fossunited/fossunited/issues/1120)

#### Install FOSS United App

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

## NixOS Setup

For those using **NixOS**, refer to this guide by @idlip:
==> [Issue #1068 – NixOS Setup Guide](https://github.com/fossunited/fossunited/issues/1068)

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

```sh
pip install pre-commit
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
