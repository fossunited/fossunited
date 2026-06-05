"""
Schema patch runner for the FOSSUnited bench.

Applies schema fixes that `bench migrate` doesn't handle automatically:

- FOSS Event CFP Review is simultaneously a standalone doctype AND a child table
  of FOSS Event CFP Submission. `migrate` creates it without the parent/parentfield/
  parenttype columns that are required for the child-table relationship. This causes
  `submission.reload()` to fail with "Unknown column 'parent' in WHERE".

Run via:
    podman exec -w /workspace/development/fossu-bench/sites devcontainer-frappe-1 \
        ../env/bin/python /workspace/development/patch_schema.py
"""
import frappe

frappe.init(site="fossunited.localhost")
frappe.connect()

FIXES = [
    # (table, column, definition)
    ("tabFOSS Event CFP Review", "parent",      "varchar(140) DEFAULT NULL"),
    ("tabFOSS Event CFP Review", "parentfield", "varchar(140) DEFAULT NULL"),
    ("tabFOSS Event CFP Review", "parenttype",  "varchar(255) DEFAULT NULL"),
]

for table, column, defn in FIXES:
    existing = frappe.db.sql(
        f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "  # noqa: S608
        f"WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column),
    )
    if not existing:
        frappe.db.sql(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {defn}")  # noqa: S608
        print(f"  Added `{column}` to `{table}`")
    else:
        print(f"  `{table}`.`{column}` already exists — skipped")

# Ensure the index exists
frappe.db.sql(
    "CREATE INDEX IF NOT EXISTS `parent` ON `tabFOSS Event CFP Review`(`parent`)"
)

frappe.db.commit()  # nosemgrep
frappe.destroy()
print("✅ Schema patch complete.")
