import html
from datetime import datetime
from email.utils import format_datetime
from urllib.parse import urljoin

import frappe
from frappe import _
from frappe.utils import escape_html, get_request_site_address, sanitize_html

from fossunited.doctype_ids import EVENT

no_cache = 1
base_template_path = "www/c/rss.xml"


def _safe_cdata(text):
    return (text or "").replace("]]>", "]]]]><![CDATA[>")


def get_context(context):
    slug = frappe.form_dict.get("chapter")
    if not slug:
        frappe.throw(_("chapter parameter is required"), frappe.InvalidRequestException)

    chapter = frappe.db.get_value(
        "FOSS Chapter", {"slug": slug}, ["chapter_name", "route", "name", "slug"], as_dict=True
    ) or frappe.db.get_value(
        "FOSS Chapter", slug, ["chapter_name", "route", "name", "slug"], as_dict=True
    )
    if not chapter:
        frappe.throw(_("Chapter not found"), frappe.DoesNotExistError)

    host = get_request_site_address()

    events = frappe.get_all(
        EVENT,
        filters={
            "chapter": chapter.name,
            "event_end_date": (">=", frappe.utils.now()),
            "status": "Live",
            "is_published": 1,
        },
        fields=[
            "name",
            "event_name",
            "event_description",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_type",
            "route",
            "modified",
            "is_external_event",
            "external_event_url",
            "must_attend",
        ],
        order_by="event_start_date asc",
        limit=50,
    )

    items = []
    for e in events:
        if e.is_external_event and e.external_event_url:
            link = e.external_event_url
        else:
            link = urljoin(host, e.route) if e.route else host + "/events/timeline"

        location = escape_html(e.event_location or "")
        event_type = escape_html(e.event_type or "")
        start = frappe.utils.get_datetime(e.event_start_date)
        end = frappe.utils.get_datetime(e.event_end_date)

        description = _safe_cdata(sanitize_html(e.event_description or ""))
        content = (
            "<![CDATA["
            f"<p><strong>Type:</strong> {event_type}</p>"
            f"<p><strong>Location:</strong> {location}</p>"
            f"<p><strong>Start:</strong> {start.strftime('%d %B %Y, %I:%M %p')}</p>"
            f"<p><strong>End:</strong> {end.strftime('%d %B %Y, %I:%M %p')}</p>"
        )
        if e.must_attend:
            content += "<p><strong>⭐ Must Attend</strong></p>"
        if description:
            content += f"<div>{description}</div>"
        content += f'<p><a href="{html.escape(link, quote=True)}">View Event →</a></p>'
        content += "]]>"

        items.append(
            {
                "title": escape_html(
                    f"{e.event_name} – {location}" if location else (e.event_name or "")
                ),
                "link": link,
                "guid": f"{host}/c/{chapter.slug}/rss.xml#{e.name}",
                "author": escape_html(chapter.chapter_name),
                "published_date": format_datetime(start),
                "modified": e.modified,
                "category": event_type,
                "content": content,
            }
        )

    if items:
        modified = format_datetime(max(frappe.utils.get_datetime(i["modified"]) for i in items))
    else:
        modified = format_datetime(datetime.now())

    feed_url = f"{host}/c/{chapter.slug}/rss.xml"
    chapter_url = urljoin(host, chapter.route) if chapter.route else host

    return {
        "title": f"{chapter.chapter_name} – Upcoming Events",
        "description": f"Upcoming events from {chapter.chapter_name}",
        "modified": modified,
        "items": items,
        "link": chapter_url,
        "feed_url": feed_url,
    }
