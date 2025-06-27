from datetime import datetime

import frappe

from fossunited.doctype_ids import CHAPTER, CHAPTER_MEMBER, EVENT, RSVP_RESPONSE


def get_context(context):
    context.title = "FOSS Clubs"
    context.body_class = "scroll-smooth"
    context.roles = get_lead_roles()
    context.support_items = get_support_item_content()
    context.active_clubs = get_active_clubs()
    context.past_clubs = get_past_clubs()


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
            "icon": "ti-microphone",
            "heading": "Expert Speakers",
            "content": "Provide experienced speakers for lectures and workshops.",
        },
        {
            "icon": "ti-book-2",
            "heading": "Educational Resources",
            "content": "Supply educational material and resources to facilitate learning.",
        },
        {
            "icon": "ti-empathize",
            "heading": "Mentorship",
            "content": "Provide access to mentors for guidance and assistance in projects.",
        },
        {
            "icon": "ti-cash",
            "heading": "Funding Support",
            "content": "Financial aid of up to ₹50,000 per club annually and top performing clubs will get additional support up to ₹50,000 to host FOSS Hack.",
        },
    ]


def get_active_clubs() -> list[dict[str, str]]:
    active_clubs = frappe.db.get_all(
        CHAPTER,
        filters={
            "chapter_type": "FOSS Club",
            "chapter_status": ["in", ["Active", "Independant"]],
        },
        fields=[
            "route",
            "chapter_name",
            "chapter_logo",
            "institution_name",
            "city",
            "state",
            "name",
            "creation",
        ],
        order_by="chapter_name",
    )

    club_statistics = {club["name"]: get_club_statistics(club["name"]) for club in active_clubs}

    for club in active_clubs:
        club["logo"] = club["chapter_logo"] or "/assets/fossunited/images/clubs/fossclub_logo.svg"
        statistics = club_statistics[club["name"]]
        club.update(statistics)
        club["stats"] = [
            {
                "label": "Participants",
                "value": statistics["participants_count"],
            },
            {
                "label": "Events",
                "value": statistics["events_count"],
            },
            {
                "label": "Team Size",
                "value": statistics["team_member_count"],
            },
        ]
        club["is_new_club"] = is_new_club(club["creation"])
        club["is_inactive"] = False

    return active_clubs


def get_past_clubs() -> list[dict[str, str]]:
    past_clubs = frappe.db.get_all(
        CHAPTER,
        filters={
            "chapter_type": "FOSS Club",
            "chapter_status": ["not in", ["Active", "Independant"]],
        },
        fields=[
            "route",
            "chapter_name",
            "chapter_logo",
            "institution_name",
            "city",
            "state",
            "name",
            "creation",
        ],
        order_by="chapter_name",
    )

    club_statistics = {club["name"]: get_club_statistics(club["name"]) for club in past_clubs}

    for club in past_clubs:
        club["logo"] = club["chapter_logo"] or "/assets/fossunited/images/clubs/fossclub_logo.svg"
        statistics = club_statistics[club["name"]]
        club.update(statistics)
        club["stats"] = [
            {
                "label": "Participants",
                "value": statistics["participants_count"],
            },
            {
                "label": "Events",
                "value": statistics["events_count"],
            },
            {
                "label": "Team Size",
                "value": statistics["team_member_count"],
            },
        ]
        club["is_new_club"] = False
        club["is_inactive"] = True

    return past_clubs


def get_club_statistics(club_id: str) -> dict[str, str | int]:
    participants_count = len(
        set(
            frappe.db.get_all(
                RSVP_RESPONSE,
                filters={"chapter": club_id},
                pluck="email",
                page_length=999999,
            )
        )
    )

    team_member_count = frappe.db.count(
        CHAPTER_MEMBER,
        filters={
            "parent": club_id,
            "parenttype": "FOSS Chapter",
        },
    )

    events = frappe.db.get_all(
        EVENT,
        filters={
            "chapter": club_id,
            "status": [
                "in",
                ["Live", "Concluded"],
            ],
        },
        fields=["event_start_date", "event_end_date"],
    )

    has_live_event = frappe.db.exists(
        EVENT,
        {
            "chapter": club_id,
            "status": "Live",
            "event_start_date": ["<=", frappe.utils.now()],
            "event_end_date": [">=", frappe.utils.now()],
        },
    )

    has_upcoming_event = frappe.db.exists(
        EVENT,
        {
            "chapter": club_id,
            "status": "Live",
            "event_start_date": [">", frappe.utils.now()],
        },
    )

    events_count = len(events) if has_live_event or has_upcoming_event else 0

    return {
        "participants_count": participants_count,
        "team_member_count": team_member_count,
        "events_count": events_count,
        "has_live_event": has_live_event,
        "has_upcoming_event": has_upcoming_event,
    }


def is_new_club(creation_date: datetime) -> bool:
    """
    A club is new if it was created in the last 90 days
    """
    return frappe.utils.days_diff(frappe.utils.now(), creation_date) <= 90
