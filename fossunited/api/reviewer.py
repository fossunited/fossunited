import frappe

from fossunited.api.dashboard import get_profile_data
from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    PROPOSAL_REVIEW,
    USER_PROFILE,
)


@frappe.whitelist()
def get_cfp_submissions(event: str) -> list:
    """
    Get all the submissions for the given event

    Args:
        event (str): The id of the event

    Returns:
        list: List of submissions for the given event
    """

    if not has_reviewer_role():
        frappe.throw(
            "You do not have permission to access this resource",
            frappe.PermissionError,
            "Permission Error!",
        )

    cfp = frappe.db.get_value(EVENT_CFP, {"event": event}, "name")

    fields = [
        "name",
        "talk_title",
        "status",
        "session_categories",
        "session_type",
        "is_first_talk",
        "intended_audience",
        "creation",
    ]

    submissions = frappe.db.get_list(
        PROPOSAL,
        {"linked_cfp": cfp},
        fields,
        page_length=9999,
    )

    submission_names = [submission.name for submission in submissions]

    # Fetch review statuses in bulk
    reviews = frappe.db.get_all(
        PROPOSAL_REVIEW,
        {
            "parent": ("in", submission_names),
            "parenttype": PROPOSAL,
            "reviewer_profile": frappe.db.get_value(
                USER_PROFILE, {"email": frappe.session.user}, "name"
            ),
        },
        ["parent"],
    )
    reviewed_submissions = {review.parent for review in reviews}

    # Fetch like counts in bulk
    likes = frappe.db.get_all(
        "Comment",
        {
            "comment_type": "Like",
            "reference_doctype": PROPOSAL,
            "reference_name": ("in", submission_names),
        },
        ["reference_name"],
    )
    like_counts = {}
    for like in likes:
        like_counts[like.reference_name] = like_counts.get(like.reference_name, 0) + 1

    for submission in submissions:
        submission["_is_reviewed"] = submission.name in reviewed_submissions
        submission["_is_seen"] = submission["_is_reviewed"]
        submission["_likes_count"] = like_counts.get(submission.name, 0)

    return submissions


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

    submissions = frappe.db.get_all(PROPOSAL, {"linked_cfp": cfp}, ["name"])
    reviewed_count = 0

    for item in submissions:
        if has_cfp_review(item.name):
            reviewed_count += 1

    not_reviewed_count = len(submissions) - reviewed_count

    return (reviewed_count, not_reviewed_count)


@frappe.whitelist()
def get_events_by_open_cfp() -> list:
    """
    Get all the upcoming events with open CFP

    Returns:
        list: List of events with open CFP
    """
    if not has_reviewer_role():
        frappe.throw("Unauthorized Access")

    cfps_to_review = []

    events = frappe.db.get_list(
        EVENT,
        filters={
            "status": "Live",
            "is_published": 1,
            "event_start_date": [">=", frappe.utils.nowdate()],
        },
        fields=[
            "name",
            "event_name",
            "event_start_date",
            "event_end_date",
            "chapter",
        ],
        page_length=99,
        order_by="event_start_date",
    )

    for event in events:
        cfp_exists = frappe.db.exists(EVENT_CFP, {"event": event.name})
        if not cfp_exists:
            continue

        cfp = frappe.db.get_value(
            EVENT_CFP,
            {"event": event.name},
            ["name", "chapter"],
            as_dict=1,
        )
        chapter = frappe.db.get_value(
            CHAPTER,
            event.chapter,
            ["name", "chapter_name", "chapter_type"],
            as_dict=1,
        )
        submission_count = frappe.db.count(PROPOSAL, {"linked_cfp": cfp.name})
        reviewed_count, not_reviewed_count = get_reviewed_count(event=event.name)
        cfps_to_review.append(
            {
                "event": event.name,
                "event_name": event.event_name,
                "start_date": event.event_start_date,
                "end_date": event.event_end_date,
                "cfp": cfp.name,
                "submission_count": submission_count,
                "reviewed_count": reviewed_count,
                "not_reviewed_count": not_reviewed_count,
                "chapter": chapter.name,
                "chapter_name": chapter.chapter_name,
                "chapter_type": chapter.chapter_type,
            }
        )

    return cfps_to_review


@frappe.whitelist()
def has_cfp_review(submission_id: str, reviewer: str = frappe.session.user) -> bool:
    """
    Check if the reviewer has reviewed the submission

    Args:
        submission_id (str): The id of the submission
        reviewer (str): The reviewer's email

    Returns:
        bool: True if the reviewer has reviewed the submission, False otherwise
    """

    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": reviewer}, "name")

    return bool(
        frappe.db.exists(
            PROPOSAL_REVIEW,
            {
                "parent": submission_id,
                "reviewer_profile": reviewer_profile,
                "parenttype": PROPOSAL,
            },
        )
    )


@frappe.whitelist()
def get_review(submission_id: str, reviewer: str = frappe.session.user) -> dict:
    """
    Get the review of the submission by the reviewer

    Args:
        submission_id (str): The id of the submission
        reviewer (str): The reviewer's email

    Returns:
        dict: The review of the submission by the reviewer
    """
    if not has_cfp_review(submission_id, reviewer):
        frappe.throw("No review found")

    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": reviewer}, "name")

    review = frappe.db.get_value(
        PROPOSAL_REVIEW,
        {
            "parent": submission_id,
            "reviewer_profile": reviewer_profile,
            "parenttype": PROPOSAL,
        },
        ["to_approve", "remarks", "name", "reviewer_profile"],
        as_dict=1,
    )

    return review


@frappe.whitelist()
def get_submitter_profile(submission_id: str) -> dict:
    """
    Returns the profile of the submitter of the CFP submission.
    """
    submitter_email = frappe.db.get_value(PROPOSAL, submission_id, ["submitted_by"])

    if not submitter_email:
        frappe.throw("Submitter email not found")

    user = get_profile_data(email=submitter_email)

    return user
