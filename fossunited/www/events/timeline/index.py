from datetime import datetime

import frappe
from frappe.utils import get_datetime, now_datetime

from fossunited.doctype_ids import EVENT, EVENT_GRANTS, HACKATHON


def get_context(context, page_type="upcoming"):
    context.no_cache = 1
    context.page_type = page_type

    now = get_datetime(now_datetime())

    is_upcoming = page_type == "upcoming"

    context.title = "Upcoming Events - FOSS United" if is_upcoming else "Past Events - FOSS United"

    event_filters = {
        "event_end_date": [">=" if is_upcoming else "<", now],
        "status": "Live" if is_upcoming else "Concluded",
    }

    hackathon_filters = {
        "is_published": 1,
        "end_date": [">=" if is_upcoming else "<", now],
    }

    events = frappe.get_all(
        EVENT,
        filters=event_filters,
        or_filters={
            "is_published": 1,
            "is_external_event": 1,
        },
        fields=[
            "name",
            "route",
            "external_event_url",
            "is_external_event",
            "event_name",
            "event_start_date",
            "event_end_date",
            "event_location",
            "banner_image",
            "chapter",
            "must_attend",
            "chapter.chapter_type as _chapter_type",
            "chapter.city as _chapter_city",
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
            "chapter.chapter_type as _chapter_type",
            "chapter.city as _chapter_city",
        ],
    )

    grants = frappe.get_all(
        EVENT_GRANTS,
        filters={
            "grant_status": "Approved",
            "event_end_date": [">=" if is_upcoming else "<", now],
        },
        fields=[
            "name",
            "event_name",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_website",
            "grant_amount",
        ],
    )

    for h in hackathons:
        h["_kind"] = "hackathon"
        h["must_attend"] = 1  # by default

    for e in events:
        e["_kind"] = "event"

    GRANTS_CHAPTER_BASE = frappe._dict(
        {
            "doctype": "FOSS Chapter",
            "chapter_name": "FOSS Event Grants",
            "chapter_type": "City Community",
        }
    )

    for g in grants:
        website = g.get("event_website") or "/grants/events"
        location = (g.get("event_location") or "").strip().title()
        city = location.split(",")[0].strip() if location else None

        g.update(
            {
                "route": website,
                "external_event_url": website,
                "is_external_event": 1,
                "banner_image": None,
                "chapter": frappe._dict({**GRANTS_CHAPTER_BASE, "city": city}),
                "must_attend": (g.get("grant_amount") or 0) > 10000,
                "_kind": "grant",
                "_chapter_city": city,
                "event_location": location,
            }
        )

    # Collect cities directly from fetched data
    context.all_cities = sorted(
        {e.get("_chapter_city") for e in events + hackathons + grants if e.get("_chapter_city")}
    )

    timeline = []

    for item in events + hackathons + grants:
        start_dt = get_datetime(item.get("event_start_date"))
        end_dt = get_datetime(item.get("event_end_date"))

        timeline.append(
            {
                **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in item.items()},
                "_start": start_dt.isoformat(),
                "_end": end_dt.isoformat(),
                "_is_past": end_dt < now,
            }
        )

    timeline.sort(
        key=lambda x: x["_start"],
        reverse=not is_upcoming,
    )

    context.timeline_events = timeline
