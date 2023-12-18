import json

import frappe
from frappe.utils import format_datetime, format_time


def get_month(date_string, format_string):
    return date_string.strftime(format_string)


def formatted_datetime_with_tz(datetime_string):
    datetime_string = format_datetime(
        datetime_string, "EEE, d MMM, h:mm a"
    )
    return datetime_string


def format_time_with_zone(time, format_string="%-I:%m %p %Z"):
    return format_time(time, format_string)


def format_date_time(time, format="h:mm a"):
    return format_datetime(time, format)


def get_foss_profile(email):
    if email == "admin@example.com":
        return frappe.get_doc("User", {"email": email})

    try:
        profile = frappe.get_doc(
            "FOSS User Profile", {"email": email}
        )
    except:
        return frappe.get_doc("User", email)

    return profile


@frappe.whitelist()
def update_rsvp_count(rsvp):
    count = frappe.db.count(
        "FOSS Event RSVP Submission", {"linked_rsvp": rsvp}
    )
    frappe.db.set_value("FOSS Event RSVP", rsvp, "rsvp_count", count)


def is_session_user_team_member(chapter):
    members = frappe.get_doc("FOSS Chapter", chapter).chapter_members

    user = get_foss_profile(frappe.session.user)

    for member in members:
        return member.chapter_member == user.username


def get_event_navbar_items(
    chapter, show_speakers, show_rsvp, show_cfp, event_schedule
):
    navbar_items = {
        "Event Description": "event-description",
    }
    is_team_member = is_session_user_team_member(chapter)

    if show_speakers or is_team_member:
        navbar_items["Speakers"] = "speakers"

    if show_rsvp or is_team_member:
        navbar_items["RSVP"] = "rsvp"

    if show_cfp or is_team_member:
        navbar_items["CFP"] = "cfp"

    if event_schedule or is_team_member:
        navbar_items["Schedule"] = "schedule"

    return navbar_items


def hide_email(email):
    username, domain = email.split("@")
    username_length = len(username)

    # Calculate the number of characters to hide (5 characters or 50% of the username length, whichever is smaller)
    num_to_hide = min(5, username_length // 2)

    hidden_username = username[:-num_to_hide] + "*" * num_to_hide

    partially_hidden_email = hidden_username + "@" + domain
    return partially_hidden_email


# Filter
def get_avatar(
    user,
    size="sm",
    corners="rounded",
    grayscale=False,
    stroke="stroke",
):
    person = frappe.db.get_value(
        "FOSS User Profile",
        {"email": user},
        ["profile_photo", "full_name"],
        as_dict=1,
    )

    if person is None:
        return f'<div class="foss-avatar foss-avatar-{size} corners-{corners} {stroke}">{get_initials(f"{user}")}</div>'

    if person.profile_photo:
        return f'<img class="{grayscale} profile-image-{size} corners-{corners} {stroke}" src="{person.profile_photo}" alt="{person.full_name}">'.format(
            grayscale="grayscale-image" if grayscale else ""
        )

    return f'<div class="foss-avatar foss-avatar-{size} corners-{corners}">{get_initials(person.full_name)}</div>'


def get_initials(name):
    words = name.split(" ")
    initials = ""
    for word in words:
        initials += word[0].upper()

    return initials


# Filter
def make_badge(text="Default", size="sm"):
    # stored in the form of (background-color, text-color)
    colors = {
        "Approved": ("#30A66D", "#FFFFFF"),
        "Open": ("#DB7706", "#FFFFFF"),
        "Review Pending": ("#DB7706", "#FFFFFF"),
        "Rejected": ("#E74C3C", "#FFFFFF"),
        "Cancelled": ("#E74C3C", "#FFFFFF"),
        "Default": ("#171717", "#FFFFFF"),
    }
    bg_color, text_color = colors.get(text, colors["Default"])

    return f'<span class="badge badge-{size}" style="background-color: {bg_color}; color: {text_color};">{text}</span>'


def get_doc_likes(doctype, name):
    likes = frappe.db.get_value(doctype, name, "_liked_by")
    if likes is None:
        return []
    else:
        try:
            # Parse the string into a list
            likes = json.loads(likes)
        except json.JSONDecodeError as e:
            frappe.throw("Error parsing likes: " + str(e))

    return likes


def get_cfp_navbar(
    event, submitted_by, anonymise_proposals, cfp_status
):
    navbar_items = {
        "Proposal Details": "proposal-details",
        "Form Responses": "form-responses",
    }

    if not anonymise_proposals or (
        cfp_status not in ["Review Pending"]
        or check_if_reviewer(event)
    ):
        navbar_items["About Speaker"] = "about-speaker"

    chapter = frappe.db.get_value(
        "FOSS Event CFP", {"event": event}, "chapter"
    )

    if (
        check_if_reviewer(event)
        or is_session_user_team_member(chapter)
        or frappe.session.user == submitted_by
    ):
        navbar_items["Review Proposals"] = "review-proposals"

    return navbar_items


# checks if the user is a CFP reviewer for the event
def check_if_reviewer(event):
    reviewers = frappe.get_doc(
        "FOSS Event CFP", {"event": event}
    ).cfp_reviewers
    user = get_foss_profile(frappe.session.user)

    for reviewer in reviewers:
        return reviewer.reviewer == user.username


def get_cfp_review_statistics(event, submission):
    reviewers = frappe.get_doc(
        "FOSS Event CFP", {"event": event}
    ).cfp_reviewers
    reviews = frappe.get_doc(
        "FOSS Event CFP Submission", submission
    ).reviews

    score = {
        "Yes": 0,
        "No": 0,
        "Maybe": 0,
    }

    for review in reviews:
        score[review.to_approve] += 1

    not_reviewed = len(reviewers) - (
        score["Yes"] + score["No"] + score["Maybe"]
    )

    # percentage of approvability
    approvability = (score["Yes"] / len(reviewers)) * 100

    return {
        "score": score,
        "Not Reviewed": not_reviewed,
        "approvability": approvability,
    }


def get_reviewers(event):
    reviewers = frappe.get_doc(
        "FOSS Event CFP", {"event": event}
    ).cfp_reviewers

    reviewers_dict = {
        "Names": [],
        "Emails": [],
    }

    for reviewer in reviewers:
        reviewers_dict["Names"].append(reviewer.reviewer)
        reviewers_dict["Emails"].append(reviewer.email)

    return reviewers_dict


def user_already_reviewed(cfp_submission):
    reviews = frappe.get_doc(
        "FOSS Event CFP Submission", cfp_submission
    ).reviews

    for review in reviews:
        if review.email == frappe.session.user:
            return True

    return False


@frappe.whitelist()
def post_review(submission, reviewer, to_approve, remarks):
    submission_doc = frappe.get_doc(
        "FOSS Event CFP Submission", submission
    )
    submission_doc.append(
        "reviews",
        {
            "reviewer": reviewer,
            "email": frappe.session.user,
            "to_approve": to_approve,
            "remarks": remarks,
        },
    )
    submission_doc.save(ignore_permissions=True)


@frappe.whitelist()
def create_submission(fields):
    fields = json.loads(fields)
    doc = frappe.get_doc(fields)
    doc.insert(ignore_permissions=True)


@frappe.whitelist()
def update_submission(doctype, submission, fields, custom):
    fields = json.loads(fields)
    custom = json.loads(custom)
    frappe.db.set_value(doctype, submission, fields)

    doc = frappe.get_doc(doctype, submission).as_dict()
    for field in doc.custom_answers:
        frappe.db.set_value(
            "FOSS Custom Answers",
            field.name,
            "response",
            custom[field.idx - 1]["response"],
        )


def filter_field_values(key):
    ACCEPTED_FIELD_TYPES = [
        "fieldname",
        "label",
        "fieldtype",
        "options",
        "description",
        "reqd",
        "read_only",
        "description",
    ]

    if key in ACCEPTED_FIELD_TYPES:
        return True

    return False


def get_form_fields(doctype):
    meta = frappe.get_meta(doctype).as_dict()
    fields = {}
    current_section = None
    submission = {}
    submission["doc"] = (
        "RSVP" if frappe.form_dict.get("rsvp") else "CFP"
    )
    submission["value"] = (
        frappe.form_dict.get("rsvp")
        if frappe.form_dict.get("rsvp")
        else frappe.form_dict.get("cfp")
    )
    submission["custom_len"] = len(
        frappe.get_doc(
            f'FOSS Event {submission["doc"]} Submission',
            submission["value"],
        ).custom_answers
    )

    for field in meta["fields"]:
        if (
            field["fieldtype"] == "Section Break"
            or field["fieldtype"] == "Tab Break"
        ):
            current_section = field["label"]
            if (
                current_section == "Meta Info"
                or current_section == "Reviews"
                or (
                    current_section == "Custom Answers"
                    and submission["custom_len"] == 0
                )
            ):
                continue
            fields[current_section] = []

        if current_section not in [
            "Meta Info",
            "Reviews",
            "Custom Answers" if submission["custom_len"] == 0 else "",
        ]:
            fields[current_section].append(
                {
                    k: v
                    for k, v in field.items()
                    if filter_field_values(k)
                }
            )

    return fields
