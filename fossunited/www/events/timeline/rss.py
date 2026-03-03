from datetime import datetime
from email.utils import format_datetime
from urllib.parse import urljoin

import frappe
from frappe.utils import escape_html, get_request_site_address, sanitize_html

from fossunited.doctype_ids import EVENT, HACKATHON

no_cache = 1
base_template_path = "www/events/timeline/rss.xml"


def get_context(context):
    """Generate RSS feed for upcoming events"""

    host = get_request_site_address()
    now = frappe.utils.now_datetime()

    # Get upcoming published events
    events = frappe.get_all(
        EVENT,
        fields=[
            "name",
            "event_name",
            "event_description",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_type",
            "chapter",
            "route",
            "modified",
            "banner_image",
            "must_attend",
        ],
        filters={
            "is_published": 1,
            "event_end_date": (">=", now),
        },
        order_by="event_start_date asc",
        limit=50,
    )

    # Get upcoming hackathons
    hackathons = frappe.get_all(
        HACKATHON,
        fields=[
            "name",
            "hackathon_name as event_name",
            "hackathon_description as event_description",
            "start_date as event_start_date",
            "end_date as event_end_date",
            "hackathon_type as event_type",
            "chapter",
            "route",
            "modified",
            "hackathon_banner as banner_image",
        ],
        filters={
            "is_published": 1,
            "end_date": (">=", now),
        },
        order_by="start_date asc",
        limit=10,
    )
    grants = frappe.get_all(
        "FOSS Event Grant",
        fields=[
            "name",
            "event_name",
            "event_description",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_type",
            "event_website as route",
            "grant_amount",
            "modified",
        ],
        filters={
            "grant_status": "Approved",
            "event_end_date": (">=", now),
        },
        order_by="event_start_date asc",
        limit=20,
    )

    for g in grants:
        g.route = g.route or "/grants/events"
        g.chapter = "FOSS Event Grants"
        g.must_attend = (g.grant_amount or 0) > 10000

    for h in hackathons:
        h["must_attend"] = 1

    # Combine and process events
    all_events = events + hackathons + grants
    all_events.sort(key=lambda x: frappe.utils.get_datetime(x.event_start_date))

    for event in all_events:
        if event.route and event.route.startswith("http"):
            event.link = event.route
        else:
            event.link = urljoin(host, event.route or "")
        event.location = escape_html(event.event_location or "")
        event.chapter_name = escape_html(event.chapter or "")
        event.event_type_display = escape_html(event.event_type or "Event")
        location = event.location or ("Online" if event.event_type == "Online" else "TBA")
        event.title = escape_html(
            f"{event.event_name} \u2013 {location}" if event.event_name else ""
        )
        event.author = event.chapter_name
        event.category = event.event_type_display
        event.guid = event.link

        # Format dates
        start_date = frappe.utils.get_datetime(event.event_start_date)
        end_date = frappe.utils.get_datetime(event.event_end_date)

        event.start_date_formatted = start_date.strftime("%d %B %Y, %I:%M %p")
        event.end_date_formatted = end_date.strftime("%d %B %Y, %I:%M %p")
        event.published_date = format_datetime(start_date)

        # Build RSS description with event details
        event_details = f"""
        <![CDATA[
        <h3>{event.event_name}</h3>
        <p><strong>Type:</strong> {event.event_type_display}</p>
        <p><strong>Chapter:</strong> {event.chapter_name}</p>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Start:</strong> {event.start_date_formatted}</p>
        <p><strong>End:</strong> {event.end_date_formatted}</p>
        """

        if event.must_attend:
            event_details += "<p><strong>⭐ Must Attend Event</strong></p>"

        if event.banner_image:
            banner_url = urljoin(host, event.banner_image)
            event_details += f"""<p><img src="{banner_url}" alt="{event.event_name}"
            style="max-width: 600px; height: auto;"/></p>"""

        if event.event_description:
            description_html = sanitize_html(event.event_description)
            event_details += f"<div>{description_html}</div>"

        event_details += f'<p><a href="{event.link}">View Event Details →</a></p>'
        event_details += "]]>"

        event.content = event_details

    # Get latest modification date
    if all_events:
        modified = format_datetime(max(e.modified for e in all_events))
    else:
        modified = format_datetime(datetime.now())

    context = {
        "title": "FOSS United - Upcoming Events",
        "description": """Stay updated with upcoming FOSS events, conferences, meetups,
        and hackathons across India""",
        "modified": modified,
        "items": all_events,
        "link": host + "/events/timeline",
        "feed_url": host + "/events/timeline/rss",
    }

    return context
