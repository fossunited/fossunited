from datetime import datetime

import frappe
from frappe.utils import get_datetime, now_datetime

from fossunited.doctype_ids import CHAPTER, EVENT, HACKATHON


def get_context(context):
    context.no_cache = 1
    context.title = "Events Timeline - FOSS United"

    now = get_datetime(now_datetime())

    events = frappe.get_all(
        EVENT,
        filters={"is_published": 1},
        fields=["*"],
    )

    hackathons = frappe.get_all(
        HACKATHON,
        filters={"is_published": 1},
        fields=["*"],
    )

    chapter_type_map = {
        c.name: c.chapter_type for c in frappe.get_all(CHAPTER, fields=["name", "chapter_type"])
    }

    timeline = []

    for e in events:
        start_dt = get_datetime(e.get("event_start_date"))
        end_dt = get_datetime(e.get("event_end_date"))

        row = {
            **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in e.items()},
            "_kind": "event",
            "_start": start_dt.isoformat(),
            "_end": end_dt.isoformat(),
            "_is_past": end_dt < now,
            "_chapter_type": chapter_type_map.get(e.get("chapter")),
        }

        timeline.append(row)

    for h in hackathons:
        start_dt = get_datetime(h.get("start_date"))
        end_dt = get_datetime(h.get("end_date"))

        row = {
            **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in h.items()},
            "_kind": "hackathon",
            "_start": start_dt.isoformat(),
            "_end": end_dt.isoformat(),
            "_is_past": end_dt < now,
            "_chapter_type": chapter_type_map.get(h.get("chapter")),
        }

        timeline.append(row)

    context.timeline_events = timeline
