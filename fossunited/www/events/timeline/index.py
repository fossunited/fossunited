from datetime import datetime

import frappe
from frappe.utils import get_datetime, now_datetime

from fossunited.doctype_ids import CHAPTER, EVENT, HACKATHON


def get_context(context, page_type="upcoming"):
    context.no_cache = 1

    context.page_type = page_type

    now = get_datetime(now_datetime())

    if page_type == "upcoming":
        context.title = "Upcoming Events - FOSS United"
        event_filters = {
            "is_published": 1,
            "event_end_date": [">=", now],
        }
        hackathon_filters = {
            "is_published": 1,
            "end_date": [">=", now],
        }
    else:
        context.title = "Past Events - FOSS United"
        event_filters = {
            "is_published": 1,
            "event_end_date": ["<", now],
        }
        hackathon_filters = {
            "is_published": 1,
            "end_date": ["<", now],
        }

    events = frappe.get_all(
        EVENT,
        filters=event_filters,
        fields=[
            "name",
            "route",
            "event_name",
            "event_start_date",
            "event_end_date",
            "event_location",
            "banner_image",
            "chapter",
            "must_attend",
        ],
    )

    hackathons = frappe.get_all(
        HACKATHON,
        filters=hackathon_filters,
        fields=[
            "name",
            "route",
            "hackathon_name as event_name",
            "start_date as event_start_date",
            "end_date as event_end_date",
            "hackathon_banner as banner_image",
            "hackathon_type as event_location",
            "chapter",
        ],
    )

    for h in hackathons:
        h["must_attend"] = 1
        h["_kind"] = "hackathon"

    for e in events:
        e["_kind"] = "event"

    chapter_data = frappe.get_all(CHAPTER, fields=["name", "chapter_type", "city"])

    chapter_type_map = {c.name: c.chapter_type for c in chapter_data}
    chapter_city_map = {c.name: c.city for c in chapter_data}

    # Get unique cities for filter dropdown
    context.all_cities = sorted(list(set(c.city for c in chapter_data if c.city)))

    timeline = []

    for item in events + hackathons:
        start_dt = get_datetime(item.get("event_start_date"))
        end_dt = get_datetime(item.get("event_end_date"))

        row = {
            **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in item.items()},
            "_start": start_dt.isoformat(),
            "_end": end_dt.isoformat(),
            "_is_past": end_dt < now,
            "_chapter_type": chapter_type_map.get(item.get("chapter")),
            "_chapter_city": chapter_city_map.get(item.get("chapter")),
        }

        timeline.append(row)

    # Sort: upcoming = chronological, past = reverse chronological
    timeline.sort(key=lambda x: x["_start"], reverse=(page_type == "completed"))

    context.timeline_events = timeline
