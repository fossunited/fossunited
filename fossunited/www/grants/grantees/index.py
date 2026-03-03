from frappe.utils import fmt_money

from fossunited.www.grants.index import (
    fetch_event_grants,
    fetch_fellowship_grants,
    fetch_project_grants,
    format_event_grant,
    format_project_grant,
    group_grants_by_year,
)


def get_context(context):
    """Get combined grantees"""

    all_grants = []

    project_grants = fetch_project_grants()
    fellowship_grants = fetch_fellowship_grants()
    event_grants = fetch_event_grants()

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
    context.total_grants = len(all_grants)
    total_amount = sum(grant["grant_amount"] for grant in all_grants)
    context.total_amount = fmt_money(total_amount, precision=0, currency="INR")

    # Page metadata
    context.grant_type = "All Grantees"
    context.grant_icon = "ti ti-report-search"
    context.grant_description = """
    Browse all FOSS United grantees disbursed for Projects, Events, and Fellowships."""
    context.no_cache = 1

    return context
