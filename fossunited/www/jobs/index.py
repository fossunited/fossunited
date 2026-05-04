import frappe

from fossunited.doctype_ids import (
    JOB,
    JOB_STATUS_APPROVED,
    JOB_STATUS_EXPIRED,
)


def get_context(context):
    context.no_cache = 1
    context.active_jobs = frappe.get_all(
        JOB,
        filters={"status": JOB_STATUS_APPROVED, "is_published": 1},
        fields=[
            "name",
            "job_title",
            "job_location",
            "company_name",
            "company_website",
            "job_type",
            "creation",
            "publish_date",
        ],
        order_by="creation desc",
    )
    context.expired_jobs = frappe.get_all(
        JOB,
        filters={"status": JOB_STATUS_EXPIRED, "is_published": 1},
        fields=[
            "name",
            "job_title",
            "job_location",
            "company_name",
            "company_website",
            "job_type",
            "creation",
            "publish_date",
            "closed_date",
        ],
        order_by="closed_date desc",
    )
    context.title = "Job Board - FOSS United"
