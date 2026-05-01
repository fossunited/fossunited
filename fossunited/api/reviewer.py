import frappe
from frappe import _

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    PROPOSAL_REVIEW,
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
    Return (reviewed_count, not_reviewed_count) for the current reviewer on an event.

    Reviews are child rows on the submission; uses Frappe ToDo for "Only Assigned" phase
    visibility.
    """
    cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event})
    cfp = cfp_doc.name

    all_proposal_names = frappe.db.get_list(PROPOSAL, {"linked_cfp": cfp}, pluck="name")

    reviewed_count = frappe.db.count(
        PROPOSAL_REVIEW,
        {
            "email": frappe.session.user,
            "parent": ("in", all_proposal_names),
            "parenttype": "FOSS Event CFP Submission",
        },
    )

    active_phase = next(
        (p for p in cfp_doc.get("cfp_review_phases", []) if p.is_active), None
    )

    filters = {"linked_cfp": cfp}
    if active_phase and active_phase.proposal_visibility == "Only Assigned":
        assigned_proposals = frappe.db.get_all(
            "ToDo",
            filters={
                "reference_type": PROPOSAL,
                "reference_name": ("in", all_proposal_names),
                "allocated_to": frappe.session.user,
                "status": "Open",
            },
            pluck="reference_name",
        )
        if not assigned_proposals:
            return reviewed_count, 0
        filters["name"] = ("in", assigned_proposals)

    total_count = frappe.db.count(PROPOSAL, filters)
    return reviewed_count, total_count - reviewed_count


@frappe.whitelist()
def get_events_by_open_cfp() -> list:
    """
    Return all upcoming events with an open CFP that the current reviewer can see.
    Includes active phase info and reviewed/pending counts for the MyReviews landing page.
    """
    if not has_reviewer_role():
        frappe.throw(_("Unauthorized Access"), frappe.PermissionError)

    events = frappe.get_all(
        EVENT,
        filters={
            "status": "Live",
            "is_published": 1,
            "event_start_date": [">=", frappe.utils.nowdate()],
            "is_external_event": 0,
        },
        fields=["name", "chapter", "event_name", "event_start_date", "event_end_date"],
        page_length=99,
        order_by="event_start_date",
    )

    cfps_to_review = []

    for event in events:
        cfp = frappe.db.get_value(EVENT_CFP, {"event": event.name}, "name", pluck=True)
        if not cfp:
            continue

        chapter = frappe.db.get_value(
            CHAPTER,
            event.chapter,
            ["name", "chapter_name", "chapter_type"],
            as_dict=1,
        )

        cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event.name})
        active_phase = next(
            (p for p in cfp_doc.get("cfp_review_phases", []) if p.is_active), None
        )

        submission_count = frappe.db.count(PROPOSAL, {"linked_cfp": cfp})
        reviewed_count, not_reviewed_count = get_reviewed_count(event=event.name)

        phase_info = None
        if active_phase:
            phase_info = {
                "name": active_phase.phase_name,
                "proposal_visibility": active_phase.proposal_visibility,
                "can_see_other_reviews": active_phase.can_see_other_reviews,
            }

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
                "active_phase": phase_info,
            }
        )

    return cfps_to_review
