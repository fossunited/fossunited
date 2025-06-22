import frappe

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    PROPOSAL_REVIEW,
    USER_PROFILE,
)


def has_reviewer_role() -> bool:
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "CFP Reviewer", "parent": frappe.session.user},
        )
    )


def get_reviewed_count(event: str) -> tuple:
    """
    Return the count of reviewed / not reviewed proposals for an event

    Args:
        event: event ID

    returns:
        tuple: (reviewed count, not reviewed count)
    """
    cfp = frappe.db.get_value(EVENT_CFP, {"event": event}, "name")

    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": frappe.session.user}, "name")

    reviewed_count = frappe.db.count(
        PROPOSAL_REVIEW,
        {
            "parenttype": PROPOSAL,
            "reviewer_profile": reviewer_profile,
            "parent": ("in", frappe.db.get_list(PROPOSAL, {"linked_cfp": cfp}, pluck="name")),
        },
    )

    total_count = frappe.db.count(PROPOSAL, {"linked_cfp": cfp})
    not_reviewed_count = total_count - reviewed_count

    return reviewed_count, not_reviewed_count


@frappe.whitelist()
def get_events_by_open_cfp() -> list:
    """
    Get all the upcoming events with open CFP

    Returns:
        list: List of events with open CFP
    """
    if not has_reviewer_role():
        frappe.throw("Unauthorized Access", frappe.PermissionError)

    events = frappe.get_all(
        EVENT,
        filters={
            "status": "Live",
            "is_published": 1,
            "event_start_date": [">=", frappe.utils.nowdate()],
            "is_external_event": 0,
        },
        fields=[
            "name",
            "chapter",
            "event_name",
            "event_start_date",
            "event_end_date",
        ],
        page_length=99,
        order_by="event_start_date",
    )

    cfps_to_review = []

    for event in events:
        cfp = frappe.db.get_value(
            EVENT_CFP,
            {"event": event.name},
            ["name"],
            pluck=True,
        )

        if not cfp:
            continue

        chapter = frappe.db.get_value(
            CHAPTER,
            event.chapter,
            ["name", "chapter_name", "chapter_type"],
            as_dict=1,
        )

        submission_count = frappe.db.count(PROPOSAL, {"linked_cfp": cfp})
        reviewed_count, not_reviewed_count = get_reviewed_count(event=event.name)

        cfps_to_review.append(
            {
                "event": event.name,
                "event_name": event.event_name,
                "start_date": event.event_start_date,
                "end_date": event.event_end_date,
                "cfp": cfp,
                "submission_count": submission_count,
                "reviewed_count": reviewed_count,
                "not_reviewed_count": not_reviewed_count,
                "chapter": chapter.name,
                "chapter_name": chapter.chapter_name,
                "chapter_type": chapter.chapter_type,
            }
        )

    return cfps_to_review
