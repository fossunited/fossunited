import frappe

from fossunited.doctype_ids import EVENT_GRANTS, PROJ_GRANTS
from fossunited.www.grants.index import (
    format_event_grant,
    format_project_grant,
    group_grants_by_year,
)


def get_context(context):
    """Get combined grantees"""

    all_grants = []

    project_grants = frappe.db.get_all(
        PROJ_GRANTS,
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

    fellowship_grants = frappe.db.get_all(
        PROJ_GRANTS,
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

    event_grants = frappe.db.get_all(
        EVENT_GRANTS,
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

    for grant in project_grants:
        all_grants.append(
            format_project_grant(
                grant,
                grant_type="Project",
            )
        )

    for grant in event_grants:
        all_grants.append(
            format_event_grant(
                grant,
                grant_type="Event",
            )
        )

    for grant in fellowship_grants:
        all_grants.append(
            format_project_grant(
                grant,
                grant_type="Fellowship",
            )
        )

    context.grants_by_year = group_grants_by_year(
        all_grants,
        formatter=lambda x: x,
    )

    context.all_grants = all_grants
    context.all_grants_json = frappe.as_json(all_grants)

    # Page metadata
    context.grant_type = "All Grants"
    context.grant_icon = "ti ti-list-search"
    context.grant_description = (
        """Browse all FOSS United grantees disbursed for Projects, Events, and Fellowships."""
    )

    return context
