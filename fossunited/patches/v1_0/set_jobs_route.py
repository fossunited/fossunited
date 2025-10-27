import frappe


def execute():
    """
    Migration: Set job route and publish existing jobs.
    - Auto-generate a route if not set (same logic as before_save).
    - Set is_published = 1 for all jobs.
    """
    all_jobs = frappe.get_all("Job Board", fields=["name", "route", "is_published"])

    for job in all_jobs:
        doc = frappe.get_doc("Job Board", job.name)

        if not doc.route:
            doc.route = f"jobs/{doc.name}"

        doc.is_published = 1

        doc.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger().info("✅ Job Board migration completed: routes + is_published set.")
