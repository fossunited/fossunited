import frappe


def get_context(context):
    """Main grants landing page with card data"""

    # Get counts for each grant type
    project_completed = frappe.db.count(
        "FOSS Project Grant", {"grant_status": "Approved", "grant_type": "Project"}
    )
    project_pending = frappe.db.count(
        "FOSS Project Grant",
        {"grant_status": ["in", ["Open", "Under Review"]], "grant_type": "Project"},
    )

    fellowship_completed = frappe.db.count(
        "FOSS Project Grant", {"grant_status": "Approved", "grant_type": "Fellowship"}
    )
    fellowship_pending = frappe.db.count(
        "FOSS Project Grant",
        {"grant_status": ["in", ["Open", "Under Review"]], "grant_type": "Fellowship"},
    )

    event_completed = frappe.db.count("FOSS Event Grant", {"grant_status": "Approved"})
    event_pending = frappe.db.count(
        "FOSS Event Grant", {"grant_status": ["in", ["Open", "Under Review"]]}
    )

    # Build grant types list for the macro
    context.grant_types = [
        {
            "title": "Project Grants",
            "icon": "ti ti-device-imac-code",
            "description": """We fund FOSS projects by raising funds from the tech industry,
            either through our Industry Partnership Program or
            by reaching out to them upon receiving requests from FOSS projects/organizations.""",
            "route": "/grants/project",
            "completed": project_completed,
            "pending": project_pending,
        },
        {
            "title": "Event Grants",
            "icon": "ti ti-building-circus",
            "description": """Our grants program provide financial support to FOSS events.
            To avail an event grant, write to us with a proposal on the event specifics like goals,
            target audience, support links and documents etc.""",
            "route": "/grants/event",
            "completed": event_completed,
            "pending": event_pending,
        },
        {
            "title": "Fellowship Grants",
            "icon": "ti ti-heart-handshake",
            "description": """Fellowship grants support individuals contributing to
            FOSS projects and communities. These grants help developers, students,
            and community organizers dedicate time to open source work.""",
            "route": "/grants/fellowship",
            "completed": fellowship_completed,
            "pending": fellowship_pending,
        },
    ]

    project_grants = frappe.db.get_all(
        "FOSS Project Grant",
        filters={"grant_status": "Approved", "grant_type": "Project"},
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

    event_grants = frappe.db.get_all(
        "FOSS Event Grant",
        filters={"grant_status": "Approved"},
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

    fellowship_grants = frappe.db.get_all(
        "FOSS Project Grant",
        filters={"grant_status": "Approved", "grant_type": "Fellowship"},
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

    context.recent_project_grants = [format_project_grant(g) for g in project_grants]
    context.recent_event_grants = [format_event_grant(g) for g in event_grants]
    context.recent_fellowship_grants = [format_project_grant(g) for g in fellowship_grants]

    return context


def format_project_grant(grant):
    """Format project/fellowship grant for render"""
    return {
        "name": grant.project_name,
        "url": grant.project_website,
        "description": grant.about_project,
        "year": grant.date_of_provision.year if grant.date_of_provision else None,
        "amount": grant.grant_amount or "N/A",
        "co_sponsor": grant.co_sponsor,
    }


def format_event_grant(grant):
    """Format event grant for render"""
    return {
        "name": grant.event_name,
        "url": grant.event_website,
        "description": grant.application_details or "Event grant for FOSS community.",
        "year": grant.event_start_date.year if grant.event_start_date else None,
        "date": grant.event_start_date.strftime("%d %b %Y") if grant.event_start_date else None,
        "amount": grant.custom_amount
        if grant.grant_amount == "Custom"
        else grant.grant_amount or "N/A",
        "co_sponsor": grant.event_organiser,
    }
