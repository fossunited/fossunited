from frappe.utils import fmt_money

from fossunited.www.grants.index import (
    fetch_project_grants,
    format_project_grant,
    group_grants_by_year,
)


def get_context(context):
    """Project grants detail page"""

    # Fetch all approved project grants
    grants = fetch_project_grants()

    context.grants_by_year = group_grants_by_year(
        grants,
        formatter=format_project_grant,
    )
    context.total_grants = len(grants)

    total_amount = sum(grant.grant_amount for grant in grants)
    context.total_amount = fmt_money(total_amount, precision=0, currency="INR")

    # Page metadata
    context.grant_type = "Project Grants"
    context.grant_icon = "ti ti-device-imac-code"
    context.grant_description = """We fund FOSS projects by raising funds from the tech industry,
    either through our Industry Partnership Program or
    by reaching out to them upon receiving requests from FOSS projects/organizations."""
    context.no_cache = 1

    return context
