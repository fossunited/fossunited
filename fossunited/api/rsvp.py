import frappe
from frappe.query_builder import DocType, Order
from frappe.query_builder.functions import Coalesce
from frappe.utils import get_datetime

from fossunited.api.chapter import check_if_chapter_or_event_core_member
from fossunited.doctype_ids import (
    EVENT,
    EVENT_CHECKIN,
    RSVP_CUSTOM_FIELD,
    RSVP_RESPONSE,
)


@frappe.whitelist()
def get_submissions_with_answers(event_id: str) -> list:
    """
    Get all RSVP submissions with custom field answers as flat records.
    Returns: list of dicts with dynamic custom field keys
    """
    if not check_if_chapter_or_event_core_member(event_id):
        frappe.throw("Not permitted", frappe.PermissionError)

    rsvp = DocType(RSVP_RESPONSE)
    custom = DocType(RSVP_CUSTOM_FIELD)

    results = (
        frappe.qb.from_(rsvp)
        .left_join(custom)
        .on(
            (custom.parent == rsvp.name)
            & (custom.parenttype == RSVP_RESPONSE)
            & (custom.parentfield == "custom_answers")
        )
        .select(
            rsvp.name,
            rsvp.confirm_attendance,
            rsvp.status,
            rsvp.name1,
            rsvp.email,
            rsvp.im_a,
            Coalesce(custom.question, "").as_("question"),
            Coalesce(custom.response, "").as_("response"),
        )
        .where(rsvp.event == event_id)
        .orderby(rsvp.creation)
        .orderby(custom.idx)
    ).run(as_dict=True)

    if not results:
        return []

    # flatten the structure
    # the raw results will have dup items with each custom fields
    submissions_map = {}
    for row in results:
        sub_id = row["name"]
        if sub_id not in submissions_map:
            submissions_map[sub_id] = {
                "confirm_attendance": row["confirm_attendance"],
                "status": row["status"],
                "name1": row["name1"],
                "email": row["email"],
                "im_a": row["im_a"],
            }
        if row["question"]:
            submissions_map[sub_id][row["question"]] = row["response"] or ""

    return list(submissions_map.values())


@frappe.whitelist()
def get_rsvp_checkins(event_id: str) -> list:
    """
    Get all check-ins for an event.
    Returns: list of check-in records with attendee details
    """
    if not check_if_chapter_or_event_core_member(event_id):
        frappe.throw("Not permitted", frappe.PermissionError)

    Submission = DocType(RSVP_RESPONSE)
    CheckIn = DocType(EVENT_CHECKIN)

    checkins = (
        frappe.qb.from_(CheckIn)
        .join(Submission)
        .on(CheckIn.parent == Submission.name)
        .select(
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

    return checkins


@frappe.whitelist()
def if_rsvp_show_checkins(event_id: str) -> bool:
    """
    Check if check-ins should be shown (event has started).
    Returns: boolean
    """
    event_start = frappe.db.get_value(EVENT, event_id, "event_start_date")
    if not event_start:
        return False

    now = get_datetime()
    return get_datetime(event_start) <= now


@frappe.whitelist()
def get_rsvp_checkin_stats(event_id: str) -> dict:
    """
    Get event statistics.
    Returns: dict with counts
    """
    total_accepted = frappe.db.count(
        RSVP_RESPONSE,
        filters={"event": event_id, "status": "Accepted", "confirm_attendance": 1},
    )

    return {"total_accepted": total_accepted}
