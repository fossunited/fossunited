import frappe

from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    PROPOSAL_REVIEW,
    SPEAKER,
    USER_PROFILE,
)
from fossunited.id.roles import CHAPTER_MEMBER, REVIEWER


@frappe.whitelist(allow_guest=True)
def get_cfp_from_route(route: str) -> dict:
    event = frappe.db.get_value(
        EVENT,
        {"route": f"c/{route}"},
        [
            "route",
            "name",
            "event_name",
            "event_logo",
            "event_location",
            "event_start_date",
            "event_end_date",
            "event_description",
        ],
        as_dict=True,
    )

    cfp = frappe.get_doc(EVENT_CFP, {"event": event.name}).as_dict()
    cfp.event = event

    return cfp


@frappe.whitelist(allow_guest=True)
def get_cfp_submissions_insight(event_id: str) -> list:
    cfp_form_id = frappe.db.get_value(EVENT_CFP, {"event": event_id}, "name")

    today_date = frappe.utils.nowdate()
    filters = {"linked_cfp": cfp_form_id}
    today_filters = {**filters, "creation": ["like", f"{today_date}%"]}

    insight_values = [
        {
            "label": "Total",
            "count": frappe.db.count(PROPOSAL, filters),
            "today": frappe.db.count(PROPOSAL, today_filters),
        }
    ]

    PROPOSAL_STATUSES = ["Approved", "Rejected", "Review Pending", "Screening"]
    insight_values.extend(
        {
            "label": status,
            "count": frappe.db.count(PROPOSAL, {**filters, "status": status}),
        }
        for status in PROPOSAL_STATUSES
    )

    return insight_values


@frappe.whitelist()
def get_cfp_submissions(event: str) -> list:
    """
    Get all the submissions for the given event

    Args:
        event (str): The id of the event

    Returns:
        list: List of submissions for the given event
    """
    frappe.only_for([REVIEWER, CHAPTER_MEMBER])

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
        order_by="creation desc",
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
        is_reviewed = submission.name in reviewed_submissions
        submission.update(
            {
                "_is_reviewed": "Yes" if is_reviewed else "No",
                "_is_not_reviewed": "No" if is_reviewed else "Yes",
                "_is_seen": is_reviewed,
            }
        )
        submission["_likes_count"] = like_counts.get(submission.name, 0)
        submission.update(get_custom_answers(submission.name))
        submission.update(get_review_percentages(submission.name))

    return submissions


def get_review_percentages(submission: str) -> dict:
    reviews = frappe.db.get_all(
        PROPOSAL_REVIEW,
        {"parent": submission, "parenttype": PROPOSAL},
        pluck="to_approve",
    )
    positive_reviews = reviews.count("Yes")
    negative_reviews = reviews.count("No")
    unsure_reviews = reviews.count("Maybe")

    total_reviews = len(reviews)
    if total_reviews == 0:
        return {
            "approved_percent": 0,
            "rejected_percent": 0,
            "unsure_percent": 0,
            "approvability": 0,
        }

    approved_percent = int((positive_reviews / total_reviews) * 100)
    rejected_percent = int((negative_reviews / total_reviews) * 100)
    unsure_percent = int((unsure_reviews / total_reviews) * 100)

    approvability = int(
        (positive_reviews / (positive_reviews + negative_reviews)) * 100
        if positive_reviews + negative_reviews > 0
        else 0
    )

    return {
        "approved_percent": approved_percent,
        "rejected_percent": rejected_percent,
        "unsure_percent": unsure_percent,
        "approvability": approvability,
    }


def get_speakers(submission: str) -> list:
    return frappe.db.get_all(
        SPEAKER,
        {"parent": submission},
        ["photo", "full_name", "designation", "organization", "linked_user", "social_link", "bio"],
    )


def get_custom_answers(submission: str) -> dict:
    custom_answers = frappe.db.get_all("FOSS Custom Answer", {"parent": submission}, ["*"])

    custom_answers_dict = {}

    for answer in custom_answers:
        custom_answers_dict[f"custom_question_{answer.idx}"] = answer.response

    return custom_answers_dict


@frappe.whitelist(allow_guest=True)
def get_global_cfp_guidelines() -> dict:
    """
    Get the global CFP guidelines.
    """
    return frappe.db.get_value("Global CFP Settings", None, "guidelines", as_dict=True)


@frappe.whitelist()
def get_proposal_filter_fields(event_id: str) -> list:
    fields = frappe.get_meta(PROPOSAL).fields

    fieldtypes_to_remove = ["Section Break", "Tab Break", "Column Break"]
    fields_to_remove = [
        "talk_title",
        "is_published",
        "route",
        "linked_cfp",
        "chapter",
        "event",
        "submitted_by",
        "event_name",
        "attendance_confirmed",
        "first_name",
        "last_name",
        "talk_reference",
        "full_name",
        "email",
        "picture_url",
        "designation",
        "organization",
        "bio",
        "positive_reviews",
        "negative_reviews",
        "unsure_reviews",
        "approvability",
    ]

    fieldnames_to_remove = set(fields_to_remove)
    filtered_fields = [
        field
        for field in fields
        if field.fieldtype not in fieldtypes_to_remove
        and field.fieldname not in fieldnames_to_remove
    ]

    cfp = frappe.get_doc(EVENT_CFP, {"event": event_id})

    for question in cfp.cfp_custom_questions:
        custom_field = {
            "fieldname": "custom_question_" + str(question.idx),
            "fieldtype": question.type,
            "label": question.question + " (Custom question)",
            "options": question.options,
            "reqd": question.is_mandatory or 0,
            "description": question.description,
        }

        filtered_fields.append(custom_field)

    if REVIEWER in frappe.get_roles(frappe.session.user):
        # appending _is_reviewed field
        filtered_fields[:0] = [
            {
                "fieldname": "_is_reviewed",
                "fieldtype": "Check",
                "label": "Only show reviewed (By Me)",
                "reqd": 0,
            },
            {
                "fieldname": "_is_not_reviewed",
                "fieldtype": "Check",
                "label": "Only show not reviewed (By Me)",
                "reqd": 0,
            },
        ]

    return filtered_fields
