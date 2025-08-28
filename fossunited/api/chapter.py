import ast
from datetime import timedelta, timezone

import frappe
from ics import Calendar, Event

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_VOLUNTEER,
    RSVP_CUSTOM_FIELD,
    RSVP_RESPONSE,
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
        e = Event()
        e.name = event.event_name
        e.location = event.event_location
        e.organizer = event.chapter_name + " Community"
        e.description = event.event_description
        e.url = "https://fossunited.org/" + str(event.route)
        e.begin = event.event_start_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        e.end = event.event_end_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        c.events.add(e)

    return c.serialize()


@frappe.whitelist()
def get_submissions_with_answers(event_id):
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)

    submissions = frappe.get_all(
        RSVP_RESPONSE,
        filters={"event": event_id},
        fields=["name", "name1", "email", "im_a"],
    )

    if not check_if_event_lead(event_id):
        # Mask email and return without answers
        for s in submissions:
            s["email"] = mask_email(s["email"])
        return submissions

    # Event lead: fetch answers
    submission_ids = [s["name"] for s in submissions]

    answers = frappe.get_all(
        RSVP_CUSTOM_FIELD,
        filters={"parent": ["in", submission_ids]},
        fields=["parent", "question", "response"],
    )

    answers_by_parent = {}
    for a in answers:
        answers_by_parent.setdefault(a["parent"], []).append(a)

    for s in submissions:
        for a in answers_by_parent.get(s["name"], []):
            # Use question as field key
            s[a["question"]] = a["response"]

    return submissions


def mask_email(email):
    import re

    return re.sub(r"(?<=.{3}).(?=[^@]*?@)", "*", email)
