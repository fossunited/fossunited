"""Atom feed of upcoming events, served at rss.xml (template: templates/rss.xml)."""

from fossunited.utils.rss import event_entry, feed_context
from fossunited.www.events.timeline.index import get_foss_timeline_items

no_cache = 1
base_template_path = "www/events/timeline/rss.xml"


def get_context(context):
    """Generate the Atom feed for upcoming events"""
    entries = [
        event_entry(item, item.get("_chapter_name"))
        for item in get_foss_timeline_items(is_upcoming=True)
    ]
    return feed_context(
        "FOSS United | Upcoming Events",
        "Stay updated with upcoming FOSS events, conferences, meetups, and hackathons across India",
        "/events/timeline",
        "/events/timeline/rss.xml",
        entries,
    )
