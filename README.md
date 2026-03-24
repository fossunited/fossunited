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

Please follow our [development guide](https://docs.fossunited.org/development/) to set up the project locally.

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
