from collections import defaultdict

import frappe
from frappe.utils import fmt_money

from fossunited.doctype_ids import EVENT_GRANTS, PROJ_GRANTS

OPEN_STATUSES = ["Open", "Under Review"]
APPROVED_STATUS = ["Approved", "Disbursed", "Ongoing"]
DISBURSED_STATUS = [*APPROVED_STATUS]
DISBURSED_STATUS.remove("Ongoing")


def get_context(context):
    """Main grants landing page with card data"""

    project_counts = get_project_grant_counts()
    event_counts = get_event_grant_counts()

    context.grant_types = [
        {
            "title": "Project Grants",
            "icon": "ti ti-device-imac-code",
            "description": """Project grants are largely “non-thematic”.
            In the past, we have funded developer tools,
            consumer apps, non-profit foundations, FOSS mirrors, Open Hardware projects,
            individual contributors, and even new programming languages! """,
            "route": "/grants/projects",
            "completed": project_counts["Project"]["completed"],
            "pending": project_counts["Project"]["pending"],
        },
        {
            "title": "Event Grants",
            "icon": "ti ti-building-circus",
            "description": """Our approach towards funding events has evolved to support
            events that directly benefit the FOSS community.
            To apply for a FOSS event grant,
            please send us a detailed proposal at grants@fossunited.org""",
            "route": "/grants/events",
            "completed": event_counts["completed"],
            "pending": event_counts["pending"],
        },
        {
            "title": "Fellowships",
            "icon": "ti ti-heart-handshake",
            "description": """We provide grants to individuals contributing to
            FOSS projects and communities. These grants help developers, students,
            and community organizers dedicate time to FOSS work.""",
            "route": "/grants/fellowships",
            "completed": project_counts["Fellowship"]["completed"],
            "pending": project_counts["Fellowship"]["pending"],
        },
    ]

    context.recent_project_grants = get_recent_project_grants("Project")
    context.recent_fellowship_grants = get_recent_project_grants("Fellowship")
    context.recent_event_grants = get_recent_event_grants()
    context.no_cache = 1

    return context


def get_project_grant_counts():
    """Return counts grouped by grant_type and status"""

    rows = frappe.db.get_all(
        PROJ_GRANTS,
        fields=[
            "grant_type",
            "grant_status",
            {"COUNT": "name", "as": "count"},
        ],
        filters={
            "grant_status": ["in", OPEN_STATUSES + APPROVED_STATUS],
        },
        group_by="grant_type, grant_status",
    )

    counts = {
        "Project": {"completed": 0, "pending": 0},
        "Fellowship": {"completed": 0, "pending": 0},
    }

    for row in rows:
        if row.grant_status in DISBURSED_STATUS:
            counts[row.grant_type]["completed"] += row.count
        else:
            counts[row.grant_type]["pending"] += row.count

    return counts


def get_event_grant_counts():
    rows = frappe.db.get_all(
        EVENT_GRANTS,
        fields=[
            "grant_status",
            {"COUNT": "name", "as": "count"},
        ],
        filters={
            "grant_status": ["in", OPEN_STATUSES + APPROVED_STATUS],
        },
        group_by="grant_status",
    )

    completed = 0
    pending = 0

    for row in rows:
        if row.grant_status in DISBURSED_STATUS:
            completed += row.count
        else:
            pending += row.count

    return {"completed": completed, "pending": pending}


_PROJ_GRANT_FIELDS = [
    "name",
    "project_name",
    "project_website",
    "about_project",
    "date_of_provision",
    "grant_amount",
    "co_sponsor",
    "grant_type",
    "modified",
]

_EVENT_GRANT_FIELDS = [
    "name",
    "event_name",
    "event_website",
    "event_description",
    "event_start_date",
    "grant_amount",
    "event_organiser",
    "modified",
]


def fetch_project_grants(limit=None):
    kwargs = dict(
        filters={"grant_status": ["in", APPROVED_STATUS], "grant_type": "Project"},
        fields=_PROJ_GRANT_FIELDS,
        order_by="date_of_provision desc",
    )
    if limit is not None:
        kwargs["limit"] = limit
    return frappe.db.get_all(PROJ_GRANTS, **kwargs)


def fetch_fellowship_grants(limit=None):
    kwargs = dict(
        filters={"grant_status": ["in", APPROVED_STATUS], "grant_type": "Fellowship"},
        fields=_PROJ_GRANT_FIELDS,
        order_by="date_of_provision desc",
    )
    if limit is not None:
        kwargs["limit"] = limit
    return frappe.db.get_all(PROJ_GRANTS, **kwargs)


def fetch_event_grants(limit=None):
    kwargs = dict(
        filters={"grant_status": ["in", APPROVED_STATUS]},
        fields=_EVENT_GRANT_FIELDS,
        order_by="event_start_date desc",
    )
    if limit is not None:
        kwargs["limit"] = limit
    return frappe.db.get_all(EVENT_GRANTS, **kwargs)


def fetch_all_grants(limit=None):
    return (
        fetch_project_grants(limit=limit)
        + fetch_fellowship_grants(limit=limit)
        + fetch_event_grants(limit=limit)
    )


def get_recent_project_grants(grant_type):
    fetch = fetch_fellowship_grants if grant_type == "Fellowship" else fetch_project_grants
    return [format_project_grant(g) for g in fetch(limit=3)]


def get_recent_event_grants():
    return [format_event_grant(g) for g in fetch_event_grants(limit=3)]


def format_project_grant(grant, grant_type=None):
    return {
        "name": grant.project_name,
        "url": grant.project_website,
        "description": grant.about_project,
        "year": grant.date_of_provision.year if grant.date_of_provision else None,
        "date": (
            grant.date_of_provision.strftime("%Y-%m-%d") if grant.date_of_provision else None
        ),
        "grant_amount": grant.grant_amount,
        "amount": (
            fmt_money(grant.grant_amount, precision=0, currency="INR")
            if grant.grant_amount is not None
            else "N/A"
        ),
        "co_sponsor": grant.co_sponsor,
        "grant_type": grant_type,
    }


def format_event_grant(grant, grant_type=None):
    return {
        "name": grant.event_name,
        "url": grant.event_website,
        "description": grant.event_description or "FOSS event grant",
        "year": grant.event_start_date.year if grant.event_start_date else None,
        "date": (grant.event_start_date.strftime("%Y-%m-%d") if grant.event_start_date else None),
        "date_display": grant.event_start_date.strftime("%d %b %Y"),
        "grant_amount": grant.grant_amount,
        "amount": (
            fmt_money(grant.grant_amount, precision=0, currency="INR")
            if grant.grant_amount is not None
            else "N/A"
        ),
        "organizer": grant.event_organiser,
        "grant_type": grant_type,
    }


def group_grants_by_year(grants, formatter):
    """
    Groups formatted grant items by year.
    """
    grouped = defaultdict(list)

    for grant in grants:
        item = formatter(grant)
        year = item.get("year")

        if not year:
            continue

        grouped[year].append(item)

    return dict(sorted(grouped.items(), reverse=True))
