import frappe

from fossunited.doctype_ids import PROJ_GRANTS
from fossunited.www.grants.index import (
    APPROVED_STATUS,
    format_project_grant,
    group_grants_by_year,
)


def get_context(context):
    """Fellowship grants detail page"""

    # Fetch all approved fellowship grants
    grants = frappe.db.get_all(
        PROJ_GRANTS,
        filters={"grant_status": ["in", APPROVED_STATUS], "grant_type": "Fellowship"},
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
    context.grant_type = "Fellowships"
    context.grant_icon = "ti ti-heart-handshake"
    context.grant_description = """Fellowship grants support individuals contributing to
    FOSS projects and communities. These grants help developers, students,
    and community organizers dedicate time to open source work."""
    context.no_cache = 1

    return context
