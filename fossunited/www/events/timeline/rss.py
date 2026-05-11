from datetime import datetime
from email.utils import format_datetime
from urllib.parse import urljoin

from frappe.utils import escape_html, get_datetime, get_request_site_address, sanitize_html

from fossunited.www.events.timeline.index import get_foss_timeline_items

no_cache = 1
base_template_path = "www/events/timeline/rss.xml"


def get_context(context):
    """Generate RSS feed for upcoming events"""
    host = get_request_site_address()

    all_events = get_foss_timeline_items(is_upcoming=True)

    for event in all_events:
        if event.route and event.route.startswith("http"):
            event.link = event.route
        else:
            event.link = urljoin(host, event.route or "")

        chapter = event.get("chapter") or ""
        chapter_name = (
            chapter.get("chapter_name", "") if isinstance(chapter, dict) else str(chapter)
        )

        event.location = escape_html(event.event_location or "")
        event.chapter_name = escape_html(chapter_name)
        event.event_type_display = escape_html(event.get("event_type") or "Event")
        location = event.location or ("Online" if event.event_location == "Online" else "TBA")
        event.title = escape_html(
            f"{event.event_name} \u2013 {location}" if event.event_name else ""
        )
        event.author = event.chapter_name
        event.category = event.event_type_display
        event.guid = event.link

        start_date = get_datetime(event.event_start_date)
        end_date = get_datetime(event.event_end_date)

        event.start_date_formatted = start_date.strftime("%d %B %Y, %I:%M %p")
        event.end_date_formatted = end_date.strftime("%d %B %Y, %I:%M %p")
        event.published_date = format_datetime(start_date)

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

        if event.get("event_description"):
            description_html = sanitize_html(event.event_description)
            event_details += f"<div>{description_html}</div>"

        event_details += f'<p><a href="{event.link}">View Event Details →</a></p>'
        event_details += "]]>"

        event.content = event_details

    if all_events:
        modified_dates = [get_datetime(e.modified) for e in all_events if e.get("modified")]
        modified = (
            format_datetime(max(modified_dates))
            if modified_dates
            else format_datetime(datetime.now())
        )
    else:
        modified = format_datetime(datetime.now())

    return {
        "title": "FOSS United - Upcoming Events",
        "description": """Stay updated with upcoming FOSS events, conferences, meetups,
        and hackathons across India""",
        "modified": modified,
        "items": all_events,
        "link": host + "/events/timeline",
        "feed_url": host + "/events/timeline/rss",
    }
