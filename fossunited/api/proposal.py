import frappe

from fossunited.api.cfp import get_custom_answers, get_speakers
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
    cfp = frappe.db.get_value(
        EVENT_CFP,
        {"event": event},
        ["anonymise_proposals", "has_public_custom_responses"],
        as_dict=True,
    )

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
        if not cfp.anonymise_proposals:
            proposal["_speaker"] = get_speakers(proposal.name)
        if cfp.has_public_custom_responses:
            proposal.update(get_custom_answers(proposal.name))

    return proposals


@frappe.whitelist(allow_guest=True)
def get_public_proposal_filters(
    event: str,
):
    filter_fields = [
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "options": "Approved\nRejected\nReview Pending\nScreening",
            "label": "Status",
        },
        {
            "fieldname": "session_type",
            "fieldtype": "Select",
            "options": "Talk\nLightning Talk\nWorkshop\nPanel Discussion\nBirds of Feather(BoF)",
            "label": "Session Type",
        },
        {
            "fieldname": "is_first_talk",
            "fieldtype": "Select",
            "options": "Yes\nNo",
            "label": "Is First Talk?",
        },
        {
            "label": "Intended Audience",
            "fieldname": "intended_audience",
            "fieldtype": "Select",
            "options": "Beginner\nIntermediate\nAdvanced",
        },
    ]

    cfp = frappe.db.get_value(
        EVENT_CFP, {"event": event}, ["name", "has_public_custom_responses"], as_dict=True
    )

    if cfp.has_public_custom_responses:
        custom_fields = frappe.get_all(
            "FOSS Custom Question",
            filters={
                "parenttype": EVENT_CFP,
                "parent": cfp.name,
            },
            fields=["question", "type", "description", "options"],
            limit_page_length=9999,
        )

        for index, field in enumerate(custom_fields, start=1):
            if field.type == "Radio Group":
                field.type = "Select"

            filter_fields.append(
                {
                    "fieldname": f"custom_question_{index}",
                    "fieldtype": field.type,
                    "label": field.question,
                    "options": field.options or "",
                }
            )

    return filter_fields
