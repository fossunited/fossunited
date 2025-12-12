import ast
from zoneinfo import ZoneInfo

import frappe
from ics import Calendar, Event

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    CORE_TEAM,
    EVENT,
    EVENT_VOLUNTEER,
    USER_PROFILE,
)


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
            CHAPTER_MEMBER,
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
            EVENT_VOLUNTEER,
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
def check_if_chapter_or_event_core_member(event: str) -> bool:
    """
    A common function to check if user is either chapter or event member to give some access.
    This API function is intended to only apply for cases where every time event is created
    they would not add themselves to event_members table
    """
    event_doc = frappe.get_doc(EVENT, event, ["name"])
    chapter_id = event_doc.chapter
    is_team = bool(
        check_if_event_lead(event) or check_if_chapter_member(chapter_id, frappe.session.user)
    )
    return is_team


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
        tz_name = frappe.db.get_single_value("System Settings", "time_zone") or "Asia/Kolkata"
        tz = ZoneInfo(tz_name)
        start_dt = frappe.utils.get_datetime(event.event_start_date)
        end_dt = frappe.utils.get_datetime(event.event_end_date)
        # If naive, treat as local time in site TZ; if aware, convert
        start = start_dt.replace(tzinfo=tz) if start_dt.tzinfo is None else start_dt.astimezone(tz)
        end = end_dt.replace(tzinfo=tz) if end_dt.tzinfo is None else end_dt.astimezone(tz)

        # Skip if end is before start
        if end < start:
            continue

        e = Event()
        e.name = event.event_name
        e.location = event.event_location
        e.organizer = event.chapter_name + " Community"
        # Optional hardening (keep if desired):
        e.description = frappe.utils.strip_html(event.event_description or "") or None
        if event.route:
            e.url = f"https://fossunited.org/{str(event.route).lstrip('/')}"
        e.begin = start
        e.end = end
        c.events.add(e)

    return c.serialize()


def get_chapter_members_email(chapter):
    return frappe.db.get_all(
        CHAPTER_MEMBER,
        {
            "parent": chapter,
            "role": ["in", [CORE_TEAM, "Volunteer"]],
        },
        pluck="email",
    )
