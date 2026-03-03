from frappe.utils import fmt_money

from fossunited.www.grants.index import (
    fetch_fellowship_grants,
    format_project_grant,
    group_grants_by_year,
)


def get_context(context):
    """Fellowship grants detail page"""

    # Fetch all approved fellowship grants
    grants = fetch_fellowship_grants()

    context.grants_by_year = group_grants_by_year(
        grants,
        formatter=format_project_grant,
    )

    context.total_grants = len(grants)

    total_amount = sum(grant.grant_amount for grant in grants)
    context.total_amount = fmt_money(total_amount, precision=0, currency="INR")

    # Page metadata
    context.grant_type = "Fellowships"
    context.grant_icon = "ti ti-heart-handshake"
    context.grant_description = """Fellowship grants support individuals contributing to
    FOSS projects and communities. These grants help developers, students,
    and community organizers dedicate time to open source work."""
    context.no_cache = 1

    return context
