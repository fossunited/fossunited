"""
Seed runner for the FOSSUnited bench.

Run via:
    podman exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/fossunited/development/run_seed.py

This bypasses `bench execute`'s eval() namespace bug on Python 3.14 which prevents
dotted module paths (fossunited.dev.seed.seed) from resolving.
"""
import frappe

frappe.init(site="fossunited.localhost")
frappe.connect()

from fossunited.dev.seed import seed  # noqa: E402

seed()
frappe.destroy()
print("✅ Seed complete.")
