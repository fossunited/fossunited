import frappe

from fossunited.api.cfp import get_speakers
from fossunited.doctype_ids import EVENT_CFP, PROPOSAL
from fossunited.fossunited.utils import get_doc_likes


@frappe.whitelist(allow_guest=True)
def get_event_proposals(
    event: str,
) -> list:
    """
    Get all the proposal submissions for the given event.

    Adds number of likes, and redacts speaker name based on is_anonymise condition

    Args:
        event (str): The id of the event

    Returns:
        list: proposals of an event
    """
    has_anonymous_cfps = frappe.db.get_value(EVENT_CFP, {"event": event}, "anonymise_proposals")

    fields = [
        "name",
        "route",
        "talk_title",
        "session_type",
        "status",
        "session_categories",
        "intended_audience",
        "creation",
        "modified",
    ]

    proposals = frappe.get_all(
        PROPOSAL,
        filters={"event": event},
        fields=fields,
        page_length=99999,
        order_by="talk_title",
    )

    for proposal in proposals:
        likes = get_doc_likes(PROPOSAL, proposal.name)
        proposal["_likes"] = len(likes)
        proposal["_is_liked_by_user"] = frappe.session.user in likes

    if not has_anonymous_cfps:
        for proposal in proposals:
            proposal["_speaker"] = get_speakers(proposal.name)

    return proposals


@frappe.whitelist(allow_guest=True)
def get_public_proposal_filters():
    filter_fields = [
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "options": "Approved\nRejected\nReview Pending\nScreening",
            "label": "Status",
        },
    ]

    return filter_fields
