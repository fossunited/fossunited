from datetime import datetime

import frappe
from frappe.utils import get_datetime, now_datetime

from fossunited.doctype_ids import EVENT, EVENT_GRANTS, HACKATHON

_GRANTS_CHAPTER = frappe._dict(
    {
        "doctype": "FOSS Chapter",
        "chapter_name": "FOSS Event Grants",
        "chapter_type": "City Community",
    }
)


def get_foss_timeline_items(is_upcoming=True):
    """
    Returns combined normalized list of events, hackathons, and grants sorted by start date.
    """
    now = get_datetime(now_datetime())
    date_op = ">=" if is_upcoming else "<"

    events = frappe.get_all(
        EVENT,
        filters={
            "event_end_date": [date_op, now],
            "status": "Live" if is_upcoming else "Concluded",
        },
        or_filters={"is_published": 1, "is_external_event": 1},
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
            "event_description",
            "event_type",
            "modified",
            "chapter.chapter_type as _chapter_type",
            "chapter.city as _chapter_city",
        ],
    )

    hackathons = frappe.get_all(
        HACKATHON,
        filters={"is_published": 1, "end_date": [date_op, now]},
        fields=[
            "name",
            "route",
            "hackathon_name as event_name",
            "start_date as event_start_date",
            "end_date as event_end_date",
            "hackathon_banner as banner_image",
            "hackathon_type as event_location",
            "chapter",
            "hackathon_description as event_description",
            "modified",
            "chapter.chapter_type as _chapter_type",
            "chapter.city as _chapter_city",
        ],
    )

    grants = frappe.get_all(
        EVENT_GRANTS,
        filters={"grant_status": "Approved", "event_end_date": [date_op, now]},
        fields=[
            "name",
            "event_name",
            "event_description",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_website",
            "grant_amount",
            "modified",
        ],
    )

    for e in events:
        e["_kind"] = "event"

    for h in hackathons:
        h["_kind"] = "hackathon"
        h["must_attend"] = 1

    for g in grants:
        website = g.get("event_website") or f"/grants/events?s={g.event_name}"
        location = (g.get("event_location") or "").strip().title()
        city = location.split(",")[0].strip() if location else None
        g.update(
            {
                "route": website,
                "external_event_url": website,
                "is_external_event": 1,
                "banner_image": None,
                "chapter": frappe._dict({**_GRANTS_CHAPTER, "city": city}),
                "_chapter_type": "City Community",
                "_chapter_city": city,
                "event_location": location,
                "must_attend": (g.get("grant_amount") or 0) > 10000,
                "_kind": "grant",
            }
        )

    all_items = events + hackathons + grants
    all_items.sort(key=lambda x: get_datetime(x.get("event_start_date")), reverse=not is_upcoming)
    return all_items


def get_must_attend_events(limit=9):
    """Upcoming must-attend or City Community chapter events for web templates."""
    return [
        i
        for i in get_foss_timeline_items(is_upcoming=True)
        if i.get("must_attend") or i.get("_chapter_type") == "City Community"
    ][:limit]


def get_context(context, page_type="upcoming"):
    context.no_cache = 1
    context.page_type = page_type

    now = get_datetime(now_datetime())
    is_upcoming = page_type == "upcoming"

    context.title = "Upcoming Events - FOSS United" if is_upcoming else "Past Events - FOSS United"

    items = get_foss_timeline_items(is_upcoming=is_upcoming)

    context.all_cities = sorted({e.get("_chapter_city") for e in items if e.get("_chapter_city")})

    timeline = [
        {
            **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in item.items()},
            "_start": get_datetime(item.get("event_start_date")).isoformat(),
            "_end": get_datetime(item.get("event_end_date")).isoformat(),
            "_is_past": get_datetime(item.get("event_end_date")) < now,
        }
        for item in items
    ]

    context.timeline_events = timeline
