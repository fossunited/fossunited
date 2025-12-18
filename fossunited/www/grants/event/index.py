from collections import defaultdict

import frappe


def get_context(context):
    """Event grants detail page"""

    # Fetch all approved event grants
    grants = frappe.db.get_all(
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
    )

    # Group by year
    grants_by_year = defaultdict(list)
    for grant in grants:
        if grant.event_start_date:
            year = grant.event_start_date.year

            # Determine actual grant amount
            amount = grant.custom_amount if grant.grant_amount == "Custom" else grant.grant_amount

            # Format date as "DD Mon YYYY" (e.g., "15 Dec 2025")
            formatted_date = grant.event_start_date.strftime("%d %b %Y")

            grants_by_year[year].append(
                {
                    "name": grant.event_name,
                    "url": grant.event_website,
                    "description": grant.application_details or "Event grant for FOSS community.",
                    "year": year,
                    "date": formatted_date,  # Add formatted date
                    "amount": amount or "N/A",
                    "co_sponsor": grant.event_organiser,
                }
            )

    # Convert defaultdict to regular dict and sort by year
    context.grants_by_year = dict(sorted(grants_by_year.items(), reverse=True))

    # Page metadata
    context.grant_type = "Event"
    context.grant_icon = "ti ti-building-circus"
    context.grant_description = """Our grants program provide financial support to FOSS events.
    To avail an event grant, write to us with a proposal on the event specifics like goals,
    target audience, support links and documents etc."""

    return context
