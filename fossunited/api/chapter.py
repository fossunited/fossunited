import json
from zoneinfo import ZoneInfo

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_days, now_datetime
from ics import Calendar, Event
from ics.grammar.parse import ContentLine

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    CORE_TEAM,
    EVENT,
    EVENT_GRANTS,
    EVENT_VOLUNTEER,
    USER_PROFILE,
)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def check_if_chapter_member(chapter: str, user: str) -> bool:
    """
    Check if the user is a member of the chapter.

    Args:
        chapter (str): Chapter id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": user}, ["name"])

    if not profile:
        return False

    is_member = bool(
        frappe.db.exists(
            CHAPTER_MEMBER,
            {
                "parent": chapter,
                "parenttype": CHAPTER,
                "chapter_member": profile,
                "parentfield": "chapter_members",
            },
        )
    )

    return is_member


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def check_if_event_member(event: str) -> bool:
    """
    Check if the user is an event lead

    Args:
        event (str): Event id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": frappe.session.user}, ["name"])

    is_volunteer = bool(
        frappe.db.exists(
            EVENT_VOLUNTEER,
            {
                "parent": event,
                "parenttype": EVENT,
                "member": profile,
                "parentfield": "event_members",
            },
        )
    )

    return is_volunteer


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def check_if_chapter_or_event_core_member(event: str) -> bool:
    """
    A common function to check if user is either chapter or event member to give some access.
    This API function is intended to only apply for cases where every time event is created
    they would not add themselves to event_members table
    """
    event_doc = frappe.get_doc(EVENT, event, ["name"])
    chapter_id = event_doc.chapter
    is_team = bool(
        check_if_event_member(event) or check_if_chapter_member(chapter_id, frappe.session.user)
    )
    return is_team


# Only published event data is returned. No sensitive fields exposed.
_ICS_FIELDS = [
    "name",
    "modified",
    "event_name",
    "event_type",
    "event_bio",
    "event_location",
    "map_link",
    "chapter_name",
    "event_description",
    "livestream_link",
    "route",
    "event_start_date",
    "event_end_date",
]


def _build_ics_calendar(events):
    tz_name = frappe.db.get_single_value("System Settings", "time_zone") or "Asia/Kolkata"
    tz = ZoneInfo(tz_name)
    utc = ZoneInfo("UTC")
    c = Calendar()

    for event in events:
        start_dt = frappe.utils.get_datetime(event.event_start_date)
        end_dt = frappe.utils.get_datetime(event.event_end_date)
        start = start_dt.replace(tzinfo=tz) if start_dt.tzinfo is None else start_dt.astimezone(tz)
        end = end_dt.replace(tzinfo=tz) if end_dt.tzinfo is None else end_dt.astimezone(tz)

        if end < start:
            continue

        e = Event()
        e.uid = event.name
        e.name = event.event_name
        if event.modified:
            mod = frappe.utils.get_datetime(event.modified)
            e.last_modified = mod.replace(tzinfo=utc) if mod.tzinfo is None else mod
        if event.event_location and event.map_link:
            e.location = f"{event.event_location}\n{event.map_link}"
        else:
            e.location = event.event_location or event.map_link or None
        e.organizer = (event.chapter_name or "FOSS United") + " Community"
        if event.event_type:
            e.categories = {event.event_type}
        description_parts = []
        if event.event_bio:
            description_parts.append(event.event_bio)
        long_desc = frappe.utils.strip_html(event.event_description or "").strip()
        if long_desc:
            description_parts.append(long_desc)
        if event.livestream_link:
            description_parts.append(f"Livestream: {event.livestream_link}")
        e.description = "\n\n".join(description_parts) or None
        if event.route:
            route = str(event.route)
            e.url = (
                route
                if route.startswith("http")
                else f"https://fossunited.org/{route.lstrip('/')}"
            )
        e.begin = start
        e.end = end
        c.events.add(e)

    return c


def _ics_download_response(c, filename, *, is_subscription=False):
    frappe.response["type"] = "download"
    frappe.response["filename"] = filename
    frappe.response["filecontent"] = c.serialize().encode("utf-8")
    frappe.response["content_type"] = "text/calendar; charset=utf-8"
    if is_subscription:
        frappe.response["display_content_as"] = "inline"


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60 * 6)
def generate_ics(event_ids: str | list, chapter: str | None = None, download: bool = False):
    try:
        if isinstance(event_ids, str) and len(event_ids) > 10000:
            frappe.throw(_("Input too large"), frappe.ValidationError)

        ids = json.loads(event_ids) if isinstance(event_ids, str) else event_ids

        if not isinstance(ids, list):
            frappe.throw(_("event_ids must be a list"), frappe.ValidationError)

        if len(ids) > 30:
            frappe.throw(_("Maximum 30 events allowed per request"), frappe.ValidationError)

        for event_id in ids:
            if not isinstance(event_id, str) or len(event_id) > 140:
                frappe.throw(_("Invalid event ID format"), frappe.ValidationError)

    except (json.JSONDecodeError, ValueError):
        frappe.throw(_("Invalid JSON format"), frappe.ValidationError)

    if chapter and (not isinstance(chapter, str) or len(chapter) > 140):
        frappe.throw(_("Invalid chapter"), frappe.ValidationError)

    filters = [["name", "IN", ids], ["status", "=", "Live"], ["is_published", "=", 1]]
    if chapter:
        filters.append(["chapter", "=", chapter])

    events = frappe.db.get_all(EVENT, filters=filters, fields=_ICS_FIELDS)
    c = _build_ics_calendar(events)

    if download:
        _ics_download_response(c, "event.ics")
        return

    return c.serialize()


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60 * 60)
def upcoming_events_ics():
    """
    ICS subscription feed — upcoming published events + approved grants.
    Stable UIDs + LAST-MODIFIED so calendar apps detect reschedules.
    Subscribe via: /api/method/fossunited.api.chapter.upcoming_events_ics
    """
    now = now_datetime()

    events = frappe.db.get_all(
        EVENT,
        filters=[
            ["status", "=", "Live"],
            ["is_published", "=", 1],
            ["event_start_date", ">=", now],
        ],
        fields=_ICS_FIELDS,
    )

    grants = frappe.db.get_all(
        EVENT_GRANTS,
        filters={
            "grant_status": "Approved",
            "event_end_date": [">=", now],
            "grant_amount": [">", 10000],
        },
        fields=[
            "name",
            "modified",
            "event_name",
            "event_description",
            "event_start_date",
            "event_end_date",
            "event_location",
            "event_website",
        ],
    )
    for g in grants:
        g.chapter_name = "FOSS Event Grants"

        g.route = g.event_website

    c = _build_ics_calendar(list(events) + list(grants))
    # Calendar metadata for subscription clients
    c.extra.append(ContentLine(name="X-WR-CALNAME", value="FOSS United Events"))
    c.extra.append(ContentLine(name="REFRESH-INTERVAL;VALUE=DURATION", value="PT1H"))
    c.extra.append(ContentLine(name="X-PUBLISHED-TTL", value="PT1H"))
    _ics_download_response(c, "foss-upcoming-events.ics", is_subscription=True)


def get_chapter_members_email(chapter):
    return frappe.db.get_all(
        CHAPTER_MEMBER,
        {
            "parent": chapter,
            "role": ["in", [CORE_TEAM, "Volunteer"]],
        },
        pluck="email",
    )


def get_my_chapters(user):
    return frappe.get_all(
        CHAPTER_MEMBER,
        filters={"email": user},
        pluck="parent",
    )


@frappe.whitelist()
def get_my_chapter_dashboard():
    """
    '/dashboard/chapter' to show events+chapters belonging to the user.
    """
    user = frappe.session.user
    since_3w = add_days(now_datetime(), -21)

    chapter_names = get_my_chapters(user)
    chapters = []
    scheduled = []
    recent_concluded = []

    if chapter_names:
        chapters = frappe.get_all(
            CHAPTER,
            filters={"name": ["in", chapter_names]},
            fields=["*"],
        )

        for chapter in chapters:
            doc = frappe.get_doc(CHAPTER, chapter.name)
            scheduled.extend(doc.get_upcoming_events())
            recent = [
                e
                for e in doc.get_past_events()
                if e.event_end_date and (e.event_end_date >= since_3w)
            ]
            recent_concluded.extend(recent)

    # Also include events where user is an event volunteer (but not a chapter member)
    chapter_event_names = {e.name for e in scheduled + recent_concluded}
    volunteer_event_names = frappe.get_all(
        EVENT_VOLUNTEER,
        filters={"email": user, "parenttype": EVENT},
        pluck="parent",
    )
    only_volunteer_event_names = [n for n in volunteer_event_names if n not in chapter_event_names]
    if only_volunteer_event_names:
        scheduled.extend(
            frappe.get_all(
                EVENT,
                filters={
                    "name": ["in", only_volunteer_event_names],
                    "status": ["in", ["Live", "Draft"]],
                },
                fields=["*"],
            )
        )
        recent_concluded.extend(
            frappe.get_all(
                EVENT,
                filters={
                    "name": ["in", only_volunteer_event_names],
                    "status": ["not in", ["Live", "Draft"]],
                    "event_end_date": [">=", since_3w],
                },
                fields=["*"],
            )
        )

    return {
        "chapters": chapters,
        "scheduled": scheduled,
        "recent_concluded": recent_concluded,
    }
