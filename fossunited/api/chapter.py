import ast
from collections import defaultdict
from zoneinfo import ZoneInfo

import frappe
from frappe.query_builder import DocType, Order
from frappe.utils import get_datetime, getdate
from ics import Calendar, Event

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    CORE_TEAM,
    EVENT,
    EVENT_CHECKIN,
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


@frappe.whitelist()
def get_submissions_with_answers(event_id: str) -> list[dict]:
    """
    Get all RSVP submissions with their custom field answers.

    Args:
        event_id (str): Event ID

    Returns:
        list[dict]: List of submissions with custom answers as dynamic fields
    """
    if not check_if_chapter_or_event_core_member(event_id):
        frappe.throw("Not permitted", frappe.PermissionError)

    # Get all submissions
    submissions = frappe.get_all(
        RSVP_RESPONSE,
        filters={"event": event_id},
        fields=["name", "confirm_attendance", "status", "name1", "email", "im_a"],
        order_by="creation asc",
    )

    if not submissions:
        return []

    # Get all custom field answers for these submissions
    submission_ids = [s["name"] for s in submissions]

    answers = frappe.get_all(
        RSVP_CUSTOM_FIELD,
        filters={
            "parent": ["in", submission_ids],
            "parenttype": RSVP_RESPONSE,
            "parentfield": "custom_answers",
        },
        fields=["parent", "question", "response"],
        order_by="parent asc, idx asc",
    )

    # Group answers by parent (submission)
    answers_map = {}
    for answer in answers:
        parent = answer["parent"]
        if parent not in answers_map:
            answers_map[parent] = {}

        # Use question as key, response as value
        question = answer["question"] or "custom_field"
        answers_map[parent][question] = answer["response"] or ""

    # merge answers into submissions
    for submission in submissions:
        submission_id = submission["name"]
        if submission_id in answers_map:
            submission.update(answers_map[submission_id])

    return submissions


@frappe.whitelist()
def get_checked_in_attendees(event_id):
    # event date check (same guard as before)
    if not check_if_chapter_or_event_core_member(event_id):
        frappe.throw("Not permitted, only intended for event core team.", frappe.PermissionError)

    event_start, event_end = frappe.db.get_value(
        EVENT, event_id, ["event_start_date", "event_end_date"]
    )
    if not event_start or not event_end:
        return {"show_checkins": False, "attendees": [], "by_date": {}}
    now = get_datetime()
    if not (get_datetime(event_start) <= now):
        return {"show_checkins": False, "attendees": [], "by_date": {}}

    Submission = DocType(RSVP_RESPONSE)
    CheckIn = DocType(EVENT_CHECKIN)

    rows = (
        frappe.qb.from_(CheckIn)
        .join(Submission)
        .on(CheckIn.parent == Submission.name)
        .select(
            Submission.name.as_("submission"),
            Submission.name1,
            Submission.email,
            Submission.im_a,
            CheckIn.check_in_time,
        )
        .where(Submission.event == event_id)
        .where(Submission.status == "Accepted")
        .where(Submission.confirm_attendance == 1)
        .where(CheckIn.parenttype == RSVP_RESPONSE)
        .where(CheckIn.parentfield == "check_ins")
        .orderby(CheckIn.check_in_time, Order.desc)
        .run(as_dict=True)
    )

    total_accepted = frappe.db.count(
        RSVP_RESPONSE,
        filters={"event": event_id, "status": "Accepted"},
    )

    if not rows:
        return {
            "show_checkins": True,
            "attendees": [],
            "by_date": {},
            "total_checked_in": 0,
            "total_accepted": total_accepted,
            "event_start": str(getdate(event_start)),
            "event_end": str(getdate(event_end)),
        }

    checkins_by_parent = defaultdict(list)
    by_date = defaultdict(lambda: {"date": None, "attendees": []})

    for r in rows:
        p, t = r["submission"], r["check_in_time"]
        checkins_by_parent[p].append(r)
        date_key = str(getdate(t))
        if by_date[date_key]["date"] is None:
            by_date[date_key]["date"] = date_key
        by_date[date_key]["attendees"].append(
            {
                "name": p,
                "name1": r.get("name1"),
                "email": r.get("email"),
                "im_a": r.get("im_a"),
                "check_in_time": t,
            }
        )

    attendees = [
        {
            "name": p,
            "name1": lst[0].get("name1"),
            "email": lst[0].get("email"),
            "im_a": lst[0].get("im_a"),
            "check_in_time": lst[0].get("check_in_time"),
            "total_check_ins": len(lst),
        }
        for p, lst in checkins_by_parent.items()
    ]

    by_date_sorted = {d: by_date[d] for d in sorted(by_date)}

    return {
        "show_checkins": True,
        "attendees": attendees,
        "by_date": by_date_sorted,
        "total_checked_in": len(attendees),
        "total_accepted": total_accepted,
        "event_start": str(getdate(event_start)),
        "event_end": str(getdate(event_end)),
    }


@frappe.whitelist()
def get_chapter_members_email(chapter):
    return frappe.db.get_all(
        CHAPTER_MEMBER,
        {
            "parent": chapter,
            "role": ["in", [CORE_TEAM, "Volunteer"]],
        },
        pluck="email",
    )
