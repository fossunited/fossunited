import itertools
import json

import frappe
from frappe.utils import format_datetime, format_time
from frappe.utils.data import now_datetime


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
        fields=["*"],
        filters={
            "status": ["in", ["Approved", "Live", "Concluded"]],
            "is_published": 1,
        },
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


@frappe.whitelist(allow_guest=True)
def get_foss_profile(email):
    """
    Return the FOSS User Profile doc linked to the parameter email.
    """
    if email in ["guest@example.com", "admin@example.com"]:
        return None

    return frappe.get_doc("FOSS User Profile", {"user": email})
