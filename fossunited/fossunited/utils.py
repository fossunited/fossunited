import itertools
import json
from datetime import datetime

import frappe
from frappe.utils.data import now_datetime

from fossunited.doctype_ids import USER_PROFILE


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


def is_user_team_member(chapter, user):
    members = frappe.get_doc("FOSS Chapter", chapter).chapter_members
    for member in members:
        if member.email == user:
            return True

    return False


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


def get_user_socials(foss_user):
    user = frappe.get_doc(USER_PROFILE, foss_user).as_dict()
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
        USER_PROFILE, {"username": username}
    )

    is_cityname = frappe.db.exists("City", {"name": username})
    return username_exists or is_cityname


@frappe.whitelist(allow_guest=True)
def check_if_profile_owner(username):
    profile_user = frappe.get_doc(
        USER_PROFILE, {"username": username}
    )
    return profile_user.user == frappe.session.user


@frappe.whitelist()
def validate_profile_completion():
    """
    Check if the user has completed their profile
    """
    return frappe.db.exists(
        USER_PROFILE,
        {"email": frappe.session.user},
    )


def get_grouped_events():
    """
    Retrieves FOSS Chapter Events and Hackathons, then groups them by month and year, separating upcoming and past events.
    """
    events = frappe.get_all(
        "FOSS Chapter Event",
        fields=["*"],
        filters={
            "status": ["in", ["Approved", "Live", "Concluded"]],
            "is_published": 1,
        },
        order_by="event_start_date",
    )

    hackathons = frappe.get_all(
        "FOSS Hackathon",
        fields=["*"],
        filters={
            "is_published": 1,
        },
        order_by="start_date",
    )
    return get_month_grouped_events(events, hackathons)


def process_event(event, event_list):
    """
    Processes a single event or hackathon, adding it to the upcoming or past events list based on the current date.
    """
    now = now_datetime()
    event_date = (
        event.event_start_date
        if event.event_start_date
        else event.start_date
    )
    event_month_year = frappe.utils.formatdate(
        event_date, "MMMM yyyy"
    )
    event.month_year = event_month_year
    if event_date > now:
        event_list["Upcoming FOSS Events"].append(event)
    else:
        event_list["Past Events"].append(event)


def get_month_grouped_events(events, hackathons):
    """
    Groups events and hackathons by month and year, ensuring they are sorted chronologically within each group.
    """
    grouped_events = {"Upcoming FOSS Events": [], "Past Events": []}

    for event in events:
        process_event(event, grouped_events)

    for hackathon in hackathons:
        process_event(hackathon, grouped_events)

    month_grouped_events = {key: {} for key in grouped_events}

    for key, values in grouped_events.items():
        values.sort(
            key=lambda x: x.event_start_date
            if x.event_start_date
            else x.start_date
        )
        for month_year, month_year_events in itertools.groupby(
            values, key=lambda x: x.month_year
        ):
            month_grouped_events[key][month_year] = list(
                month_year_events
            )

    for key in month_grouped_events:
        sorted_month_years = sorted(
            month_grouped_events[key].keys(),
            key=lambda x: datetime.strptime(x, "%B %Y"),
        )
        month_grouped_events[key] = {
            month: month_grouped_events[key][month]
            for month in sorted_month_years
        }

    return month_grouped_events


@frappe.whitelist(allow_guest=True)
def get_foss_profile(email):
    """
    Return the FOSS User Profile doc linked to the parameter email.
    """
    if email in ["guest@example.com", "admin@example.com"]:
        return None

    return frappe.get_doc(USER_PROFILE, {"user": email})
