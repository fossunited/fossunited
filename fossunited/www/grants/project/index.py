from collections import defaultdict

import frappe


def get_context(context):
    """Project grants detail page"""

    # Fetch all approved project grants
    grants = frappe.db.get_all(
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
                    "year": grant.date_of_provision.year,
                    "amount": grant.grant_amount or "N/A",
                    "co_sponsor": grant.co_sponsor,
                }
            )

    # Convert defaultdict to regular dict and sort by year
    context.grants_by_year = dict(sorted(grants_by_year.items(), reverse=True))

    # Page metadata
    context.grant_type = "Project"
    context.grant_icon = "ti ti-device-imac-code"
    context.grant_description = """We fund FOSS projects by raising funds from the tech industry,
    either through our Industry Partnership Program or
    by reaching out to them upon receiving requests from FOSS projects/organizations."""

    return context
