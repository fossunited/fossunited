import frappe

from fossunited.doctype_ids import EVENT_GRANTS, PROJ_GRANTS

OPEN_STATUSES = ["Open", "Under Review"]
APPROVED_STATUS = "Approved"


def get_context(context):
    """Main grants landing page with card data"""

    project_counts = get_project_grant_counts()
    event_counts = get_event_grant_counts()

    context.grant_types = [
        {
            "title": "Project Grants",
            "icon": "ti ti-device-imac-code",
            "description": """We fund FOSS projects by raising funds from the tech industry,
            either through our Industry Partnership Program or
            by reaching out to them upon receiving requests from FOSS projects/organizations.""",
            "route": "/grants/project",
            "completed": project_counts["Project"]["completed"],
            "pending": project_counts["Project"]["pending"],
        },
        {
            "title": "Event Grants",
            "icon": "ti ti-building-circus",
            "description": """Our grants program provide financial support to FOSS events.
            To avail an event grant, write to us with a proposal on the event specifics like goals,
            target audience, support links and documents etc.""",
            "route": "/grants/event",
            "completed": event_counts["completed"],
            "pending": event_counts["pending"],
        },
        {
            "title": "Fellowship Grants",
            "icon": "ti ti-heart-handshake",
            "description": """Fellowship grants support individuals contributing to
            FOSS projects and communities. These grants help developers, students,
            and community organizers dedicate time to open source work.""",
            "route": "/grants/fellowship",
            "completed": project_counts["Fellowship"]["completed"],
            "pending": project_counts["Fellowship"]["pending"],
        },
    ]

    context.recent_project_grants = get_recent_project_grants("Project")
    context.recent_fellowship_grants = get_recent_project_grants("Fellowship")
    context.recent_event_grants = get_recent_event_grants()

    return context


def get_project_grant_counts():
    """Return counts grouped by grant_type and status"""

    rows = frappe.db.get_all(
        PROJ_GRANTS,
        fields=[
            "grant_type",
            "grant_status",
            "count(name) as count",
        ],
        filters={
            "grant_status": ["in", OPEN_STATUSES + [APPROVED_STATUS]],
        },
        group_by="grant_type, grant_status",
    )

    counts = {
        "Project": {"completed": 0, "pending": 0},
        "Fellowship": {"completed": 0, "pending": 0},
    }

    for row in rows:
        if row.grant_status == APPROVED_STATUS:
            counts[row.grant_type]["completed"] = row.count
        else:
            counts[row.grant_type]["pending"] += row.count

    return counts


def get_event_grant_counts():
    rows = frappe.db.get_all(
        EVENT_GRANTS,
        fields=[
            "grant_status",
            "count(name) as count",
        ],
        filters={
            "grant_status": ["in", OPEN_STATUSES + [APPROVED_STATUS]],
        },
        group_by="grant_status",
    )

    completed = 0
    pending = 0

    for row in rows:
        if row.grant_status == APPROVED_STATUS:
            completed = row.count
        else:
            pending += row.count

    return {"completed": completed, "pending": pending}


def get_recent_project_grants(grant_type):
    grants = frappe.db.get_all(
        PROJ_GRANTS,
        filters={
            "grant_status": APPROVED_STATUS,
            "grant_type": grant_type,
        },
        fields=[
            "project_name",
            "project_website",
            "about_project",
            "date_of_provision",
            "grant_amount",
            "co_sponsor",
        ],
        order_by="date_of_provision desc",
        limit=3,
    )

    return [format_project_grant(g) for g in grants]


def get_recent_event_grants():
    grants = frappe.db.get_all(
        EVENT_GRANTS,
        filters={"grant_status": APPROVED_STATUS},
        fields=[
            "event_name",
            "event_website",
            "application_details",
            "event_start_date",
            "grant_amount",
            "custom_amount",
            "event_organiser",
        ],
        order_by="event_start_date desc",
        limit=3,
    )

    return [format_event_grant(g) for g in grants]


def format_project_grant(grant):
    return {
        "name": grant.project_name,
        "url": grant.project_website,
        "description": grant.about_project,
        "year": grant.date_of_provision.year if grant.date_of_provision else None,
        "amount": grant.grant_amount or "N/A",
        "co_sponsor": grant.co_sponsor,
    }


def format_event_grant(grant):
    return {
        "name": grant.event_name,
        "url": grant.event_website,
        "description": grant.application_details or "Event grant for FOSS community.",
        "year": grant.event_start_date.year if grant.event_start_date else None,
        "date": (grant.event_start_date.strftime("%d %b %Y") if grant.event_start_date else None),
        "amount": (
            grant.custom_amount if grant.grant_amount == "Custom" else grant.grant_amount or "N/A"
        ),
        "co_sponsor": grant.event_organiser,
    }
