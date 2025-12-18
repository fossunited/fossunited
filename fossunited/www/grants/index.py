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

    return context
