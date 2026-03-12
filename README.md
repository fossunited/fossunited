<div align="center">
    <img alt="FOSS United logo" src=".github/logo.png" width="150px" height="120px">
</div>

<p align="center">
<a href="https://docs.fossunited.org/">
<img src="https://img.shields.io/badge/FOSSUnited-Docs-lightgreen?style=for-the-badge&labelColor=black" alt="FOSS United Docs website badge">
</a>
<a href="https://frappe.io/framework/">
<img src="https://img.shields.io/badge/Frappe-framework-blue?style=for-the-badge&logo=frappe&labelColor=black" alt="Badge for Frappe, for backend framework">
</a>
<a href="https://vuejs.org/">
<img src="https://img.shields.io/badge/Vue.js-dashboard-42b883?style=for-the-badge&logo=vuedotjs&labelColor=black" alt="Badge for Vue.js, used for building dashboard frontend">
</a>
<a href="https://tailwindcss.com/">
<img src="https://img.shields.io/badge/TailwindCSS-dashboard-38bdf8?style=for-the-badge&logo=tailwindcss&labelColor=black" alt="Badge for TailwindCSS, used for styling components">
</a>
</p>


## The FOSS United Platform

Project repo for the website and open-source platform of FOSS United. The whole platform is being built on [Frappe](https://frappe.io).

Read more at [https://docs.fossunited.org/](https://docs.fossunited.org/)

## Installation

This guide explains how to set up the project locally for development.
You can either use the recommended Docker setup or install everything manually using Frappe Bench.

> Recommended Frappe version: v15+

### Prerequisites

- Git
- Python 3.11+
- Node.js 18+ and `yarn`
- MariaDB 10.6+ (manual install) or Docker (recommended path)
- Frappe Bench CLI — `pip install frappe-bench`
- `uv` — [astral-sh/uv](https://github.com/astral-sh/uv)

---

### Option A: Recommended Setup (Docker + frappe-manager)

This uses [frappe-manager](https://github.com/rtCamp/Frappe-Manager) to spin up a Docker-based bench — no manual MariaDB setup needed.
```bash
mkdir fossu-dev && cd fossu-dev
uv init
uv add frappe-manager
fm create foss.localhost
fm start        # start the container and select your site from the menu
fm shell        # enter the container shell
```

Inside the container:
```bash
bench get-app https://github.com/fossunited/fossunited.git
bench install-app fossunited
bench --site foss.localhost set-config developer_mode 1
bench set-config -g server_script_enabled true
bench --site foss.localhost migrate
```

Open `http://foss.localhost` in your browser.

> Dashboard is at `http://foss.localhost/dashboard`. Run `bench build --apps fossunited` after making dashboard changes since it doesn't run as a live dev server.

---

### Option B: Manual Install

If you prefer not to use Docker, you can set everything up directly on your machine.
First follow the [official Frappe installation guide](https://frappeframework.com/docs/) to get MariaDB and the bench CLI ready.
```bash
bench init fossu-bench
cd fossu-bench
```

**If you're on Frappe v16+**, install the Newsletter app first (it was split into a separate app in v16):
```bash
bench get-app https://github.com/frappe/newsletter
bench install-app newsletter
```

Then install FOSS United:
```bash
bench get-app https://github.com/fossunited/fossunited
bench new-site foss.localhost
bench --site foss.localhost install-app fossunited
bench --site foss.localhost set-config developer_mode 1
bench set-config -g server_script_enabled true
bench --site foss.localhost migrate
bench start
```

Open `http://foss.localhost:8000` in your browser.

---

### Dashboard Setup

Only needed if you're working on dashboard features — skip this otherwise.
```bash
cd fossunited/dashboard
yarn install
```

Add `"ignore_csrf": 1` to your `site_config.json`, then:
```bash
yarn dev
```

Dashboard runs at `http://<your-site-name>:8080`.

---

### Running Tests

Create a separate site for tests to avoid unintended DB changes:
```bash
bench new-site test.localhost
bench --site test.localhost set-config allow_tests true
bench --site test.localhost run-tests --app fossunited
```

---

### Troubleshooting

- **MariaDB root password error** — follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password) to reset it
- **bench start fails on port 8000** — run `lsof -i :8000` to find and kill the process using it
- **Site shows errors after install** — make sure you ran `bench --site foss.localhost migrate`
- **Server scripts not running** — verify `server_script_enabled` is `true` in your bench config

Still stuck? Open a [GitHub issue](https://github.com/fossunited/fossunited/issues) or ask on the [FOSS United forum](https://forum.fossunited.org/).

## Pre-commit

For automatic running of linters before you commit:

- We use [ruff](https://docs.astral.sh/ruff/) for linting python files. It is recommended to use [prettier](https://prettier.io/) for formatting HTML, CSS & Vue files.
- [Vale]((https://vale.sh)) is used for spell check and grammar check for docs content.

```sh
$ uv add pre-commit
$ pre-commit install
```

### Contribution

Want to contribute to the platform? Checkout the [contribution guidelines](/CONTRIBUTING.md).

### Security Policy

Please checkout [Security Policy](/SECURITY.md) for information about reporting a Security Bug or Vulnerability.

## License

The repository has been released under [AGPL-3.0](https://github.com/fossunited/fossunited/blob/develop/LICENSE).
By Contributing to the FOSS United Platform, you agree that all your contributions will be licensed under AGPL License.
