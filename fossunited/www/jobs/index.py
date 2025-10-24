import frappe


def get_context(context):
    context.active_jobs = frappe.get_all(
        "Job Board",
        filters={"status": "Approved"},
        fields=[
            "name",
            "job_title",
            "job_location",
            "company_name",
            "company_website",
            "job_type",
            "creation",
        ],
        order_by="creation desc",
    )
    context.expired_jobs = frappe.get_all(
        "Job Board",
        filters={"status": "Expired"},
        fields=[
            "name",
            "job_title",
            "job_location",
            "company_name",
            "company_website",
            "job_type",
            "creation",
            "modified",
        ],
        order_by="modified desc",
    )
    context.title = "Job Board - FOSS United"
    return context
