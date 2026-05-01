"""
Seed runner for the FOSSUnited bench.

Run via:
    podman exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/development/run_seed.py

This bypasses `bench execute`'s eval() namespace bug on Python 3.14 which prevents
dotted module paths (fossunited.dev.seed.seed) from resolving.
"""
import sys

# seed.py lives in /workspace/development/, not inside the fossunited app package
sys.path.insert(0, "/workspace/development")

import frappe

frappe.init(site="fossunited.localhost")
frappe.connect()

import importlib

_seed_mod = importlib.import_module("seed")
seed = _seed_mod.seed

seed()
frappe.destroy()
print("✅ Seed complete.")
