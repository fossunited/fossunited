import frappe

from fossunited.api.dashboard import get_profile_data
from fossunited.doctype_ids import EVENT_CFP


def get_event_cfp_submissions(event: str) -> list:
    """
    Get all the submissions for the given event

    Args:
        event (str): The id of the event

    Returns:
        list: List of submissions for the given event
    """
    fields = [
        "name",
        "linked_cfp",
        "route",
        "is_published",
        "title",
        "status",
        "event",
        "event_name",
        "is_first_talk",
        "session_type",
        "talk_title",
        "talk_reference",
        "talk_description",
        "custom_answers",
        "positive_reviews",
        "negative_reviews",
        "unsure_reviews",
        "approvability",
    ]

    is_cfp_anonymous = frappe.db.get_value(EVENT_CFP, {"event": event}, "anonymise_proposals")

    if not is_cfp_anonymous:
        fields += [
            "full_name",
            "picture_url",
            "designation",
            "organization",
            "bio",
        ]

    submissions = frappe.db.get_list(
        "FOSS Event CFP Submission",
        filters={"event": event, "status": "Review Pending"},
        fields=fields,
        order_by="creation desc",
    )

    return submissions


@frappe.whitelist()
def get_cfp_submissions_by_reviewer_status(
    event: str,
    status_filter: list = ["Reviewed", "Not Reviewed"],
    to_approve_filter: list = ["Yes", "No", "Maybe"],
):
    if not has_reviewer_role():
        frappe.throw("Unauthorized Access")

    submissions_list = []

    submissions = get_event_cfp_submissions(event)

    reviewer = frappe.db.get_value("FOSS User Profile", {"user": frappe.session.user}, "name")

    for submission in submissions:
        if not frappe.db.exists(
            "FOSS Event CFP Review",
            {
                "parent": submission.name,
                "reviewer_profile": reviewer,
                "parenttype": "FOSS Event CFP Submission",
            },
        ):
            if "Not Reviewed" in status_filter:
                submission["review_status"] = "Not Reviewed"
                submission["status"] = "-"
                submission["remarks"] = "-"
                submissions_list.append(submission)
            continue

        if "Reviewed" in status_filter:
            review = frappe.get_doc(
                "FOSS Event CFP Review",
                {
                    "parenttype": "FOSS Event CFP Submission",
                    "parent": submission.name,
                    "reviewer_profile": reviewer,
                },
            )
            if review.to_approve in to_approve_filter:
                submission["review_status"] = "Reviewed"
                submission["reviewer_status"] = review.to_approve
                submission["reviewer_remarks"] = review.remarks
                submissions_list.append(submission)

    return submissions_list


def has_reviewer_role():
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "CFP Reviewer", "parent": frappe.session.user},
        )
    )


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
        "FOSS Chapter Event",
        filters={
            "status": ["in", ["Approved", "Live"]],
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
        page_length=20,
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
            "FOSS Chapter",
            event.chapter,
            ["name", "chapter_name", "chapter_type"],
            as_dict=1,
        )
        submission_count = frappe.db.count("FOSS Event CFP Submission", {"linked_cfp": cfp.name})
        cfps_to_review.append(
            {
                "event": event.name,
                "event_name": event.event_name,
                "start_date": event.event_start_date,
                "end_date": event.event_end_date,
                "cfp": cfp.name,
                "submission_count": submission_count,
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

    reviewer_profile = frappe.db.get_value("FOSS User Profile", {"email": reviewer}, "name")

    return bool(
        frappe.db.exists(
            "FOSS Event CFP Review",
            {
                "parent": submission_id,
                "reviewer_profile": reviewer_profile,
                "parenttype": "FOSS Event CFP Submission",
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

    reviewer_profile = frappe.db.get_value("FOSS User Profile", {"email": reviewer}, "name")

    review = frappe.db.get_value(
        "FOSS Event CFP Review",
        {
            "parent": submission_id,
            "reviewer_profile": reviewer_profile,
            "parenttype": "FOSS Event CFP Submission",
        },
        ["to_approve", "remarks", "name", "reviewer_profile"],
        as_dict=1,
    )

    return review


@frappe.whitelist()
def submit_review(
    submission_id: str,
    remarks: str,
    to_approve: str,
    reviewer: str = frappe.session.user,
) -> None:
    """
    Create a review for the submission

    Args:
        submission_id (str): The id of the submission
        remarks (str): The reviewer's remarks
        to_approve (str): The reviewer's decision
        reviewer (str): The reviewer's email
    """
    if not has_reviewer_role():
        frappe.throw("Unauthorized Access")

    if has_cfp_review(submission_id, reviewer):
        frappe.throw("Review already exists")

    reviewer_profile = frappe.db.get_value("FOSS User Profile", {"email": reviewer}, "name")

    submission_doc = frappe.get_doc("FOSS Event CFP Submission", submission_id)

    submission_doc.append(
        "reviews",
        {
            "reviewer_profile": reviewer_profile,
            "to_approve": to_approve,
            "remarks": remarks,
        },
    )
    submission_doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_submitter_profile(submission_id: str) -> dict:
    """
    Returns the profile of the submitter of the CFP submission.
    """
    submitter_email = frappe.db.get_value("FOSS Event CFP Submission", submission_id, ["submitted_by"])

    if not submitter_email:
        frappe.throw("Submitter email not found")

    user = get_profile_data(email=submitter_email)

    return user
