#!/usr/bin/env python3
"""
Generate OpenCollection YAML files for all @frappe.whitelist endpoints.
Idempotent: safe to re-run — creates/updates every endpoint found in source.

Usage:
    python generate_bruno_collection.py [--docs] [--dry-run]

    --docs      Also regenerate docs/docs/api.md
    --dry-run   Print what would be written, don't touch disk

Collection structure (OpenCollection spec, Bruno 3.0+):
    bruno-collection/
      opencollection.yml       # collection root
      environments/
        local-development.yml  # edit base + auth_token here
        production.yml
      .env                     # gitignored; set auth_token=token key:secret
      api/tickets/
        folder.yml
        check-ticket-validity.yml
        ...

Auth:
    Non-guest endpoints send Authorization: {{auth_token}} via apikey header auth.
    Set auth_token in .env (gitignored): auth_token=token <api_key>:<api_secret>

Bruno CLI:
    bru run bruno-collection/api/tickets --env local-development
    bru run bruno-collection/api --env local-development --recursive
    bru run bruno-collection --env "production" --recursive # Dont
"""

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).parent
COLLECTION_DIR = ROOT / "bruno-collection"
DOCS_OUTPUT = ROOT / "docs/docs/api.md"

DRY_RUN = "--dry-run" in sys.argv
WRITE_DOCS = "--docs" in sys.argv

READ_PREFIXES = (
    "get_",
    "check_",
    "is_",
    "search_",
    "download_",
    "if_",
    "has_",
    "validate_",
    "buy_",
    "partner_",
)


class LiteralStr(str):
    pass


def _literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(LiteralStr, _literal_representer)


def dump(obj) -> str:
    return yaml.dump(obj, allow_unicode=True, default_flow_style=False, sort_keys=False)


def get_group(rel_path: str) -> tuple:
    """Returns (folder_path, dotted_module_path)."""
    p = Path(rel_path)
    parts = p.with_suffix("").parts

    if parts[0] == "fossunited" and len(parts) >= 3 and parts[1] == "api":
        m = parts[2]
        return f"api/{m}", f"fossunited.api.{m}"
    if parts[0] == "fossunited" and parts[-1] == "handlers":
        return "webhooks", "fossunited.handlers"
    if parts[0] == "fossunited" and len(parts) >= 3 and parts[1] == "fossunited":
        return parts[2], f"fossunited.fossunited.{parts[2]}"
    if parts[0] == "fossunited" and "doctype" in parts:
        dt_idx = list(parts).index("doctype")
        section = parts[dt_idx - 1] if dt_idx > 0 else "misc"
        return section, ".".join(parts)
    return "misc", ".".join(parts)


@dataclass
class Endpoint:
    dotted_path: str
    function: str
    params: list  # [(name, annotation_str, default_str)]
    allow_guest: bool
    rate_limit: Optional[str]
    docstring: str
    source_file: str
    group: str


def _ann(node) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_ann(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return f"{_ann(node.value)}[{_ann(node.slice)}]"
    if isinstance(node, ast.BinOp):
        return f"{_ann(node.left)} | {_ann(node.right)}"
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return "?"


def _default(node) -> str:
    if node is None:
        return ""
    try:
        return repr(ast.literal_eval(node))
    except Exception:
        return node.id if isinstance(node, ast.Name) else "..."


def _whitelist_guest(dec) -> Optional[bool]:
    if isinstance(dec, ast.Call):
        f = dec.func
        if (isinstance(f, ast.Attribute) and f.attr == "whitelist") or (
            isinstance(f, ast.Name) and f.id == "whitelist"
        ):
            for kw in dec.keywords:
                if kw.arg == "allow_guest" and isinstance(kw.value, ast.Constant):
                    return bool(kw.value.value)
            return False
    elif isinstance(dec, ast.Attribute) and dec.attr == "whitelist":
        return False
    elif isinstance(dec, ast.Name) and dec.id == "whitelist":
        return False
    return None


def _rate_limit(decs: list) -> Optional[str]:
    for dec in decs:
        if not isinstance(dec, ast.Call):
            continue
        f = dec.func
        if not (
            (isinstance(f, ast.Attribute) and f.attr == "rate_limit")
            or (isinstance(f, ast.Name) and f.id == "rate_limit")
        ):
            continue
        limit = seconds = None
        for kw in dec.keywords:
            if kw.arg == "limit" and isinstance(kw.value, ast.Constant):
                limit = kw.value.value
            if kw.arg == "seconds" and isinstance(kw.value, ast.Constant):
                seconds = kw.value.value
        if limit and seconds:
            hrs, rem = divmod(seconds, 3600)
            mins = rem // 60
            period = (
                f"{hrs}h"
                if hrs and not mins
                else (f"{mins}m" if mins else f"{seconds}s")
            )
            return f"{limit}/{period}"
    return None


def parse_file(py_file: Path) -> list:
    rel = str(py_file.relative_to(ROOT))
    group, module_dotted = get_group(rel)
    try:
        tree = ast.parse(py_file.read_text())
    except SyntaxError:
        return []

    endpoints = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        allow_guest = None
        for dec in node.decorator_list:
            r = _whitelist_guest(dec)
            if r is not None:
                allow_guest = r
                break
        if allow_guest is None:
            continue

        args = node.args
        all_args = args.args + args.kwonlyargs
        offset = len(all_args) - len(args.defaults)
        params = []
        for i, arg in enumerate(all_args):
            if arg.arg == "self":
                continue
            ann = _ann(arg.annotation) if arg.annotation else ""
            di = i - offset
            default = (
                _default(args.defaults[di]) if 0 <= di < len(args.defaults) else ""
            )
            params.append((arg.arg, ann, default))

        endpoints.append(
            Endpoint(
                dotted_path=f"{module_dotted}.{node.name}",
                function=node.name,
                params=params,
                allow_guest=allow_guest,
                rate_limit=_rate_limit(node.decorator_list),
                docstring=(ast.get_docstring(node) or "").strip(),
                source_file=rel,
                group=group,
            )
        )
    return endpoints


def find_all_endpoints() -> list:
    result = []
    for py_file in sorted(ROOT.rglob("*.py")):
        rel = str(py_file.relative_to(ROOT))
        if any(
            rel.startswith(p)
            for p in ("node_modules/", ".git/", "development/", "__pycache__/")
        ):
            continue
        if "/test_" in rel or rel.startswith("test_"):
            continue
        result.extend(parse_file(py_file))
    return result


def is_read(fn: str) -> bool:
    return fn.startswith(READ_PREFIXES)


def has_complex_params(params: list) -> bool:
    import re

    _complex = re.compile(r"\b(dict|list|List|Dict|Any)\b")
    return any(ann and _complex.search(ann) for _, ann, _ in params)


def make_request_yml(ep: Endpoint, seq: int) -> dict:
    # Always POST — Frappe accepts POST for all whitelisted methods,
    # and Bruno CLI has a bug where GET query params from env vars don't interpolate.
    http: dict = {"method": "POST", "url": f"{{{{base}}}}/method/{ep.dotted_path}"}

    if ep.params:
        if has_complex_params(ep.params):
            http["body"] = {
                "type": "json",
                "data": LiteralStr(
                    json.dumps({n: f"{{{{{n}}}}}" for n, _, _ in ep.params}, indent=2)
                ),
            }
        else:
            http["body"] = {
                "type": "form-urlencoded",
                "data": [{"name": n, "value": f"{{{{{n}}}}}"} for n, _, _ in ep.params],
            }

    obj: dict = {
        "info": {"name": ep.function.replace("_", "-"), "type": "http", "seq": seq},
        "http": http,
    }

    obj["runtime"] = {
        "auth": {
            "type": "apikey",
            "key": "Authorization",
            "value": "{{auth_token}}",
            "placement": "header",
        }
    }

    doc_parts = []
    if ep.docstring:
        doc_parts.append(ep.docstring.split("\n")[0])
    doc_parts.append(
        f"allow_guest: {str(ep.allow_guest).lower()}"
        + (f" | Rate: {ep.rate_limit}" if ep.rate_limit else "")
    )
    doc_parts.append(f"Source: {ep.source_file}")
    if ep.params:
        doc_parts.append(
            "Args: "
            + ", ".join(
                f"{n}: {ann or 'str'}" + (" (opt)" if d else "")
                for n, ann, d in ep.params
            )
        )
    obj["docs"] = "\n".join(doc_parts)
    return obj


def make_folder_yml(name: str, seq: int) -> dict:
    return {"info": {"name": name, "type": "folder", "seq": seq}}


def make_opencollection_yml() -> dict:
    return {
        "info": {
            "name": "Fossunited API Testing",
            "summary": "Auto-generated from @frappe.whitelist. Re-run generate_bruno_collection.py to update.",
        },
        "opencollection": "1.0.0",
    }


def make_env_yml(name: str, base_url: str, endpoints: list, color: str = None) -> dict:
    # Collect every unique param name used across all endpoints
    all_params = sorted(set(n for ep in endpoints for n, _, _ in ep.params))
    param_vars = [{"name": p, "value": ""} for p in all_params]
    env = {
        "name": name,
        "variables": [
            {"name": "base", "value": base_url},
            {"name": "auth_token", "value": "{{process.env.auth_token}}"},
        ]
        + param_vars,
    }
    if color:
        env["color"] = color
    return env


def write_file(path: Path, content: str):
    if DRY_RUN:
        print(f"  [dry-run] {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def write_yml(path: Path, obj: dict):
    write_file(path, dump(obj))


def generate(endpoints: list):
    groups: dict[str, list] = {}
    for ep in endpoints:
        groups.setdefault(ep.group, []).append(ep)

    write_yml(COLLECTION_DIR / "opencollection.yml", make_opencollection_yml())

    env_dir = COLLECTION_DIR / "environments"
    local = env_dir / "local-development.yml"
    prod = env_dir / "production.yml"
    if not local.exists():
        write_yml(
            local,
            make_env_yml(
                "local-development", "http://foss.localhost/api", endpoints, "#22c55e"
            ),
        )
    if not prod.exists():
        write_yml(
            prod,
            make_env_yml(
                "production", "https://fossunited.org/api", endpoints, "#3b82f6"
            ),
        )

    # .env template — create only if missing (user fills auth_token)
    dotenv = COLLECTION_DIR / ".env"
    if not dotenv.exists():
        write_file(dotenv, "auth_token=token <api_key>:<api_secret>\n")

    for folder_seq, group in enumerate(sorted(groups), start=1):
        folder = COLLECTION_DIR / group
        write_yml(
            folder / "folder.yml", make_folder_yml(group.split("/")[-1], folder_seq)
        )
        for seq, ep in enumerate(groups[group], start=1):
            write_yml(
                folder / f"{ep.function.replace('_', '-')}.yml",
                make_request_yml(ep, seq),
            )

    if not DRY_RUN:
        total = sum(len(v) for v in groups.values())
        print(f"  {total} endpoints, {len(groups)} groups")
        for g in sorted(groups):
            print(f"    {g}/  ({len(groups[g])})")


def generate_docs(endpoints: list):
    groups: dict[str, list] = {}
    for ep in endpoints:
        groups.setdefault(ep.group, []).append(ep)

    lines = [
        "# Fossunited API Reference",
        "",
        "Auto-generated. Re-run `python generate_bruno_collection.py --docs` to update.",
        "",
        "## Authentication",
        "",
        "Pass `Authorization: token <api_key>:<api_secret>` header.",
        "Endpoints marked [Guest] work without auth.",
        "",
        "**Base URL:** `https://fossunited.org/api/method/<dotted.path>`",
        "",
        "---",
        "",
    ]
    for group in sorted(groups):
        lines += [
            f"## {group.replace('/', ' › ').replace('_', ' ').title()}",
            "",
            "| Function | Method | Auth | Rate | Description |",
            "|---|---|---|---|---|",
        ]
        for ep in groups[group]:
            method = "GET" if is_read(ep.function) else "POST"
            auth = "[Guest]" if ep.allow_guest else "🔒 Auth"
            doc = ep.docstring.split("\n")[0] if ep.docstring else "—"
            lines.append(
                f"| `{ep.function}` | {method} | {auth} | {ep.rate_limit or '—'} | {doc} |"
            )
        lines.append("")

    write_file(DOCS_OUTPUT, "\n".join(lines))
    if not DRY_RUN:
        print(f"  docs → {DOCS_OUTPUT.relative_to(ROOT)}")


def main():
    print("Scanning @frappe.whitelist...")
    endpoints = find_all_endpoints()
    print(f"  {len(endpoints)} endpoints found")

    print("Generating OpenCollection YAML...")
    generate(endpoints)

    if WRITE_DOCS:
        print("Generating docs...")
        generate_docs(endpoints)

    print("Done.")


if __name__ == "__main__":
    main()
