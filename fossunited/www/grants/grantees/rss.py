"""Atom feed of grantees, served at rss.xml (template: templates/rss.xml)."""

from urllib.parse import urlencode

from frappe.utils import escape_html, fmt_money, get_datetime, sanitize_html

from fossunited.utils.rss import facts, feed_context, public_url, safe_url
from fossunited.www.grants.index import (
    fetch_event_grants,
    fetch_fellowship_grants,
    fetch_project_grants,
)

no_cache = 1
base_template_path = "www/grants/grantees/rss.xml"


def grant_entry(grant, name, grant_type, website, about_html, published, organiser=None):
    amount = "N/A"
    if grant.grant_amount is not None:
        amount = fmt_money(grant.grant_amount, precision=0, currency="INR")

    page = public_url("/grants/grantees")
    website = safe_url(website)
    content = facts(
        ("Grant Type", f"{grant_type} Grant"), ("Organiser", organiser), ("Amount", amount)
    )
    content += f"<p>{about_html}</p>"
    if website:
        content += f'<p><a href="{escape_html(website)}">Website →</a></p>'

    return {
        "id": f"{page}?{urlencode({'s': name})}",
        "title": f"{name} ({grant_type} Grant)",
        "link": website or page,
        "published": published,
        "updated": grant.modified,
        "author": organiser,
        "category": grant_type,
        "content": content,
    }


def get_context(context):
    entries = []
    for g in fetch_project_grants(limit=50) + fetch_fellowship_grants(limit=50):
        published = g.date_of_provision or g.modified
        entries.append(
            grant_entry(
                g,
                g.project_name,
                g.grant_type,
                g.project_website,
                escape_html(g.about_project or ""),
                published,
            )
        )
    for g in fetch_event_grants(limit=50):
        published = g.event_start_date or g.modified
        entries.append(
            grant_entry(
                g,
                g.event_name,
                "Event",
                g.event_website,
                sanitize_html(g.event_description or ""),
                published,
                organiser=g.event_organiser,
            )
        )

    entries.sort(key=lambda entry: get_datetime(entry["updated"]), reverse=True)
    return feed_context(
        "FOSS United Grantees",
        "New grantees funded by FOSS United across projects, events, and fellowships",
        "/grants/grantees",
        "/grants/grantees/rss.xml",
        entries,
    )
