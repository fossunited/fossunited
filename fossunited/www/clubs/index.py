import frappe

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    RSVP_RESPONSE,
    STUDENT_CLUB,
)

DEFAULT_LOGO = "/assets/fossunited/images/clubs/fossclub_logo.svg"
ACTIVE_STATUSES = ["Active", "Independent", "New"]


def get_context(context):
    context.no_cache = 1
    context.title = "FOSS Clubs"
    context.body_class = "scroll-smooth"
    context.roles = get_lead_roles()
    context.support_items = get_support_item_content()
    clubs = get_all_clubs()
    context.active_clubs = [club for club in clubs if not club["is_inactive"]]
    context.past_clubs = [club for club in clubs if club["is_inactive"]]


def get_lead_roles() -> list[dict[str, str]]:
    return [
        {
            "icon": "/assets/fossunited/images/clubs/community_icon.svg",
            "content": "Build a FOSS Community",
        },
        {
            "icon": "/assets/fossunited/images/clubs/workshop_icon.svg",
            "content": "Host Event and Workshops",
        },
        {
            "icon": "/assets/fossunited/images/clubs/teams_icon.svg",
            "content": "Build and Maintain Teams",
        },
    ]


def get_support_item_content() -> list[dict[str, str]]:
    return [
        {
            "icon": "ti-book-2",
            "heading": "Opportunities",
            "content": (
                "Support to present your work infront of the broader "
                "FOSS Community in India and abroad."
            ),
        },
        {
            "icon": "ti-microphone",
            "heading": "Speakers and Mentors",
            "content": "Access to speakers and mentors for club activities",
        },
        {
            "icon": "ti-empathize",
            "heading": "Mentorship",
            "content": (
                "Access to the FOSS United team and community for guidance "
                "and support in club activities and growth."
            ),
        },
        {
            "icon": "ti-cash",
            "heading": "Funding Support",
            "content": "Financial aid of up to ₹50,000 per club annually",  # noqa: E501
        },
    ]


def get_all_clubs() -> list[dict]:
    # Fetch all clubs (active and past) in one query
    clubs = frappe.db.get_all(
        CHAPTER,
        filters={"chapter_type": STUDENT_CLUB},
        fields=[
            "route",
            "chapter_name",
            "chapter_status",
            "chapter_logo",
            "institution_name",
            "city",
            "state",
            "name",
        ],
        order_by="chapter_name",
    )
    club_ids = [club["name"] for club in clubs]
    now = frappe.utils.now()

    # Batch fetch statistics
    participants_map = get_participants_count_map(club_ids)
    team_members_map = get_team_member_count_map(club_ids)
    events_map = get_events_map(club_ids)
    live_event_map, upcoming_event_map = get_live_and_upcoming_event_maps(club_ids, now)

    result = []
    for club in clubs:
        club_id = club["name"]
        status = club["chapter_status"]
        participants_count = participants_map.get(club_id, 0)
        team_member_count = team_members_map.get(club_id, 0)
        events = events_map.get(club_id, [])
        has_live_event = live_event_map.get(club_id, False)
        has_upcoming_event = upcoming_event_map.get(club_id, False)
        events_count = len(events)
        is_new = status == "New"
        is_inactive = status not in ACTIVE_STATUSES
        club_dict = {
            **club,
            "logo": club["chapter_logo"] or DEFAULT_LOGO,
            "participants_count": participants_count,
            "team_member_count": team_member_count,
            "events_count": events_count,
            "has_live_event": has_live_event,
            "has_upcoming_event": has_upcoming_event,
            "stats": [
                {"label": "Participants", "value": participants_count},
                {"label": "Events", "value": events_count},
                {"label": "Team Size", "value": team_member_count},
            ],
            "is_independent": status == "Independent",
            "is_new_club": is_new,
            "is_inactive": is_inactive,
        }
        result.append(club_dict)
    return result


def get_participants_count_map(club_ids: list[str]) -> dict[str, int]:
    # Get all RSVP_RESPONSE emails for all clubs, then count unique per club
    if not club_ids:
        return {}
    rows = frappe.db.get_all(
        RSVP_RESPONSE,
        filters={"chapter": ["in", club_ids]},
        fields=["chapter", "email"],
        page_length=999999,
    )
    participants_map = {}
    for row in rows:
        club_id = row["chapter"]
        email = row["email"]
        participants_map.setdefault(club_id, set()).add(email)
    return {k: len(v) for k, v in participants_map.items()}


def get_team_member_count_map(club_ids: list[str]) -> dict[str, int]:
    if not club_ids:
        return {}
    rows = frappe.db.get_all(
        CHAPTER_MEMBER,
        filters={
            "parent": ["in", club_ids],
            "parenttype": "FOSS Chapter",
        },
        fields=["parent"],
        page_length=999999,
    )
    team_members_map = {}
    for row in rows:
        club_id = row["parent"]
        team_members_map[club_id] = team_members_map.get(club_id, 0) + 1
    return team_members_map


def get_events_map(club_ids: list[str]) -> dict[str, list[dict]]:
    if not club_ids:
        return {}
    rows = frappe.db.get_all(
        EVENT,
        filters={
            "chapter": ["in", club_ids],
            "status": ["in", ["Live", "Concluded"]],
        },
        fields=["chapter", "event_start_date", "event_end_date"],
        page_length=999999,
    )
    events_map = {}
    for row in rows:
        club_id = row["chapter"]
        events_map.setdefault(club_id, []).append(row)
    return events_map


def get_live_and_upcoming_event_maps(
    club_ids: list[str], now
) -> tuple[dict[str, bool], dict[str, bool]]:
    if not club_ids:
        return {}, {}
    # Live events
    live_rows = frappe.db.get_all(
        EVENT,
        filters={
            "chapter": ["in", club_ids],
            "status": "Live",
            "event_start_date": ["<=", now],
            "event_end_date": [">=", now],
        },
        fields=["chapter"],
        page_length=999999,
    )
    # Upcoming events
    upcoming_rows = frappe.db.get_all(
        EVENT,
        filters={
            "chapter": ["in", club_ids],
            "status": "Live",
            "event_start_date": [">", now],
        },
        fields=["chapter"],
        page_length=999999,
    )
    live_map = {row["chapter"]: True for row in live_rows}
    upcoming_map = {row["chapter"]: True for row in upcoming_rows}
    return live_map, upcoming_map
