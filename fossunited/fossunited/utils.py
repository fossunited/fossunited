import itertools
from collections import defaultdict
from datetime import datetime

import frappe
from frappe.utils import add_to_date, get_datetime, nowdate
from frappe.utils.data import now_datetime

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    CONFERENCE,
    EVENT,
    HACKATHON,
    STUDENT_CLUB,
    USER_PROFILE,
    VIRTUAL,
)


# Jinja Filter
def get_profile_image(email):
    profile = get_foss_profile(email)
    return profile.profile_photo or "/assets/fossunited/images/defaults/user_profile_image.png"


def get_event_volunteers(event):
    volunteers = frappe.get_doc(EVENT, event).event_members
    return volunteers


def is_user_team_member(chapter, user):
    members = frappe.get_doc(CHAPTER, chapter).chapter_members
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
        "Withdrawn": ("#FEE4E2", "#F04438"),
        "Rejected": ("#FEE4E2", "#F04438"),
        "Cancelled": ("#FEE4E2", "#F04438"),
        "Default": ("#171717", "#FFFFFF"),
    }
    bg_color, text_color = colors.get(text, colors["Default"])

    return (
        f'<span class="badge badge-{size}" '
        f'style="background-color: {bg_color}; color: {text_color};">{text}</span>'
    )


def get_doc_likes(doctype, name):
    return frappe.db.get_all(
        "Comment",
        {
            "comment_type": "Like",
            "reference_doctype": doctype,
            "reference_name": name,
        },
        pluck="comment_email",
        page_length=9999,
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


@frappe.whitelist()
def get_user_editable_doctype_fields(doctype, docname=None):
    meta = frappe.get_meta(doctype).as_dict()
    NOT_EDITABLE_FIELDS = ["is_published", "route", "user"]
    for field in meta["fields"]:
        if field["fieldname"] in NOT_EDITABLE_FIELDS:
            meta["fields"].remove(field)

    meta["fields"] = [
        {k: v for k, v in field.items() if filter_field_values(k)} for field in meta["fields"]
    ]

    if docname is not None:
        doc = frappe.get_doc(doctype, docname).as_dict()
        for field in meta["fields"]:
            if field["fieldname"] in doc:
                field["default"] = doc[field["fieldname"]]

    return meta["fields"]


def get_user_socials(foss_user):
    """
    Function to get dict for social svg for profile page.
    Based on svgl.app/library
    """
    user = frappe.get_doc(USER_PROFILE, foss_user).as_dict()
    SOCIAL_LINK_FIELDNAMES = [
        "github",
        "gitlab",
        "mastodon",
        "bluesky",
        "devto",
        "x",
        "linkedin",
        "instagram",
        "youtube",
    ]

    KEY_RENAMES = {
        "github": "github_light",
        "devto": "devto-light",
        "instagram": "instagram-icon",
        "facebook": "facebook-icon",
    }

    REVERSE_RENAMES = {v: k for k, v in KEY_RENAMES.items()}

    socials = {
        KEY_RENAMES.get(k, k): v for k, v in user.items() if k in SOCIAL_LINK_FIELDNAMES and v
    }

    def sort_key(item):
        original_key = REVERSE_RENAMES.get(item[0], item[0])
        return SOCIAL_LINK_FIELDNAMES.index(original_key)

    return dict(sorted(socials.items(), key=sort_key))


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
            page = frappe.db.get_single_value("FOSSU Settings", mapper[check].get("page_name"))
            route = frappe.db.get_value("Web Page", page, "route")
            links.append(
                "<a target='_blank' href='/" + route + "'>" + mapper[check].get("title") + "</a>"
            )

    return (", ").join(links)


@frappe.whitelist(allow_guest=True)
def check_username_availability(username):
    username_exists = frappe.db.exists(USER_PROFILE, {"username": username})

    is_cityname = frappe.db.exists("City", {"name": username})
    return username_exists or is_cityname


@frappe.whitelist(allow_guest=True)
def check_if_profile_owner(username):
    profile_user = frappe.get_doc(USER_PROFILE, {"username": username})
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


def get_main_foss_events():
    """
    Get main foss events to be shown for grid page in /events
    only for City chapters and Conferences
    """
    events = frappe.get_all(
        EVENT,
        fields=["*"],
        filters={
            "status": "Live",
            "is_published": 1,
            "event_end_date": [">=", frappe.utils.now()],
        },
        order_by="event_start_date",
        page_length=100,
    )

    allowed_types = {CITY_COMMUNITY, CONFERENCE, VIRTUAL}
    filtered_events = []

    chapters = list({e.get("chapter") for e in events if e.get("chapter")})
    chapter_type_map = {}
    if chapters:
        rows = frappe.db.get_all(
            CHAPTER,
            filters={"name": ["in", chapters]},
            fields=["name", "chapter_type"],
        )
        chapter_type_map = {r.name: r.chapter_type for r in rows}

    for event in events:
        ctype = chapter_type_map.get(event.get("chapter"))
        if ctype in allowed_types:
            filtered_events.append(event)

    return filtered_events[:12]


def get_grouped_events_by_chapter_type():
    """
    Retrieves FOSS Chapter Events and Hackathons,
    groups them by custom categories based on chapter_type,
    and then groups each by month and year.
    Includes a special 'All Events' group for everything.
    """

    # configurable grouping: view name -> list of chapter types
    GROUPING_CONFIG = {
        "default": [CITY_COMMUNITY, CONFERENCE, VIRTUAL],
        "club": [STUDENT_CLUB],
    }

    # fetch all events
    events = frappe.get_all(
        EVENT,
        fields=["*"],
        filters={"is_published": 1},
        order_by="event_start_date asc",
    )

    hackathons = frappe.get_all(
        HACKATHON,
        fields=["*"],
        filters={"is_published": 1},
        order_by="start_date asc",
    )

    # cache chapter_type lookups to avoid repeated DB calls
    chapter_type_cache = {}

    def get_chapter_type(chapter_name):
        if not chapter_name:
            return "Unknown"
        if chapter_name in chapter_type_cache:
            return chapter_type_cache[chapter_name]
        chapter_type = frappe.db.get_value(CHAPTER, chapter_name, "chapter_type") or "Unknown"
        chapter_type_cache[chapter_name] = chapter_type
        return chapter_type

    # group events by chapter_type
    event_groups = defaultdict(list)
    hackathon_groups = defaultdict(list)

    all_events = []
    all_hackathons = []

    for event in events:
        chapter_type = get_chapter_type(event.get("chapter"))
        event_groups[chapter_type].append(event)
        all_events.append(event)

    for hackathon in hackathons:
        chapter_type = get_chapter_type(hackathon.get("chapter"))
        hackathon_groups[chapter_type].append(hackathon)
        all_hackathons.append(hackathon)

    # helper: collect events/hackathons for a list of chapter types
    def collect_events_for_types(types):
        events = []
        hackathons = []
        for chapter_type in types:
            events.extend(event_groups.get(chapter_type, []))
            hackathons.extend(hackathon_groups.get(chapter_type, []))
        return events, hackathons

    # build final result grouped by custom views
    result = {}

    for view_name, chapter_types in GROUPING_CONFIG.items():
        view_events, view_hackathons = collect_events_for_types(chapter_types)
        result[view_name] = get_month_grouped_events(view_events, view_hackathons)

    # optionally include 'All Events'
    result["All Events"] = get_month_grouped_events(all_events, all_hackathons)

    return result


def get_chapter_details():
    """
    Retrieves FOSS Chapter Events and Hackathons, then groups them by month and year, separating
    upcoming and past events.
    """
    chapters = frappe.db.get_all(
        CHAPTER,
        fields=["chapter_name", "name", "chapter_type", "city"],
        order_by="chapter_name asc",
        page_length=9999,
    )
    return chapters


def get_all_city_names():
    """
    Get all city names for select option use.
    """
    cities = frappe.db.get_all(
        "City",
        fields=["name"],
        order_by="name asc",
        page_length=9999,
    )
    return cities


def process_event(event, event_list):
    """
    Processes a single event or hackathon, adding it to the upcoming or past events list based on
    the current date.
    """
    now = now_datetime()

    # Start drives grouping; End drives classification
    start_raw = event.get("event_start_date") or event.get("start_date")
    end_raw = event.get("event_end_date") or event.get("end_date") or start_raw
    if not start_raw:
        return

    start_dt = frappe.utils.get_datetime(start_raw)
    end_dt = frappe.utils.get_datetime(end_raw)
    event["month_year"] = frappe.utils.formatdate(start_dt, "MMMM yyyy")
    event["_sort_dt"] = start_dt

    if end_dt >= now:
        event_list["Upcoming Events"].append(event)
    else:
        event_list["Past Events"].append(event)


def get_month_grouped_events(events, hackathons):
    """
    Groups events and hackathons by month and year, ensuring they are sorted chronologically
    within each group.
    """
    grouped_events = {"Upcoming Events": [], "Past Events": []}

    for event in events:
        process_event(event, grouped_events)

    for hackathon in hackathons:
        process_event(hackathon, grouped_events)

    month_grouped_events = {key: {} for key in grouped_events}

    for key, values in grouped_events.items():
        # Ensure only dicts with month_year key are grouped
        valid_values = [v for v in values if isinstance(v, dict) and v.get("month_year")]
        valid_values.sort(key=lambda x: x.get("_sort_dt"))
        for month_year, month_year_events in itertools.groupby(
            valid_values, key=lambda x: x.get("month_year")
        ):
            month_grouped_events[key][month_year] = list(month_year_events)

    for key in month_grouped_events:
        if key == "Upcoming Events":
            sorted_month_years = sorted(
                month_grouped_events[key].keys(),
                key=lambda x: datetime.strptime(x, "%B %Y"),
            )
        else:
            sorted_month_years = sorted(
                month_grouped_events[key].keys(),
                key=lambda x: datetime.strptime(x, "%B %Y"),
                reverse=True,
            )
        month_grouped_events[key] = {
            month: month_grouped_events[key][month] for month in sorted_month_years
        }

    return month_grouped_events


@frappe.whitelist(allow_guest=True)
def get_foss_profile(email):
    """
    Return the FOSS User Profile doc linked to the parameter email.
    """
    if email in ["guest@example.com", "admin@example.com"]:
        return None

    profile = frappe.db.get_value(
        USER_PROFILE,
        {"user": email},
        [
            "name",
            "full_name",
            "user",
            "profile_photo",
            "username",
            "route",
            "github",
            "email",
            "gitlab",
        ],
        as_dict=1,
    )
    return profile


@frappe.whitelist(allow_guest=True)
def get_select_field_options(doctype_name, fieldname):
    """
    Return options for a Select field in a Doctype as a list of strings.
    """
    meta = frappe.get_meta(doctype_name)
    field = meta.get_field(fieldname)
    if not field or field.fieldtype != "Select":
        return []

    # Options are stored as newline-separated string in `field.options`
    options = field.options.split("\n") if field.options else []
    return options


@frappe.whitelist(allow_guest=True)
def get_volunteers_data():
    """
    Get all volunteers data - returns flat list of members
    Frontend handles grouping and sorting via JavaScript

    Returns:
        dict: Contains members list and stats
    """

    # Calculate one year ago date
    one_year_ago = add_to_date(nowdate(), years=-1)
    one_year_ago_dt = get_datetime(one_year_ago)

    # Get all chapters with their latest event date in one query
    chapters_data = frappe.db.sql(
        """
        SELECT
            c.name as chapter_id,
            c.chapter_name,
            c.chapter_logo,
            MAX(e.event_start_date) as latest_event_date
        FROM `tabFOSS Chapter` c
        LEFT JOIN `tabFOSS Chapter Event` e ON e.chapter = c.name
        GROUP BY c.name, c.chapter_name, c.chapter_logo
    """,
        as_dict=True,
    )

    # Build chapter lookup maps
    active_chapters = set()
    chapter_info = {}

    for chapter in chapters_data:
        chapter_info[chapter.chapter_id] = {
            "name": chapter.chapter_name,
            "logo": chapter.chapter_logo
            or "/assets/fossunited/images/chapter/foss_club_profile.svg",
        }

        if chapter.latest_event_date and chapter.latest_event_date >= one_year_ago_dt:
            active_chapters.add(chapter.chapter_id)

    # Get all chapter members with profile data in single query
    members_raw = frappe.db.sql(
        """
        SELECT DISTINCT
            cm.chapter_member,
            cm.parent as chapter_id,
            p.route as username,
            p.full_name,
            p.profile_photo,
            p.show_activity,
            p.current_city
        FROM `tabFOSS Chapter Lead Team Member` cm
        LEFT JOIN `tabFOSS User Profile` p ON cm.chapter_member = p.name
        WHERE cm.chapter_member IS NOT NULL
        AND cm.chapter_member != ''
        AND p.name IS NOT NULL
    """,
        as_dict=True,
    )

    # Build member data structure
    members_map = {}
    active_member_ids = set()

    for row in members_raw:
        member_id = row.chapter_member
        chapter_id = row.chapter_id
        is_active_chapter = chapter_id in active_chapters

        # Initialize member if not exists
        if member_id not in members_map:
            members_map[member_id] = {
                "id": member_id,
                "username": row.username,
                "name": row.full_name,
                "photo": row.profile_photo
                or "/assets/fossunited/images/defaults/user_profile_image.png",
                "activity": 1 if row.show_activity else 0,
                "city": row.current_city or "Anonymous",
                "chapters": [],
                "is_active": 0,
            }

        # Add chapter info
        if chapter_id in chapter_info:
            members_map[member_id]["chapters"].append(
                {
                    "id": chapter_id,
                    "name": chapter_info[chapter_id]["name"],
                    "logo": chapter_info[chapter_id]["logo"],
                    "active": 1 if is_active_chapter else 0,
                }
            )

            # Mark member as active if in any active chapter
            if is_active_chapter:
                members_map[member_id]["is_active"] = 1
                active_member_ids.add(member_id)

    # Convert to list and separate active/past
    all_members = list(members_map.values())
    active_members = [m for m in all_members if m["is_active"]]
    past_members = [m for m in all_members if not m["is_active"]]

    return {
        "active": active_members,
        "past": past_members,
        "stats": {
            "active_count": len(active_members),
            "past_count": len(past_members),
            "communities_count": len(active_chapters),
        },
    }
