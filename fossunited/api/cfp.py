import json
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

_EMPTY_REVIEW_STATS = {
    "approved_percent": 0,
    "rejected_percent": 0,
    "unsure_percent": 0,
    "_review_count": 0,
}


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
    Returns enriched submissions for an event.

    Reviewers get: _is_reviewed, _is_assigned, review percentages, speakers, likes.
    Organizers get everything above plus _assigned_users with review verdicts per assignee.
    """
    frappe.only_for([REVIEWER, CHAPTER_MEMBER])

    cfp = frappe.db.get_value(EVENT_CFP, {"event": event}, "name")
    submissions = frappe.db.get_list(
        PROPOSAL,
        {"linked_cfp": cfp},
        CFP_SUBMISSION_FIELDS,
        page_length=9999,
        order_by="creation desc",
    )

    if not submissions:
        return submissions

    names = [s.name for s in submissions]
    is_organizer = CHAPTER_MEMBER in frappe.get_roles(frappe.session.user)

    # Shared data (fetched for both reviewer and organizer)
    like_counts = _get_bulk_like_counts(names)
    custom_answers = _get_bulk_custom_answers_data(names)
    review_percentages = _get_bulk_review_percentages(names)
    speakers_by = _get_bulk_speakers(names)
    reviewed_by_me = _get_reviewed_by_current_user(names)

    # Role-specific assignment enrichment
    # Organizer: full _assigned_users list with avatars + per-user verdict (3 extra queries)
    # Reviewer: only _is_assigned for current user (1 cheap query)
    assignment_data = (
        _get_organizer_assignment_data(names)
        if is_organizer
        else _get_reviewer_assignment_data(names)
    )

    for s in submissions:
        s.update(
            {
                "_is_reviewed": "Yes" if s.name in reviewed_by_me else "No",
                "_is_seen": s.name in reviewed_by_me,
                "_likes_count": like_counts.get(s.name, 0),
            }
        )
        s.update(assignment_data.get(s.name, {}))
        s.update(custom_answers.get(s.name, {}))
        s.update(review_percentages.get(s.name, _EMPTY_REVIEW_STATS))
        speakers = speakers_by.get(s.name, [])
        s["speakers"] = speakers
        s["speaker_name"] = ", ".join(
            n for n in (sp.get("full_name", "").strip() for sp in speakers) if n
        )

    return submissions


# -- private helpers -----------------------------------------------------------
# Each helper takes submission_names and returns a shaped dict keyed by name.
# Keep these focused: one query concern per function.


def _get_reviewed_by_current_user(submission_names: list) -> set[str]:
    """Submission names the current user has already reviewed."""
    reviewer_profile = frappe.db.get_value(USER_PROFILE, {"email": frappe.session.user}, "name")
    if not reviewer_profile:
        return set()
    rows = frappe.db.get_all(
        PROPOSAL_REVIEW,
        {
            "parent": ("in", submission_names),
            "parenttype": PROPOSAL,
            "reviewer_profile": reviewer_profile,
        },
        ["parent"],
    )
    return {r.parent for r in rows}


def _get_bulk_like_counts(submission_names: list) -> dict[str, int]:
    """Returns {submission_name: like_count}."""
    likes = frappe.db.get_all(
        "Comment",
        {
            "comment_type": "Like",
            "reference_doctype": PROPOSAL,
            "reference_name": ("in", submission_names),
        },
        ["reference_name"],
    )
    counts: dict[str, int] = {}
    for like in likes:
        counts[like.reference_name] = counts.get(like.reference_name, 0) + 1
    return counts


def _get_bulk_review_percentages(submission_names: list) -> dict[str, dict]:
    """Returns {submission_name: {approved_percent, rejected_percent, unsure_percent, _review_count}}."""
    if not submission_names:
        return {}

    from frappe import qb

    Review = qb.DocType(PROPOSAL_REVIEW)
    rows = (
        qb.from_(Review)
        .select(Review.parent, Review.to_approve)
        .where((Review.parent.isin(submission_names)) & (Review.parenttype == PROPOSAL))
        .run(as_dict=True)
    )

    grouped: dict[str, list] = {}
    for r in rows:
        grouped.setdefault(r.parent, []).append(r.to_approve)

    result = {}
    for name, votes in grouped.items():
        total = len(votes)
        result[name] = {
            "approved_percent": int(votes.count("Yes") / total * 100),
            "rejected_percent": int(votes.count("No") / total * 100),
            "unsure_percent": int(votes.count("Maybe") / total * 100),
            "_review_count": total,
        }
    return result


def _get_bulk_speakers(submission_names: list) -> dict[str, list]:
    """Returns {submission_name: [speaker_dict, ...]}."""
    raw = frappe.db.get_all(
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
    by_sub: dict[str, list] = defaultdict(list)
    for s in raw:
        by_sub[s["parent"]].append(s)
    return by_sub


def _get_reviewer_assignment_data(submission_names: list) -> dict[str, dict]:
    """
    Reviewer context. Checks only the current user's ToDo assignment.
    Returns {submission_name: {_is_assigned, _assigned_users: []}}.
    """
    assigned = set(
        frappe.db.get_all(
            "ToDo",
            {
                "reference_type": PROPOSAL,
                "reference_name": ("in", submission_names),
                "allocated_to": frappe.session.user,
            },
            pluck="reference_name",
        )
    )
    return {
        name: {
            "_is_assigned": "Yes" if name in assigned else "No",
            "_assigned_users": [],
        }
        for name in submission_names
    }


def _get_organizer_assignment_data(submission_names: list) -> dict[str, dict]:
    """
    Organizer context. Fetches all assignees + their user profile data + review verdicts.
    Returns {submission_name: {_is_assigned, _assigned_users: [{user, full_name, user_image, _review_verdict}]}}.
    """
    todos = frappe.db.get_all(
        "ToDo",
        {"reference_type": PROPOSAL, "reference_name": ("in", submission_names)},
        ["reference_name", "allocated_to"],
    )
    todos_by_sub: dict[str, list] = defaultdict(list)
    for t in todos:
        todos_by_sub[t.reference_name].append(t.allocated_to)

    # Bulk fetch user profile data for avatars
    unique_users = {t.allocated_to for t in todos}
    user_data: dict[str, object] = {}
    if unique_users:
        user_data = {
            u.name: u
            for u in frappe.db.get_all(
                "User",
                {"name": ("in", list(unique_users))},
                ["name", "full_name", "user_image"],
            )
        }

    verdict_by_sub = _get_bulk_reviewed_by_user_verdict(submission_names)
    current_user = frappe.session.user

    result = {}
    for name in submission_names:
        assignees = todos_by_sub.get(name, [])
        verdicts = verdict_by_sub.get(name, {})
        result[name] = {
            "_is_assigned": "Yes" if current_user in assignees else "No",
            "_assigned_users": [
                {
                    "user": email,
                    "full_name": (user_data.get(email) or {}).get("full_name") or email,
                    "user_image": (user_data.get(email) or {}).get("user_image") or "",
                    "_review_verdict": verdicts.get(email),
                }
                for email in assignees
            ],
        }
    return result


def _get_bulk_reviewed_by_user_verdict(
    submission_names: list,
) -> dict[str, dict[str, str]]:
    """
    Maps {submission_name: {user_email: to_approve}} for organizer avatar verdict display.
    Requires a USER_PROFILE lookup to convert reviewer_profile links → user emails.
    """
    if not submission_names:
        return {}

    from frappe import qb

    Review = qb.DocType(PROPOSAL_REVIEW)
    rows = (
        qb.from_(Review)
        .select(Review.parent, Review.to_approve, Review.reviewer_profile)
        .where((Review.parent.isin(submission_names)) & (Review.parenttype == PROPOSAL))
        .run(as_dict=True)
    )

    unique_profiles = {r.reviewer_profile for r in rows if r.reviewer_profile}
    profile_to_user: dict[str, str] = {}
    if unique_profiles:
        profile_to_user = {
            p.name: p.user
            for p in frappe.db.get_all(
                USER_PROFILE, {"name": ("in", list(unique_profiles))}, ["name", "user"]
            )
        }

    result: dict[str, dict] = {}
    for r in rows:
        user = profile_to_user.get(r.reviewer_profile)
        if user:
            result.setdefault(r.parent, {})[user] = r.to_approve
    return result


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_global_cfp_guidelines() -> dict:
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


@frappe.whitelist()
def get_cfp_reviewers(event_id: str) -> list:
    frappe.only_for([CHAPTER_MEMBER])
    reviewer_users = frappe.db.get_all(
        "Has Role",
        {"role": REVIEWER, "parenttype": "User"},
        pluck="parent",
    )
    if not reviewer_users:
        return []
    return frappe.db.get_all(
        "User",
        {"name": ("in", reviewer_users), "enabled": 1},
        ["name as user", "full_name", "user_image"],
    )


@frappe.whitelist()
def get_submission_reviewer_assignments(submission_name: str) -> list:
    frappe.only_for([CHAPTER_MEMBER])
    return frappe.db.get_all(
        "ToDo",
        {"reference_type": PROPOSAL, "reference_name": submission_name},
        pluck="allocated_to",
    )


@frappe.whitelist()
def set_submission_reviewers(submission_name: str, reviewer_users: list) -> None:
    frappe.only_for([CHAPTER_MEMBER])
    if isinstance(reviewer_users, str):
        reviewer_users = json.loads(reviewer_users)

    existing = frappe.db.get_all(
        "ToDo",
        {"reference_type": PROPOSAL, "reference_name": submission_name},
        ["name", "allocated_to"],
    )
    existing_map = {t.allocated_to: t.name for t in existing}
    new_set = set(reviewer_users)
    existing_set = set(existing_map.keys())

    for user in existing_set - new_set:
        frappe.delete_doc("ToDo", existing_map[user], ignore_permissions=True)

    if new_set - existing_set:
        talk_title = (
            frappe.db.get_value(PROPOSAL, submission_name, "talk_title") or submission_name
        )

    for user in new_set - existing_set:
        frappe.get_doc(
            {
                "doctype": "ToDo",
                "reference_type": PROPOSAL,
                "reference_name": submission_name,
                "allocated_to": user,
                "assigned_by": frappe.session.user,
                "description": f"[RP]: {talk_title}",
            }
        ).insert(ignore_permissions=True)


@frappe.whitelist()
def get_my_latest_speaker_entry() -> dict:
    """Returns the most recent speaker entry for the current user (matched by linked_user or email)."""
    user = frappe.session.user
    profile_name = frappe.db.get_value(USER_PROFILE, {"user": user}, "name")
    or_filters = {"email": user}
    if profile_name:
        or_filters["linked_user"] = profile_name
    rows = frappe.db.get_all(
        SPEAKER,
        or_filters=or_filters,
        fields=["photo", "designation", "organization", "contact_info", "social_link"],
        order_by="creation desc",
        limit=1,
        ignore_permissions=True,
    )
    return rows[0] if rows else {}
