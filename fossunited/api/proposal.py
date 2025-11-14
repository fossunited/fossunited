import frappe
from frappe import qb

from fossunited.doctype_ids import EVENT, EVENT_CFP, PROPOSAL, SPEAKER


@frappe.whitelist(allow_guest=True)
def get_event_proposals(event: str) -> dict:
    """
    Get all the proposal submissions for the given event.

    Adds number of likes, and redacts speaker name based on is_anonymise condition

    Args:
        event (str): The id of the event

    Returns:
        dict: {
            "proposals": list[dict],
            "custom_questions": list[dict],
            "event_route": str,
            "event_name": str,
        }
    """
    # Get CFP settings in a single query
    cfp = frappe.db.get_value(
        EVENT_CFP,
        {"event": event},
        ["name", "anonymise_proposals", "has_public_custom_responses"],
        as_dict=True,
    )

    event_route, event_name = frappe.db.get_value(EVENT, event, ["route", "event_name"])

    # Use frappe.qb for the main proposals query for better performance
    Proposal = qb.DocType(PROPOSAL)

    proposals_query = (
        qb.from_(Proposal)
        .select(
            Proposal.name,
            Proposal.route,
            Proposal.talk_title,
            Proposal.session_type,
            Proposal.status,
            Proposal.session_categories,
            Proposal.intended_audience,
            Proposal.creation,
            Proposal.modified,
        )
        .where(Proposal.event == event)
        .orderby(Proposal.talk_title)
    )

    proposals = proposals_query.run(as_dict=True)

    if not proposals:
        return proposals

    proposal_names = [proposal.name for proposal in proposals]
    current_user = frappe.session.user

    # Bulk fetch likes count and user like status
    likes_data = _get_bulk_likes_data(proposal_names, current_user)

    # Bulk fetch speakers if needed
    speakers_data = {}
    if not cfp.anonymise_proposals:
        speakers_data = _get_bulk_speakers_data(proposal_names)

    # Bulk fetch custom answers if needed
    custom_answers_data = {}
    if cfp.has_public_custom_responses:
        custom_answers_data = _get_bulk_custom_answers_data(proposal_names)

    # Combine all data
    for proposal in proposals:
        proposal_name = proposal.name

        # Add likes data
        if proposal_name in likes_data:
            proposal["_likes"] = likes_data[proposal_name]["count"]
            proposal["_is_liked_by_user"] = likes_data[proposal_name]["is_liked_by_user"]
        else:
            proposal["_likes"] = 0
            proposal["_is_liked_by_user"] = False

        # Add speakers data
        if not cfp.anonymise_proposals:
            proposal["_speaker"] = speakers_data.get(proposal_name, [])

        # Add custom answers data
        if cfp.has_public_custom_responses:
            proposal.update(custom_answers_data.get(proposal_name, {}))

    custom_questions = []
    if cfp.has_public_custom_responses:
        custom_questions = frappe.get_all(
            "FOSS Custom Question",
            filters={"parenttype": EVENT_CFP, "parent": cfp.name},
            fields=["idx", "question"],
            order_by="idx asc",
        )

    return {
        "proposals": proposals,
        "custom_questions": custom_questions,
        "event_route": event_route,
        "event_name": event_name,
    }


def _get_bulk_likes_data(proposal_names: list, current_user: str) -> dict:
    """
    Bulk fetch likes count and user like status for all proposals.

    Returns:
        dict: {proposal_name: {"count": int, "is_liked_by_user": bool}}
    """
    if not proposal_names:
        return {}

    # Use frappe.qb for better performance
    Comment = qb.DocType("Comment")

    # Get all likes for the proposals with optimized query
    likes_query = (
        qb.from_(Comment)
        .select(Comment.reference_name, Comment.comment_email)
        .where(
            (Comment.comment_type == "Like")
            & (Comment.reference_doctype == PROPOSAL)
            & (Comment.reference_name.isin(proposal_names))
        )
    )

    likes_results = likes_query.run(as_dict=True)

    # Process results more efficiently
    likes_data = {}
    for like in likes_results:
        proposal_name = like.reference_name
        if proposal_name not in likes_data:
            likes_data[proposal_name] = {"count": 0, "is_liked_by_user": False}

        likes_data[proposal_name]["count"] += 1
        if like.comment_email == current_user:
            likes_data[proposal_name]["is_liked_by_user"] = True

    return likes_data


def _get_bulk_speakers_data(proposal_names: list) -> dict:
    """
    Bulk fetch speakers for all proposals.

    Returns:
        dict: {proposal_name: [speaker_data]}
    """
    if not proposal_names:
        return {}

    # Use frappe.qb for better performance
    Speaker = qb.DocType(SPEAKER)

    speakers_query = (
        qb.from_(Speaker)
        .select(
            Speaker.parent,
            Speaker.photo,
            Speaker.full_name,
            Speaker.designation,
            Speaker.organization,
            Speaker.linked_user,
            Speaker.social_link,
            Speaker.bio,
        )
        .where(Speaker.parent.isin(proposal_names))
    )

    speakers_results = speakers_query.run(as_dict=True)

    # Group speakers by proposal more efficiently
    speakers_data = {}
    for speaker in speakers_results:
        proposal_name = speaker.parent
        if proposal_name not in speakers_data:
            speakers_data[proposal_name] = []
        speakers_data[proposal_name].append(speaker)

    return speakers_data


def _get_bulk_custom_answers_data(proposal_names: list) -> dict:
    """
    Bulk fetch custom answers for all proposals.

    Returns:
        dict: {proposal_name: {custom_question_1: response, ...}}
    """
    if not proposal_names:
        return {}

    # Use frappe.qb for better performance
    CustomAnswer = qb.DocType("FOSS Custom Answer")

    answers_query = (
        qb.from_(CustomAnswer)
        .select(CustomAnswer.parent, CustomAnswer.idx, CustomAnswer.response)
        .where(CustomAnswer.parent.isin(proposal_names))
    )

    answers_results = answers_query.run(as_dict=True)

    # Group answers by proposal more efficiently
    custom_answers_data = {}
    for answer in answers_results:
        proposal_name = answer.parent
        if proposal_name not in custom_answers_data:
            custom_answers_data[proposal_name] = {}

        custom_answers_data[proposal_name][f"custom_question_{answer.idx}"] = answer.response

    return custom_answers_data


@frappe.whitelist(allow_guest=True)
def get_public_proposal_filters(
    event: str,
):
    filter_fields = [
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "options": "Approved\nRejected\nReview Pending\nScreening",
            "label": "Review Status",
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
        EVENT_CFP,
        {"event": event},
        ["name", "has_public_custom_responses"],
        as_dict=True,
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
