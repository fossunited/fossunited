from collections import defaultdict

import frappe

from fossunited.api.proposal import _get_bulk_custom_answers_data
from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    PROPOSAL_REVIEW,
    SPEAKER,
    USER_PROFILE,
)
from fossunited.id.roles import CHAPTER_MEMBER, REVIEWER


# nosemgrep: guest-whitelisted-method
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


# nosemgrep: guest-whitelisted-method
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


CFP_SUBMISSION_FIELDS = [
    "name",
    "talk_title",
    "status",
    "session_categories",
    "session_type",
    "is_first_talk",
    "intended_audience",
    "talk_license",
    "creation",
]


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

    cfp_doc = frappe.get_doc(EVENT_CFP, {"event": event})
    cfp = cfp_doc.name
    
    active_phase = next(
        (p for p in cfp_doc.get("cfp_review_phases", []) if p.is_active), None
    )

    filters = {"linked_cfp": cfp}

    if active_phase and active_phase.proposal_visibility == "Only Assigned":
        all_cfp_proposals = frappe.db.get_list(PROPOSAL, {"linked_cfp": cfp}, pluck="name")
        assigned_proposals = frappe.db.get_all(
            "ToDo",
            filters={
                "reference_type": PROPOSAL,
                "reference_name": ("in", all_cfp_proposals),
                "allocated_to": frappe.session.user,
                "status": "Open",
            },
            pluck="reference_name",
        )
        if not assigned_proposals:
            return []
        filters["name"] = ("in", assigned_proposals)

    submissions = frappe.db.get_list(
        PROPOSAL,
        filters,
        CFP_SUBMISSION_FIELDS,
        page_length=9999,
        order_by="creation desc",
    )

    if not submissions:
        return submissions

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

    # Reuse bulk query functions from proposal.py
    custom_answers_data = _get_bulk_custom_answers_data(submission_names)

    # Bulk fetch review percentages
    review_percentages_data = _get_bulk_review_percentages_data(submission_names)

    # Bulk fetch speakers for all submissions (outside selected range)
    speakers_raw = frappe.db.get_all(
        SPEAKER,
        {"parent": ("in", submission_names)},
        [
            "parent",
            "photo",
            "full_name",
            "designation",
            "organization",
            "linked_user",
            "social_link",
            "bio",
        ],
    )
    speakers_by_submission = defaultdict(list)

    for s in speakers_raw:
        speakers_by_submission[s["parent"]].append(s)

    # Fetch assignment status in bulk via Frappe's built-in ToDo
    assigned_todos = frappe.db.get_all(
        "ToDo",
        {
            "reference_type": PROPOSAL,
            "reference_name": ("in", submission_names),
            "allocated_to": frappe.session.user,
            "status": "Open",
        },
        pluck="reference_name",
    )
    assigned_submissions = set(assigned_todos)

    for submission in submissions:
        is_reviewed = submission.name in reviewed_submissions
        submission.update(
            {
                "_is_reviewed": "Yes" if is_reviewed else "No",
                "_is_seen": is_reviewed,
                "_is_assigned": "Yes" if submission.name in assigned_submissions else "No",
            }
        )
        submission["_likes_count"] = like_counts.get(submission.name, 0)
        submission.update(custom_answers_data.get(submission.name, {}))
        submission.update(review_percentages_data.get(submission.name, {}))

        speakers = speakers_by_submission.get(submission.name, [])
        submission["speakers"] = speakers
        submission["speaker_name"] = ", ".join(
            name for name in ((s.get("full_name") or "").strip() for s in speakers) if name
        )

    return submissions


def _get_bulk_review_percentages_data(submission_names: list) -> dict:
    """
    Bulk fetch review percentages for all submissions.

    Returns:
        dict: {submission_name: {approved_percent: int, rejected_percent: int, ...}}
    """
    if not submission_names:
        return {}

    # Use frappe.qb for better performance
    from frappe import qb

    Review = qb.DocType(PROPOSAL_REVIEW)

    reviews_query = (
        qb.from_(Review)
        .select(Review.parent, Review.to_approve)
        .where((Review.parent.isin(submission_names)) & (Review.parenttype == PROPOSAL))
    )

    reviews_results = reviews_query.run(as_dict=True)

    # Group reviews by submission and calculate percentages
    review_percentages_data = {}
    submission_reviews = {}

    for review in reviews_results:
        submission_name = review.parent
        if submission_name not in submission_reviews:
            submission_reviews[submission_name] = []
        submission_reviews[submission_name].append(review.to_approve)

    for submission_name, reviews in submission_reviews.items():
        positive_reviews = reviews.count("Yes")
        negative_reviews = reviews.count("No")
        unsure_reviews = reviews.count("Maybe")

        total_reviews = len(reviews)
        if total_reviews == 0:
            review_percentages_data[submission_name] = {
                "approved_percent": 0,
                "rejected_percent": 0,
                "unsure_percent": 0,
            }
        else:
            review_percentages_data[submission_name] = {
                "approved_percent": int((positive_reviews / total_reviews) * 100),
                "rejected_percent": int((negative_reviews / total_reviews) * 100),
                "unsure_percent": int((unsure_reviews / total_reviews) * 100),
            }

    return review_percentages_data


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
        }

    return {
        "approved_percent": int((positive_reviews / total_reviews) * 100),
        "rejected_percent": int((negative_reviews / total_reviews) * 100),
        "unsure_percent": int((unsure_reviews / total_reviews) * 100),
    }


def get_speakers(submission: str) -> list:
    return frappe.db.get_all(
        SPEAKER,
        {"parent": submission},
        [
            "photo",
            "full_name",
            "designation",
            "organization",
            "linked_user",
            "social_link",
            "bio",
        ],
    )


def get_custom_answers(submission: str) -> dict:
    custom_answers = frappe.db.get_all("FOSS Custom Answer", {"parent": submission}, ["*"])

    custom_answers_dict = {}

    for answer in custom_answers:
        custom_answers_dict[f"custom_question_{answer.idx}"] = answer.response

    return custom_answers_dict


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_global_cfp_guidelines() -> dict:
    """
    Get the global CFP guidelines.
    """
    return {"guidelines": frappe.db.get_single_value("Global CFP Settings", "guidelines")}


@frappe.whitelist()
def get_proposal_filter_fields(event_id: str) -> list:
    # excluding non-filterable ones (name, creation, talk_title handled by search)
    FILTERABLE_FIELDNAMES = {
        f for f in CFP_SUBMISSION_FIELDS if f not in ("name", "talk_title")
    } | {
        "is_withdrawn",
        "talk_license",
        "speakers",
        "custom_answers",
        "is_first_talk",
        "organization",
        "session_categories",
        "submitted_by",
    }

    all_meta_fields = frappe.get_meta(PROPOSAL).fields
    filtered_fields = [
        field for field in all_meta_fields if field.fieldname in FILTERABLE_FIELDNAMES
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
                "label": "Reviewed (By Me)",
                "reqd": 0,
            },
        ]

    return filtered_fields
