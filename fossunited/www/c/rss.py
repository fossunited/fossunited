from datetime import datetime
from email.utils import format_datetime
from urllib.parse import urljoin

import frappe
from frappe import _
from frappe.utils import escape_html, get_request_site_address, sanitize_html

from fossunited.doctype_ids import CHAPTER

no_cache = 1
base_template_path = "www/c/rss.xml"


def get_context(context):
    slug = frappe.form_dict.get("chapter")
    if not slug:
        frappe.throw(_("chapter parameter is required"), frappe.InvalidRequestException)

    try:
        doc = frappe.get_doc(CHAPTER, {"slug": slug})
    except frappe.DoesNotExistError:
        frappe.throw(_("Chapter not found"), frappe.DoesNotExistError)

    host = get_request_site_address()
    events = [e for e in doc.get_upcoming_events() if e.is_published]

    for event in events:
        if event.is_external_event and event.external_event_url:
            event.link = event.external_event_url
        else:
            event.link = urljoin(host, event.route or "") or host + "/events/timeline"

        location = escape_html(event.event_location or "")
        event.event_type_display = escape_html(event.event_type or "Event")
        location = location or ("Online" if event.event_type == "Online" else "TBA")
        event.title = escape_html(
            f"{event.event_name} \u2013 {location}" if event.event_name else ""
        )
        event.author = escape_html(doc.chapter_name)
        event.category = event.event_type_display
        event.guid = f"{host}/c/{doc.slug}/rss.xml#{event.name}"

        start_date = frappe.utils.get_datetime(event.event_start_date)
        end_date = frappe.utils.get_datetime(event.event_end_date)
        event.start_date_formatted = start_date.strftime("%d %B %Y, %I:%M %p")
        event.end_date_formatted = end_date.strftime("%d %B %Y, %I:%M %p")
        event.published_date = format_datetime(start_date)

        event_details = f"""
        <![CDATA[
        <h3>{event.event_name}</h3>
        <p><strong>Type:</strong> {event.event_type_display}</p>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Start:</strong> {event.start_date_formatted}</p>
        <p><strong>End:</strong> {event.end_date_formatted}</p>
        """

        if event.must_attend:
            event_details += "<p><strong>⭐ Must Attend Event</strong></p>"

        if event.banner_image:
            banner_url = urljoin(host, event.banner_image)
            event_details += (
                f'<p><img src="{banner_url}" alt="{event.event_name}"'
                ' style="max-width: 600px; height: auto;"/></p>'
            )

        if event.event_description:
            event_details += f"<div>{sanitize_html(event.event_description)}</div>"

        event_details += f'<p><a href="{event.link}">View Event Details \u2192</a></p>'
        event_details += "]]>"

        event.content = event_details

    if events:
        modified = format_datetime(max(e.modified for e in events))
    else:
        modified = format_datetime(datetime.now())

    feed_url = f"{host}/c/{doc.slug}/rss.xml"
    chapter_url = urljoin(host, doc.route) if doc.route else host

    return {
        "title": f"{doc.chapter_name} \u2013 Upcoming Events",
        "description": f"Upcoming events from {doc.chapter_name}",
        "modified": modified,
        "items": events,
        "link": chapter_url,
        "feed_url": feed_url,
    }
