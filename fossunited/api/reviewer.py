import frappe
from frappe import _

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
    cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event})
    cfp = cfp_doc.name

    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": frappe.session.user}, "name")

    reviewed_count = frappe.db.count(
        PROPOSAL_REVIEW,
        {
            "reviewer_profile": reviewer_profile,
            "proposal": ("in", frappe.db.get_list(PROPOSAL, {"linked_cfp": cfp}, pluck="name")),
        },
    )

    active_phase = None
    for phase in cfp_doc.get("cfp_review_phases", []):
        if phase.is_active:
            active_phase = phase
            break

    filters = {"linked_cfp": cfp}
    if active_phase and active_phase.proposal_visibility == "Only Assigned":
        assigned_proposals = frappe.db.get_all(
            "CFP Reviewer Assignment", 
            filters={"reviewer": reviewer_profile},
            pluck="proposal"
        )
        if not assigned_proposals:
            return reviewed_count, 0
        filters["name"] = ("in", assigned_proposals)

    total_count = frappe.db.count(PROPOSAL, filters)
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
        frappe.throw(_("Unauthorized Access"), frappe.PermissionError)

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

        active_phase = None
        cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event.name})
        for phase in cfp_doc.get("cfp_review_phases", []):
            if phase.is_active:
                active_phase = phase
                break

        submission_count = frappe.db.count(PROPOSAL, {"linked_cfp": cfp})
        reviewed_count, not_reviewed_count = get_reviewed_count(event=event.name)
        
        phase_info = None
        if active_phase:
            phase_info = {
                "name": active_phase.phase_name,
                "proposal_visibility": active_phase.proposal_visibility,
                "can_see_other_reviews": active_phase.can_see_other_reviews
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
                "active_phase": phase_info
            }
        )

    return cfps_to_review

@frappe.whitelist()
def get_reviews_for_proposal(proposal: str) -> list:
    """
    Get all reviews and their child scores for a proposal.
    """
    frappe.only_for(["CFP Reviewer", "System Manager", "Chapter Team Member"])
    
    reviews = frappe.get_all(
        "FOSS Event CFP Review",
        filters={"proposal": proposal},
        fields=["*"]
    )
    
    for review in reviews:
        review.scores = frappe.get_all(
            "CFP Review Score",
            filters={"parent": review.name, "parenttype": "FOSS Event CFP Review"},
            fields=["*"]
        )
        
    return reviews

@frappe.whitelist()
def get_bulk_review_data(event: str) -> dict:
    frappe.only_for(["CFP Reviewer", "System Manager", "Chapter Team Member"])
    
    cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event})
    
    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": frappe.session.user}, "name")
    
    submissions = frappe.get_all(
        PROPOSAL,
        filters={"linked_cfp": cfp_doc.name},
        fields=["name", "talk_title", "status"]
    )
    
    categories = frappe.get_all(
        "CFP Score Category",
        filters={"event_cfp": cfp_doc.name, "active": 1},
        fields=["name", "category_name", "weight"]
    )
    
    reviews = frappe.get_all(
        "FOSS Event CFP Review",
        filters={
            "proposal": ("in", [s.name for s in submissions]),
            "reviewer_profile": reviewer_profile
        },
        fields=["name", "proposal", "to_approve"]
    )
    
    for review in reviews:
        review.scores = frappe.get_all(
            "CFP Review Score",
            filters={"parent": review.name, "parenttype": "FOSS Event CFP Review"},
            fields=["category", "score"]
        )
        
    return {
        "submissions": submissions,
        "categories": categories,
        "reviews": reviews
    }
