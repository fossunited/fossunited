from collections import defaultdict
from datetime import datetime

import frappe

from fossunited.doctype_ids import EVENT, EVENT_SCHEDULE, PROPOSAL, SPEAKER


def format_date(date_obj):
    """Format a date object to 'dd/mm/YYYY' string."""
    return date_obj.strftime("%d/%m/%Y")


@frappe.whitelist(allow_guest=True)
def get_event_schedule(event_id: str) -> dict:
    """
    Get the schedule for the event, grouped by date and hall.
    For each schedule item with a linked_cfp, also fetch the proposal route and speakers.

    Args:
        event_id (str): Event ID

    Returns:
        dict: {date: {hall: [sessions]}}
    """
    schedule = frappe.db.get_all(
        EVENT_SCHEDULE,
        {"parent": event_id, "parenttype": EVENT},
        ["*"],
        order_by="start_time",
    )

    # Build a sorted list of unique dates
    unique_dates = sorted({session["scheduled_date"] for session in schedule})
    date_to_day = {format_date(date): idx + 1 for idx, date in enumerate(unique_dates)}

    # Batch fetch all linked_cfp proposal routes and speakers
    linked_cfp_set = {
        session.get("linked_cfp") for session in schedule if session.get("linked_cfp")
    }
    linked_cfp_list = list(linked_cfp_set)

    # Batch fetch proposal routes
    proposal_routes = (
        frappe.db.get_all(
            PROPOSAL,
            filters={"name": ("in", linked_cfp_list)} if linked_cfp_list else {},
            fields=["name", "route"],
        )
        if linked_cfp_list
        else []
    )
    route_lookup = {row["name"]: row["route"] for row in proposal_routes}

    # Batch fetch all speakers for these proposals
    speakers = (
        frappe.db.get_all(
            SPEAKER,
            filters={"parent": ("in", linked_cfp_list)} if linked_cfp_list else {},
            fields=[
                "parent",
                "full_name",
                "designation",
                "organization",
                "bio",
                "photo",
                "linked_user",
                "social_link",
            ],
        )
        if linked_cfp_list
        else []
    )
    speakers_lookup = {}
    for speaker in speakers:
        parent = speaker.pop("parent")
        speakers_lookup.setdefault(parent, []).append(speaker)

    # Group by date and hall, enrich with batch-fetched data
    schedule_by_date_and_hall = defaultdict(lambda: defaultdict(list))
    for session in schedule:
        date_str = format_date(session["scheduled_date"])
        hall = session.get("hall") or "no-hall"
        session.day = date_to_day[date_str]

        linked_cfp = session.get("linked_cfp")
        if linked_cfp:
            session["cfp_route"] = route_lookup.get(linked_cfp)
            session["cfp_speakers"] = speakers_lookup.get(linked_cfp, [])
        else:
            session["cfp_route"] = None
            session["cfp_speakers"] = []

        schedule_by_date_and_hall[date_str][hall].append(session)

    # Convert defaultdicts to dicts and sort by date
    sorted_schedule = {
        date: dict(halls)
        for date, halls in sorted(
            schedule_by_date_and_hall.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%Y")
        )
    }
    return sorted_schedule
