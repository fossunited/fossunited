"""Shared helpers for the Atom feeds served at */rss.xml (template: templates/rss.xml).

Not renaming to atom feed cause rss term is popular, and atom feed is better to have.

A feed's rss.py only runs its query and maps each row to an entry dict. Entry keys, all optional
except id, title and updated: id, title, link, published, updated, author, author_uri, category,
category_label, summary (plain text), content (HTML), image, image_type.
"""

from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import frappe
from frappe.utils import (
    escape_html,
    get_datetime,
    get_request_site_address,
    get_system_timezone,
    now_datetime,
    sanitize_html,
)


def public_url(route):
    """Absolute URL for a site route. Absolute URLs pass through unchanged."""
    return urljoin(get_request_site_address().rstrip("/") + "/", route) if route else None


def safe_url(url):
    """The url if it is http(s). User-entered links must not become javascript: hrefs."""
    return url if url and urlparse(url).scheme in ("http", "https") else None


def atom_date(value):
    """RFC 3339 string in the site timezone. A plain date becomes midnight."""
    value = get_datetime(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo(get_system_timezone()))
    return value.isoformat(timespec="seconds")


def facts(*rows):
    """`<p><strong>Label:</strong> value</p>` lines. Rows with an empty value are skipped."""
    return "".join(
        f"<p><strong>{label}:</strong> {escape_html(value)}</p>" for label, value in rows if value
    )


def event_entry(event, chapter_name, entry_id=None):
    """Entry for a Chapter Event or a timeline item (event, hackathon or event grant)."""
    external = event.is_external_event and event.external_event_url
    link = public_url(external or event.route) or public_url("/events/timeline")
    event_type = event.event_type or "Event"
    location = event.event_location or ("Online" if event_type == "Online" else "TBA")
    start = get_datetime(event.event_start_date)
    end = get_datetime(event.event_end_date)
    time_format = "%d %B %Y, %I:%M %p"

    content = facts(
        ("Type", event_type),
        ("Chapter", chapter_name),
        ("Location", location),
        ("Start", start.strftime(time_format)),
        ("End", end.strftime(time_format)),
        ("Must Attend", "Yes" if event.must_attend else ""),
    )
    if event.banner_image:
        banner = escape_html(public_url(event.banner_image))
        alt = escape_html(event.event_name)
        content += f'<p><img src="{banner}" alt="{alt}" style="max-width: 600px;" /></p>'
    if event.event_description:
        content += f"<div>{sanitize_html(event.event_description)}</div>"
    content += f'<p><a href="{escape_html(link)}">View Event Details →</a></p>'

    return {
        "id": entry_id or link,
        "title": f"{event.event_name} | {location}",
        "link": link,
        "published": start,
        "updated": event.modified,
        "author": chapter_name,
        "category": event_type,
        "content": content,
    }


def feed_context(title, subtitle, link, path, entries):
    """Context for templates/rss.xml. Entry dates may be dates or datetimes."""
    entries = [frappe._dict(entry) for entry in entries]
    updated = max((get_datetime(entry.updated) for entry in entries), default=now_datetime())
    for entry in entries:
        entry.published = atom_date(entry.published or entry.updated)
        entry.updated = atom_date(entry.updated)

    # TemplatePage's default XML MIME type is replaced for this response only.
    frappe.local.response_headers.set("Content-Type", "application/atom+xml; charset=utf-8")
    return {
        "title": title,
        "subtitle": subtitle,
        "link": public_url(link),
        "feed_url": public_url(path),
        "updated": atom_date(updated),
        "entries": entries,
    }
