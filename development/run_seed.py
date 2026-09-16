"""
Seed runner for the FOSSUnited bench.

Run via:
    <docker|podman> exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/development/run_seed.py

This bypasses `bench execute`'s eval() namespace bug on Python 3.14 which prevents
dotted module paths (fossunited.dev.seed.seed) from resolving.
"""

import argparse
import sys

# seed.py lives in /workspace/development/, not inside the fossunited app package
sys.path.insert(0, "/workspace/development")

import frappe

frappe.init(site="fossunited.localhost")
frappe.connect()

import importlib

_seed_mod = importlib.import_module("seed")
seed = _seed_mod.seed

parser = argparse.ArgumentParser(description="Create a realistic local FOSS United demo site")
parser.add_argument(
    "--profile",
    choices=("quick", "full"),
    default="full",
    help="quick creates 18 tickets; full creates 120 tickets (default: full)",
)
args = parser.parse_args()

summary = seed(profile=args.profile)
frappe.destroy()
print(f"✅ Seed complete ({summary['profile']} profile).")
print(
    f"   {summary['chapters']} chapters, {summary['events']} events, "
    f"{summary['tickets']['total']} tickets"
)
