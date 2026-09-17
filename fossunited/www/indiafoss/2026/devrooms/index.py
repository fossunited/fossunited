import json

import frappe

from fossunited.doctype_ids import EVENT, EVENT_CFP, EVENT_SCHEDULE, PROPOSAL, SPEAKER
from fossunited.fossunited.event_media import get_indiafoss_years
from fossunited.fossunited.user_utils import fetch_user_profiles

INDIAFOSS_2026_EVENT = "IndiaFOSS 2026"


def get_context(context):
    context.no_cache = 1
    context.hide_nav, context.hide_footer = True, True

    slug = frappe.form_dict.slug
    if not slug:
        raise frappe.DoesNotExistError

    event_docname = frappe.db.get_value(EVENT, {"event_name": INDIAFOSS_2026_EVENT}, "name")
    if not event_docname:
        raise frappe.DoesNotExistError

    devroom = frappe.db.get_value(
        "Devroom Custom",
        {"event": event_docname, "slug": slug},
        ["name", "title", "slug", "logo", "tagline", "description", "manager_section", "pattern"],
        as_dict=True,
    )
    if not devroom:
        raise frappe.DoesNotExistError

    context.devroom = devroom
    context.pattern = devroom.pattern

    # CFP status
    cfp_status = frappe.db.get_value(EVENT_CFP, {"event": event_docname}, "status")
    cfp_deadline = frappe.db.get_value(EVENT_CFP, {"event": event_docname}, "deadline")
    cfp_is_live = cfp_status == "Live"
    context.cfp_is_live = cfp_is_live
    context.cfp_is_closed = not cfp_is_live
    if cfp_is_live:
        context.cfp_text = "Specify the devroom while proposing your session in the track field."
    else:
        context.cfp_text = f"Closed on {cfp_deadline}" if cfp_deadline else "Closed"

    event = frappe.get_doc(EVENT, event_docname)
    context.cfp_route = f"/{event.route}/cfp" if cfp_is_live else ""

    # Submissions: find via FOSS Custom Answer linking to this devroom title
    submission_ids = frappe.db.get_all(
        "FOSS Custom Answer",
        {"response": devroom.title},
        pluck="parent",
    )

    submissions = []
    if submission_ids:
        submissions = frappe.db.get_all(
            PROPOSAL,
            filters={
                "name": ("in", submission_ids),
                "status": "Approved",
                "event": event_docname,
            },
            fields=["name", "talk_title", "session_type", "intended_audience", "status", "route"],
            order_by="talk_title asc",
        )

    for s in submissions:
        s.route = f"/{s.route}"
        s.speakers = frappe.get_all(
            SPEAKER,
            filters={"parent": s.name},
            fields=["full_name", "photo"],
        )

    context.submissions = submissions

    # Schedule: items linked to approved proposals for this devroom
    schedule_items = []
    if submissions:
        cfp_names = [s.name for s in submissions]
        schedule_items = frappe.get_all(
            EVENT_SCHEDULE,
            filters={"linked_cfp": ("in", cfp_names)},
            fields=[
                "title",
                "hall",
                "scheduled_date",
                "start_time",
                "end_time",
                "linked_cfp",
                "category",
            ],
            order_by="scheduled_date asc, start_time asc",
        )

    schedule_by_date = {}
    for item in schedule_items:
        date_str = item.scheduled_date.strftime("%-d %B %Y") if item.scheduled_date else "TBA"
        schedule_by_date.setdefault(date_str, []).append(item)
        item.start_time_display = _fmt_timedelta(item.start_time)
        item.end_time_display = _fmt_timedelta(item.end_time)
        cfp_match = next((s for s in submissions if s.name == item.linked_cfp), None)
        item.speakers = cfp_match.speakers if cfp_match else []
        item.cfp_route = cfp_match.route if cfp_match else None

    context.schedule_by_date = schedule_by_date
    context.has_schedule = bool(schedule_items)

    # Devroom managers
    context.manager_section = devroom.manager_section or ""
    event_data = json.loads(event.get("event_data") or "{}")
    devroom_members = event_data.get("devrooms", {}).get(devroom.title, [])
    context.managers = (
        fetch_user_profiles(devroom_members, f"{devroom.title} Devroom Manager", force_bio=True)
        if devroom_members
        else []
    )

    context.years = get_indiafoss_years()
    context.current_year = 2026

    context.pagetitle = f"{devroom.title} Devroom — IndiaFOSS 2026"
    context.description = devroom.tagline or (
        devroom.description[:150]
        if devroom.description
        else f"{devroom.title} devroom at IndiaFOSS 2026"
    )
    context.image = "https://fossunited.org/files/indiafoss-2026-og.png"


def _fmt_timedelta(td):
    if not td:
        return ""
    s = int(td.total_seconds())
    h, m = (s // 3600) % 24, (s % 3600) // 60
    suffix = "AM" if h < 12 else "PM"
    return f"{(h % 12) or 12:02d}:{m:02d} {suffix}"
