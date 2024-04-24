import itertools
import json

import frappe
from frappe.utils import format_datetime, format_time
from frappe.utils.data import now_datetime


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


# Jinja Filter
def get_profile_image(email):
    profile = get_foss_profile(email)
    return (
        profile.profile_photo
        or "/assets/fossunited/images/defaults/user_profile_image.png"
    )


def get_event_volunteers(event):
    volunteers = frappe.get_doc(
        "FOSS Chapter Event", event
    ).event_members
    return volunteers


@frappe.whitelist()
def update_rsvp_count(rsvp):
    count = frappe.db.count(
        "FOSS Event RSVP Submission", {"linked_rsvp": rsvp}
    )
    frappe.db.set_value("FOSS Event RSVP", rsvp, "rsvp_count", count)


# To Remove
def is_session_user_team_member(chapter):
    members = frappe.get_doc("FOSS Chapter", chapter).chapter_members

    user = get_foss_profile(frappe.session.user)

    for member in members:
        return member.chapter_member == user.username


# To Remove
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


def is_user_team_member(chapter, user):
    members = frappe.get_doc("FOSS Chapter", chapter).chapter_members
    for member in members:
        if member.email == user:
            return True

    return False


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
        "Approved": ("#B2E9C8", "#07A748"),
        "Open": ("#FEF0C7", "#F79009"),
        "Review Pending": ("#FEF0C7", "#F79009"),
        "Rejected": ("#FEE4E2", "#F04438"),
        "Cancelled": ("#FEE4E2", "#F04438"),
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


@frappe.whitelist()
def get_user_editable_doctype_fields(doctype, docname=None):
    meta = frappe.get_meta(doctype).as_dict()
    NOT_EDITABLE_FIELDS = ["is_published", "route", "user"]
    for field in meta["fields"]:
        if field["fieldname"] in NOT_EDITABLE_FIELDS:
            meta["fields"].remove(field)

    meta["fields"] = [
        {k: v for k, v in field.items() if filter_field_values(k)}
        for field in meta["fields"]
    ]

    if docname is not None:
        doc = frappe.get_doc(doctype, docname).as_dict()
        for field in meta["fields"]:
            if field["fieldname"] in doc:
                field["default"] = doc[field["fieldname"]]

    return meta["fields"]


@frappe.whitelist()
def insert_foss_profile_child_doc(
    parent, parenttype, parentfield, doctype, fields
):
    fields = json.loads(fields)
    doc = frappe.get_doc(
        {
            "doctype": doctype,
        }
    )
    for field in fields:
        doc.set(field, fields[field])
    doc.parent = parent
    doc.parenttype = parenttype
    doc.insert(ignore_permissions=True)
    parentdoc = frappe.get_doc(parenttype, parent)
    parentdoc.append(parentfield, doc)
    parentdoc.save(ignore_permissions=True)


# To remove
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


def get_user_socials(foss_user):
    user = frappe.get_doc("FOSS User Profile", foss_user).as_dict()
    SOCIAL_LINK_FIELDNAMES = [
        "github",
        "gitlab",
        "x",
        "linkedin",
        "instagram",
        "mastodon",
        "youtube",
        "medium",
    ]

    links = {}
    for field in user:
        if field in SOCIAL_LINK_FIELDNAMES and user[field]:
            links[field] = user[field]

    return links


@frappe.whitelist()
def get_meta(doctype):
    return frappe.get_meta(doctype).as_dict()


def get_signup_optin_checks():
    mapper = frappe._dict(
        {
            "terms_of_use": {
                "page_name": "terms_page",
                "title": "Terms of Use",
            },
            "privacy_policy": {
                "page_name": "privacy_policy_page",
                "title": "Privacy Policy",
            },
            "cookie_policy": {
                "page_name": "cookie_policy_page",
                "title": "Cookie Policy",
            },
            "code_of_conduct": {
                "page_name": "code_of_conduct_page",
                "title": "Code of Conduct",
            },
        }
    )
    checks = [
        "terms_of_use",
        "privacy_policy",
        "cookie_policy",
        "code_of_conduct",
    ]
    links = []

    for check in checks:
        if frappe.db.get_single_value("FOSSU Settings", check):
            page = frappe.db.get_single_value(
                "FOSSU Settings", mapper[check].get("page_name")
            )
            route = frappe.db.get_value("Web Page", page, "route")
            links.append(
                "<a target='_blank' href='/"
                + route
                + "'>"
                + mapper[check].get("title")
                + "</a>"
            )

    return (", ").join(links)


@frappe.whitelist(allow_guest=True)
def check_username_availability(username):
    username_exists = frappe.db.exists(
        "FOSS User Profile", {"username": username}
    )

    is_cityname = frappe.db.exists("City", {"name": username})
    return username_exists or is_cityname


@frappe.whitelist()
def create_foss_profile(user, username, fields):
    fields = json.loads(fields)
    args = {}
    args["doctype"] = "FOSS User Profile"
    args["user"] = user
    args["username"] = username
    args["is_published"] = 1
    args.update(fields)

    try:
        foss_profile = frappe.get_doc(args)
        foss_profile.insert(ignore_permissions=True)
    except Exception as e:
        frappe.throw(str(e))

    return foss_profile


@frappe.whitelist(allow_guest=True)
def check_if_profile_owner(username):
    profile_user = frappe.get_doc(
        "FOSS User Profile", {"username": username}
    )
    return profile_user.user == frappe.session.user


@frappe.whitelist()
def validate_profile_completion():
    """
    Check if the user has completed their profile
    """
    return frappe.db.exists(
        "FOSS User Profile",
        {"email": frappe.session.user},
    )


def get_grouped_events():
    events = frappe.get_all(
        "FOSS Chapter Event",
        fields=[
            "event_name",
            "chapter",
            "banner_image",
            "route",
            "must_attend",
            "event_location",
            "map_link",
            "event_start_date",
            "banner_image",
        ],
        filters={"status": "Approved", "is_published": 1},
        order_by="event_start_date",
    )
    return get_month_grouped_events(events)


def get_month_grouped_events(events):
    grouped_events = {"Upcoming FOSS Events": [], "Past Events": []}
    month_grouped_events = {
        "Upcoming FOSS Events": {},
        "Past Events": {},
    }
    now = now_datetime()

    for event in events:
        event_month_year = frappe.utils.formatdate(
            event.event_start_date, "MMMM yyyy"
        )
        event.month_year = event_month_year
        if event.event_start_date > now:
            grouped_events["Upcoming FOSS Events"].append(event)
        else:
            grouped_events["Past Events"].append(event)

    for key, values in grouped_events.items():
        for month_year, month_year_events in itertools.groupby(
            values, lambda x: x.month_year
        ):
            month_grouped_events[key][month_year] = list(
                month_year_events
            )

    return month_grouped_events
