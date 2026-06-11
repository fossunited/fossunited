from datetime import datetime
from email.utils import format_datetime
from urllib.parse import quote, urlparse

import frappe
from frappe.utils import escape_html, fmt_money, get_request_site_address

from fossunited.www.grants.index import (
    fetch_event_grants,
    fetch_fellowship_grants,
    fetch_project_grants,
)

no_cache = 1
base_template_path = "www/grants/grantees/rss.xml"


def _safe_href(url):
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return ""
    return quote(url, safe=":/?#[]@!$&'()*+,;=%")


def _safe_cdata(text):
    return (text or "").replace("]]>", "]]]]><![CDATA[>")


def get_context(context):
    host = get_request_site_address()

    project_grants = fetch_project_grants(limit=50) + fetch_fellowship_grants(limit=50)
    event_grants = fetch_event_grants(limit=50)

    items = []

    for g in project_grants:
        amount = (
            fmt_money(g.grant_amount, precision=0, currency="INR")
            if g.grant_amount is not None
            else "N/A"
        )
        date = g.date_of_provision or g.modified
        url = _safe_href(g.project_website)
        description = _safe_cdata(g.about_project or "")
        items.append(
            {
                "title": escape_html(f"{g.project_name} ({g.grant_type} Grant)"),
                "link": escape_html(url) if url else host + "/grants/grantees",
                "guid": f"{host}/grants/grantees?s={g.project_name}",
                "author": "",
                "published_date": format_datetime(frappe.utils.get_datetime(date)),
                "modified": g.modified,
                "category": escape_html(g.grant_type),
                "content": (
                    "<![CDATA["
                    f"<p><strong>Grant Type:</strong> {escape_html(g.grant_type)}</p>"
                    f"<p><strong>Amount:</strong> {escape_html(amount)}</p>"
                    f"<p>{description}</p>"
                    + (f'<p><a href="{url}">Project Website →</a></p>' if url else "")
                    + "]]>"
                ),
            }
        )

    for g in event_grants:
        amount = (
            fmt_money(g.grant_amount, precision=0, currency="INR")
            if g.grant_amount is not None
            else "N/A"
        )
        date = g.event_start_date or g.modified
        url = _safe_href(g.event_website)
        description = _safe_cdata(g.event_description or "")
        items.append(
            {
                "title": escape_html(f"{g.event_name} (Event Grant)"),
                "link": escape_html(url) if url else host + "/grants/grantees",
                "guid": f"{host}/grants/grantees?s={g.event_name}",
                "author": escape_html(g.event_organiser or ""),
                "published_date": format_datetime(frappe.utils.get_datetime(date)),
                "modified": g.modified,
                "category": "Event",
                "content": (
                    "<![CDATA["
                    "<p><strong>Grant Type:</strong> Event Grant</p>"
                    f"<p><strong>Organiser:</strong> {escape_html(g.event_organiser or '')}</p>"
                    f"<p><strong>Amount:</strong> {escape_html(amount)}</p>"
                    f"<p>{description}</p>"
                    + (f'<p><a href="{url}">Event Website →</a></p>' if url else "")
                    + "]]>"
                ),
            }
        )

    items.sort(key=lambda x: frappe.utils.get_datetime(x["modified"]), reverse=True)

    if items:
        modified = format_datetime(max(frappe.utils.get_datetime(i["modified"]) for i in items))
    else:
        modified = format_datetime(datetime.now())

    return {
        "title": "FOSS United Grantees",
        "description": (
            "New grantees funded by FOSS United across projects, events, and fellowships"
        ),
        "modified": modified,
        "items": items,
        "link": host + "/grants/grantees",
        "feed_url": host + "/grants/grantees/rss.xml",
    }
