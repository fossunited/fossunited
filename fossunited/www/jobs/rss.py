"""Atom feed of job board, served at rss.xml (template: templates/rss.xml)."""

import frappe
from frappe.utils import escape_html, md_to_html

from fossunited.doctype_ids import JOB, JOB_STATUS_APPROVED
from fossunited.utils.rss import facts, feed_context, public_url, safe_url

no_cache = 1
base_template_path = "www/jobs/rss.xml"


def get_context(context):
    jobs = frappe.get_all(
        JOB,
        filters={"status": JOB_STATUS_APPROVED, "is_published": 1},
        fields=[
            "job_title",
            "company_name",
            "job_location",
            "job_type",
            "job_description",
            "application_link",
            "route",
            "creation",
            "modified",
        ],
        order_by="creation desc",
        limit=50,
    )

    entries = []
    for job in jobs:
        link = public_url(job.route) or public_url("/jobs")
        apply_link = safe_url(job.application_link) or link
        content = facts(
            ("Company", job.company_name),
            ("Location", job.job_location),
            ("Type", job.job_type),
        )
        content += md_to_html(job.job_description or "")
        content += f'<p><a href="{escape_html(apply_link)}">Apply →</a></p>'
        entries.append(
            {
                "id": link,
                "title": f"{job.job_title} at {job.company_name}",
                "link": link,
                "published": job.creation,
                "updated": job.modified,
                "author": job.company_name,
                "category": job.job_type,
                "content": content,
            }
        )

    return feed_context(
        "FOSS United Job Board",
        "Latest job postings in the FOSS United job board",
        "/jobs",
        "/jobs/rss.xml",
        entries,
    )
