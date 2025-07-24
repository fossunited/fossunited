from collections import defaultdict
from datetime import datetime

import frappe

from fossunited.doctype_ids import EVENT


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
        "FOSS Event Schedule",
        {"parent": event_id, "parenttype": EVENT},
        ["*"],
        order_by="start_time",
    )

    # Build a sorted list of unique dates
    unique_dates = sorted({session["scheduled_date"] for session in schedule})
    date_to_day = {format_date(date): idx + 1 for idx, date in enumerate(unique_dates)}

    # Group by date and hall in a single pass
    schedule_by_date_and_hall = defaultdict(lambda: defaultdict(list))
    for session in schedule:
        date_str = format_date(session["scheduled_date"])
        hall = session.get("hall") or "no-hall"
        session.day = date_to_day[date_str]

        linked_cfp = session.get("linked_cfp")
        if linked_cfp:
            proposal_route = frappe.db.get_value("FOSS Event CFP Submission", linked_cfp, "route")
            session["cfp_route"] = proposal_route
            speakers = frappe.db.get_all(
                "CFP Submission Speaker",
                {"parent": linked_cfp},
                [
                    "full_name",
                    "designation",
                    "organization",
                    "bio",
                    "photo",
                    "linked_user",
                    "social_link",
                ],
            )
            session["cfp_speakers"] = speakers
        else:
            session["cfp_route"] = None
            session["cfp_speakers"] = []

        schedule_by_date_and_hall[date_str][hall].append(session)

    sorted_schedule = {
        date: dict(halls)
        for date, halls in sorted(
            schedule_by_date_and_hall.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%Y")
        )
    }
    return sorted_schedule
