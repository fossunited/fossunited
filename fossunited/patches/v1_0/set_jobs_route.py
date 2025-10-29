import frappe


def execute():
    """
    Migration: Set job route and publish existing jobs.
    - Auto-generate a route if not set (same logic as before_save).
    - Set is_published = 1 for all jobs.
    """
    all_jobs = frappe.get_all("Job Board", fields=["name", "route", "is_published", "status"])

    for job in all_jobs:
        updates = {}

        if not job.route:
            updates["route"] = f"jobs/{job.name}"

        updates["is_published"] = 1

        if updates:
            frappe.db.set_value("Job Board", job.name, updates, update_modified=False)
    frappe.logger().info("✅ Job Board migration completed: routes + is_published set.")
