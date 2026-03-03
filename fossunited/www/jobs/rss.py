from datetime import datetime
from email.utils import format_datetime
from urllib.parse import quote, urljoin, urlparse

import frappe
from frappe.utils import escape_html, get_request_site_address, md_to_html

from fossunited.doctype_ids import JOB, JOB_STATUS_APPROVED

no_cache = 1
base_template_path = "www/jobs/rss.xml"


def _safe_href(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return ""
    return escape_html(quote(url, safe=":/?#[]@!$&'()*+,;=%"))


def _safe_cdata(text: str) -> str:
    return text.replace("]]>", "]]]]><![CDATA[>")


def get_context(context):
    host = get_request_site_address()

    jobs = frappe.get_all(
        JOB,
        filters={"status": JOB_STATUS_APPROVED, "is_published": 1},
        fields=[
            "name",
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

    for job in jobs:
        job.link = urljoin(host, job.route) if job.route else host + "/jobs"
        job.title = escape_html(f"{job.job_title} at {job.company_name}")
        job.company = escape_html(job.company_name or "")
        job.location = escape_html(job.job_location or "")
        job.job_type_display = escape_html(job.job_type or "")
        job.published_date = format_datetime(frappe.utils.get_datetime(job.creation))

        description_html = _safe_cdata(md_to_html(job.job_description or "") or "")
        apply_link = _safe_href(job.application_link) or _safe_href(job.link)
        apply_html = f'<p><a href="{apply_link}">Apply →</a></p>' if apply_link else ""
        job.content = (
            f"<![CDATA["
            f"<p><strong>Company:</strong> {job.company}</p>"
            f"<p><strong>Location:</strong> {job.location}</p>"
            f"<p><strong>Type:</strong> {job.job_type_display}</p>"
            f"{description_html}"
            f"{apply_html}"
            f"]]>"
        )

    if jobs:
        modified = format_datetime(max(frappe.utils.get_datetime(j.modified) for j in jobs))
    else:
        modified = format_datetime(datetime.now())

    return {
        "title": "FOSS United Job Board",
        "description": "Latest job postings in the FOSS United job board",
        "modified": modified,
        "items": jobs,
        "link": host + "/jobs",
        "feed_url": host + "/jobs/rss.xml",
    }
