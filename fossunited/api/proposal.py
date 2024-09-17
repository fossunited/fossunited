import frappe

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

    fields = [
        "name",
        "route",
        "talk_title",
        "session_type",
        "full_name",
        "status",
    ]

    proposals = frappe.get_all(
        PROPOSAL,
        filters={"event": event},
        fields=fields,
        page_length=99999,
        order_by="talk_title",
    )

    is_cfp_anonymous = frappe.db.get_value(EVENT_CFP, {"event": event}, "anonymise_proposals")

    for proposal in proposals:
        proposal["likes"] = len(get_doc_likes(PROPOSAL, proposal["name"]))
        if is_cfp_anonymous and proposal.status != "Approved":
            proposal.full_name = ""
        del proposal["name"]

    return proposals
