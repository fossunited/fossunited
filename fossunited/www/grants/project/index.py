import frappe

from fossunited.doctype_ids import PROJ_GRANTS
from fossunited.www.grants.index import format_project_grant, group_grants_by_year


def get_context(context):
    """Project grants detail page"""

    # Fetch all approved project grants
    grants = frappe.db.get_all(
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

    context.grants_by_year = group_grants_by_year(
        grants,
        formatter=format_project_grant,
    )
    context.total_grants = len(grants)

    # Page metadata
    context.grant_type = "Project Grants"
    context.grant_icon = "ti ti-device-imac-code"
    context.grant_description = """We fund FOSS projects by raising funds from the tech industry,
    either through our Industry Partnership Program or
    by reaching out to them upon receiving requests from FOSS projects/organizations."""

    return context
