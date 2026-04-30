import frappe
from frappe import qb
from frappe.query_builder.functions import Max
from frappe.utils import add_to_date, get_datetime, nowdate, sanitize_html

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    CITY_COMMUNITY,
    CONFERENCE,
    EVENT,
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
def get_user_editable_doctype_fields(doctype: str, docname: str | None = None):
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
def get_meta(doctype: str):
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def check_username_availability(username: str):
    username_exists = frappe.db.exists(USER_PROFILE, {"username": username})

    is_cityname = frappe.db.exists("City", {"name": username})
    return username_exists or is_cityname


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def check_if_profile_owner(username: str):
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_foss_profile(email: str):
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_select_field_options(doctype_name: str, fieldname: str):
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


def get_volunteers_data():
    """
    Get all volunteers data - returns flat list of members
    """
    Member = qb.DocType(CHAPTER_MEMBER)
    Profile = qb.DocType(USER_PROFILE)
    Chapter = qb.DocType(CHAPTER)
    Event = qb.DocType(EVENT)

    results = (
        qb.from_(Member)
        .inner_join(Profile)
        .on(Member.chapter_member == Profile.name)
        .inner_join(Chapter)
        .on(Member.parent == Chapter.name)
        .left_join(Event)
        .on(Event.chapter == Chapter.name)
        .select(
            Member.chapter_member,
            Profile.route,
            Profile.full_name,
            Profile.profile_photo,
            Profile.show_activity,
            Profile.current_city,
            Chapter.chapter_name,
            Chapter.chapter_logo,
            Chapter.route.as_("chapter_route"),
            Max(Event.event_start_date).as_("latest_event"),
        )
        .where(Member.chapter_member.isnotnull())
        .groupby(Member.chapter_member, Member.parent)
    ).run(as_dict=True)

    # Convert datetime to string for JSON serialization
    for row in results:
        if row.get("latest_event"):
            row["latest_event"] = row["latest_event"].isoformat()

    return results


def get_volunteers_stats():
    """Just get the stats for active volunteers. For page initial load."""
    one_year_ago = get_datetime(add_to_date(nowdate(), years=-1))

    ChapterMember = qb.DocType(CHAPTER_MEMBER)
    Chapter = qb.DocType(CHAPTER)
    Event = qb.DocType(EVENT)

    query = (
        frappe.qb.from_(ChapterMember)
        .inner_join(Chapter)
        .on(ChapterMember.parent == Chapter.name)
        .left_join(Event)
        .on(Event.chapter == Chapter.name)
        .select(ChapterMember.chapter_member, Chapter.name.as_("chapter_name"))
        .where(ChapterMember.chapter_member.isnotnull())
        .groupby(ChapterMember.chapter_member, Chapter.name)
        .having(Max(Event.event_start_date) >= one_year_ago)
    )

    rows = query.run(as_dict=True)

    # Count unique members and chapters (we can use email also)
    unique_members = {row["chapter_member"] for row in rows}
    unique_chapters = {row["chapter_name"] for row in rows}

    return {
        "active_count": len(unique_members),
        "communities_count": len(unique_chapters),
    }


def get_event_sponsors(sponsor_list):
    """
    Get event sponsors in sorted order (date of confirm).
    """
    # Get IP dates
    ip_dates = {
        ip["company"].strip().lower(): ip["joining_date"]
        for ip in frappe.db.get_all("Industry Partners", fields=["company", "joining_date"])
        if ip.get("company") and ip.get("joining_date")
    }

    # Tier order
    tier_rank = {
        "Patrons": 0,
        "Platinum": 1,
        "Gold": 2,
        "Silver": 3,
        "Bronze": 4,
        "Venue Partner": 5,
    }

    # Group by tier
    groups = {}
    for sponsor in sponsor_list:
        # Get tier name
        tier = sponsor.custom_tier.strip() if sponsor.tier == "Custom" else sponsor.tier

        # Get sort date (confirm date first, then IP date)
        name_key = (sponsor.sponsor_name or "").strip().lower()
        sponsor.sort_date = sponsor.date_of_confirm or ip_dates.get(name_key)
        sponsor.is_ip = name_key in ip_dates

        groups.setdefault(tier, []).append(sponsor)

    # Sort within each tier
    for sponsors in groups.values():
        sponsors.sort(
            key=lambda s: (
                s.sort_date is None,  # No date last
                s.sort_date,  # Sort by date
                not s.is_ip,  # IP first
                (s.sponsor_name or "").lower(),  # Then by name
            )
        )

    # Sort tiers
    return dict(sorted(groups.items(), key=lambda x: tier_rank.get(x[0], 999)))


def sanitize_text_content(value: str | None, fallback=""):
    from bs4 import BeautifulSoup

    if not value:
        return fallback

    cleaned = sanitize_html(value, always_sanitize=True)

    soup = BeautifulSoup(cleaned, "html.parser")

    for tag in soup.find_all(["img", "svg", "math", "style", "script", "iframe", "object"]):
        tag.decompose()

    for tag in soup.find_all(True):
        tag.attrs = {
            k: v
            for k, v in tag.attrs.items()
            if not k.lower().startswith("on") and k.lower() not in ("style",)
        }

    return str(soup)
