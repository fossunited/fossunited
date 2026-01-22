import re

import frappe
from frappe.utils import flt, fmt_money

from fossunited.doctype_ids import EVENT_GRANTS
from fossunited.www.grants.index import format_event_grant, group_grants_by_year


def get_context(context):
    """Event grants detail page"""

    # Fetch all approved event grants
    grants = frappe.db.get_all(
        EVENT_GRANTS,
        filters={"grant_status": "Approved"},
        fields=[
            "event_name",
            "event_website",
            "event_description",
            "event_start_date",
            "grant_amount",
            "custom_amount",
            "event_organiser",
        ],
        order_by="event_start_date desc",
    )

    context.grants_by_year = group_grants_by_year(
        grants,
        formatter=format_event_grant,
    )
    context.total_grants = len(grants)

    total_amount = sum(
        flt(
            re.sub(
                r"[^\d]",
                "",
                (grant.custom_amount if grant.grant_amount == "Custom" else grant.grant_amount)
                or "0",
            )
        )
        for grant in grants
    )

    context.total_amount = fmt_money(total_amount, precision=0, currency="INR")

    # Page metadata
    context.grant_type = "Event Grants"
    context.grant_icon = "ti ti-building-circus"
    context.grant_description = """Our grants program provide financial support to FOSS events.
    To avail an event grant, write to us with a proposal on the event specifics like goals,
    target audience, support links and documents etc."""
    context.no_cache = 1

    return context
