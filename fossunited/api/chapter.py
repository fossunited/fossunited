import ast
from datetime import timedelta, timezone

import frappe
from ics import Calendar, Event

from fossunited.doctype_ids import CHAPTER, EVENT, USER_PROFILE


@frappe.whitelist(allow_guest=True)
def check_if_chapter_member(chapter: str, user: str) -> bool:
    """
    Check if the user is a member of the chapter.

    Args:
        chapter (str): Chapter id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": user}, ["name"])

    if not profile:
        return False

    is_member = bool(
        frappe.db.exists(
            "FOSS Chapter Lead Team Member",
            {
                "parent": chapter,
                "parenttype": CHAPTER,
                "chapter_member": profile,
                "parentfield": "chapter_members",
            },
        )
    )

    return is_member


@frappe.whitelist(allow_guest=True)
def check_if_event_lead(event: str) -> bool:
    """
    Check if the user is an event lead

    Args:
        event (str): Event id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": frappe.session.user}, ["name"])

    is_lead = bool(
        frappe.db.exists(
            "FOSS Chapter Event Member",
            {
                "parent": event,
                "parenttype": EVENT,
                "member": profile,
                "parentfield": "event_members",
                "role": "Core Team Member",
            },
        )
    )

    return is_lead


@frappe.whitelist(allow_guest=True)
def generate_ics(event_ids):
    """
    Return ICS event for the event ids provided

    Args:
        event_ids (list): list of event ids (doc.name)

    Returns:
        str: ICS data
    """

    c = Calendar()
    ids = ast.literal_eval(event_ids)

    events = frappe.db.get_all(
        EVENT,
        filters=[["name", "IN", ids]],
        fields=[
            "event_name",
            "event_location",
            "chapter_name",
            "event_description",
            "route",
            "event_start_date",
            "event_end_date",
        ],
    )
    for event in events:
        start = event.event_start_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        end = event.event_end_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))

        # Skip if end is before start
        if end < start:
            continue

        e = Event()
        e.name = event.event_name
        e.location = event.event_location
        e.organizer = event.chapter_name + " Community"
        e.description = event.event_description
        e.url = "https://fossunited.org/" + str(event.route)
        e.begin = start
        e.end = end
        c.events.add(e)

    return c.serialize()
