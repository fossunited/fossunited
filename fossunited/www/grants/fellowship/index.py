from collections import defaultdict

import frappe


def get_context(context):
    """Fellowship grants detail page"""

    # Fetch all approved fellowship grants
    grants = frappe.db.get_all(
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
    )

    # Group by year
    grants_by_year = defaultdict(list)
    for grant in grants:
        if grant.date_of_provision:
            year = grant.date_of_provision.year
            grants_by_year[year].append(
                {
                    "name": grant.project_name,
                    "url": grant.project_website,
                    "description": grant.about_project,
                    "year": year,
                    "amount": grant.grant_amount or "N/A",
                    "co_sponsor": grant.co_sponsor,
                }
            )

    # Convert defaultdict to regular dict and sort by year
    context.grants_by_year = dict(sorted(grants_by_year.items(), reverse=True))

    # Page metadata
    context.grant_type = "Fellowship"
    context.grant_icon = "ti ti-heart-handshake"
    context.grant_description = """Fellowship grants support individuals contributing to
    FOSS projects and communities. These grants help developers, students,
    and community organizers dedicate time to open source work."""
    return context
