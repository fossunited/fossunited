from frappe.utils import fmt_money

from fossunited.www.grants.index import (
    fetch_event_grants,
    format_event_grant,
    group_grants_by_year,
)


def get_context(context):
    """Event grants detail page"""

    # Fetch all approved event grants
    grants = fetch_event_grants()

    context.grants_by_year = group_grants_by_year(
        grants,
        formatter=format_event_grant,
    )
    context.total_grants = len(grants)

    total_amount = sum(grant.grant_amount for grant in grants)
    context.total_amount = fmt_money(total_amount, precision=0, currency="INR")

    # Page metadata
    context.grant_type = "Event Grants"
    context.grant_icon = "ti ti-building-circus"
    context.grant_description = """Our grants program provide financial support to FOSS events.
    To avail an event grant, write to us with a proposal on the event specifics like goals,
    target audience, support links and documents etc."""
    context.no_cache = 1

    return context
