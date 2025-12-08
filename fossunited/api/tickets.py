"""
APIs for Tickets and Transfer Tickets
"""

import frappe
from frappe.utils import add_days, now_datetime

from fossunited.api.chapter import check_if_chapter_member
from fossunited.doctype_ids import (
    EVENT,
    EVENT_TICKET,
    FREE_TICKET_APPLY,
    FREE_TICKET_CODE,
    TICKET_TRANSFER,
)


@frappe.whitelist(allow_guest=True)
def check_ticket_validity(ticket_id: str):
    """
    Check if the ticket is valid or not
    """
    is_ticket_valid = frappe.db.exists(EVENT_TICKET, ticket_id)

    return bool(is_ticket_valid)


@frappe.whitelist(allow_guest=True)
def get_ticket_details(ticket_id: str):
    """
    Get the event for the ticket
    """
    ticket = frappe.db.get_value(
        EVENT_TICKET,
        ticket_id,
        ["*"],
        as_dict=True,
    )
    return ticket


@frappe.whitelist(allow_guest=True)
def create_transfer_request(ticket: str, receiver_details: dict):
    """
    Create a transfer request for the ticket
    """
    transfer_request = frappe.get_doc(
        {
            "doctype": TICKET_TRANSFER,
            "ticket": ticket,
            "receiver_name": receiver_details.get("receiver_name"),
            "receiver_email": receiver_details.get("receiver_email"),
            "designation": receiver_details.get("designation"),
            "organization": receiver_details.get("organization"),
            "wants_tshirt": receiver_details.get("wants_tshirt"),
            "tshirt_size": receiver_details.get("tshirt_size"),
            "status": "Pending Approval",
        }
    )
    transfer_request.insert(ignore_permissions=True)
    return transfer_request


@frappe.whitelist(allow_guest=True)
def get_transfer_doc_validity(transfer_id: str):
    """
    Check the validity of transfer doc/id
    """
    is_valid_id = frappe.db.exists(TICKET_TRANSFER, transfer_id)

    return bool(is_valid_id)


@frappe.whitelist(allow_guest=True)
def get_transfer_details(id: str):
    """
    Get the transfer doc
    """
    doc = frappe.db.get_value(
        TICKET_TRANSFER,
        id,
        ["name", "status", "ticket"],
        as_dict=True,
    )
    return doc


@frappe.whitelist(allow_guest=True)
def change_transfer_status(transfer_id: str, status: str):
    """
    Change the status of the transfer request
    """
    doc = frappe.get_doc(TICKET_TRANSFER, transfer_id)
    doc.status = status
    doc.save()
    return True


@frappe.whitelist()
def get_tickets_insights(event_id: str) -> dict:
    """
    Get the insights of the tickets for the event

    Returns:
        dict: Insights of the tickets
    """
    total_sold = frappe.db.count(EVENT_TICKET, filters={"event": event_id})

    # Get the insights of the t-shirts
    tshirt_insights = get_tshirt_insights(event_id)

    # Get the percentage of increase or decrease in the tickets sold compared to till previous day
    tickets_sold_today = frappe.db.count(
        EVENT_TICKET,
        filters={
            "event": event_id,
            "creation": ["like", f"{frappe.utils.nowdate()}%"],
        },
    )
    tickets_sold_yesterday = frappe.db.count(
        EVENT_TICKET,
        filters={
            "event": event_id,
            "creation": [
                "like",
                f"{frappe.utils.add_days(frappe.utils.nowdate(), -1)}%",
            ],
        },
    )

    percentage_change = get_percentage_change(
        float(tickets_sold_today), float(tickets_sold_yesterday)
    )

    tier_data = {}

    # Get the tickets insights for each tier
    tiers = frappe.db.get_all(
        "FOSS Ticket Tier",
        filters={"parent": event_id, "parentfield": "tiers"},
        fields=["*"],
    )

    for tier in tiers:
        tier_data[tier.title] = get_tier_insights(tier)

    combined_tier_data = list(tier_data.values())
    free_pass_data = get_free_pass_insights(event_id)
    if free_pass_data:
        combined_tier_data.append(free_pass_data)

    return {
        "total_sold": total_sold,
        "tshirt_insights": tshirt_insights,
        "tickets_sold_today": tickets_sold_today,
        "total_percentage_change": percentage_change,
        "tier_data": combined_tier_data,
    }


def get_tshirt_insights(event_id: str) -> dict:
    """
    Get the insights of the t-shirts for the event

    Returns:
        dict: Insights of the t-shirts
    """
    tshirts_sold = frappe.db.count(
        EVENT_TICKET,
        filters={"event": event_id, "wants_tshirt": 1},
    )

    # Group tshirts sold by size
    tshirt_sizes = frappe.db.get_all(
        EVENT_TICKET,
        filters={"event": event_id, "wants_tshirt": 1},
        fields=["tshirt_size"],
    )
    tshirt_sizes = [size.tshirt_size for size in tshirt_sizes]

    tshirt_size_count = {}
    for size in tshirt_sizes:
        tshirt_size_count[size] = tshirt_size_count.get(size, 0) + 1

    return {
        "tshirts_sold": tshirts_sold,
        "tshirt_size_count": tshirt_size_count,
    }


def get_tier_insights(tier: dict) -> dict:
    """
    Get the insights of the tickets for the tier
    """
    stats = {}
    stats["title"] = tier.title
    stats["total_sold"] = frappe.db.count(
        EVENT_TICKET,
        filters={"event": tier.parent, "tier": tier.title},
    )
    stats["tickets_sold_today"] = frappe.db.count(
        EVENT_TICKET,
        filters={
            "event": tier.parent,
            "tier": tier.title,
            "creation": ["like", f"{frappe.utils.nowdate()}%"],
        },
    )
    stats["tickets_sold_yesterday"] = frappe.db.count(
        EVENT_TICKET,
        filters={
            "event": tier.parent,
            "tier": tier.title,
            "creation": [
                "like",
                f"{frappe.utils.add_days(frappe.utils.nowdate(), -1)}%",
            ],
        },
    )

    stats["percentage_change"] = get_percentage_change(
        float(stats["tickets_sold_today"]),
        float(stats["tickets_sold_yesterday"]),
    )
    stats["tier_capacity"] = tier.maximum_tickets

    return stats


def get_percentage_change(today: float, yesterday: float) -> float:
    """
    Get the percentage change between today and yesterday
    """

    if yesterday > 0:
        percentage_change = ((today - yesterday) / yesterday) * 100
    elif today > 0:
        percentage_change = ((today - yesterday) / 1) * 100
    else:
        percentage_change = 0.0

    percentage_change = max(percentage_change, 0.0)

    return percentage_change


@frappe.whitelist()
def get_tickets_with_custom_fields(event_id: str, filters: dict | None = None) -> dict:
    """
    Get all tickets with their custom field answers merged as dynamic fields.

    Args:
        event_id (str): Event ID
        filters (dict): Additional filters for tickets

    Returns:
        dict: Dictionary containing tickets list and custom field names
    """
    if not has_valid_permission(event_id):
        frappe.throw("You are not authorized to view the tickets for this event")

    if filters is None:
        filters = {}

    tickets = frappe.get_all(
        EVENT_TICKET,
        filters={"event": event_id, **filters},
        fields=[
            "name",
            "tier",
            "wants_tshirt",
            "tshirt_size",
            "event",
            "full_name",
            "email",
            "designation",
            "organization",
            "is_transfer_ticket",
        ],
        order_by="creation",
    )

    if not tickets:
        return {"tickets": [], "custom_fields": []}

    ticket_ids = [t["name"] for t in tickets]

    custom_fields = frappe.get_all(
        "FOSS Ticket Custom Field",
        filters={
            "parent": ["in", ticket_ids],
            "parenttype": EVENT_TICKET,
            "parentfield": "custom_fields",
        },
        fields=["parent", "field_name", "data"],
        order_by="parent asc, idx asc",
    )
    custom_field_names = list(dict.fromkeys([f["field_name"] for f in custom_fields]))

    # Group custom fields by parent (ticket)
    custom_fields_map = {}
    for field in custom_fields:
        parent = field["parent"]
        if parent not in custom_fields_map:
            custom_fields_map[parent] = {}

        # Use field_name as key, data as value
        field_name = field["field_name"] or "unknown_field"
        custom_fields_map[parent][f"custom_field_{field_name}"] = field["data"] or ""

    # Merge custom fields into tickets
    for ticket in tickets:
        ticket_id = ticket["name"]
        if ticket_id in custom_fields_map:
            ticket.update(custom_fields_map[ticket_id])

    return {"tickets": tickets, "custom_fields": custom_field_names}


def has_valid_permission(event_id: str) -> bool:
    """
    Check if the user has valid permission to view the tickets for the event

    Args:
        event_id (str): Event ID

    Returns:
        bool: True if the user has valid permission, False otherwise
    """
    session_user = frappe.session.user

    # Allow if user has "Chapter Team Member" role AND is a member of the chapter
    if frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": session_user}):
        chapter_id = frappe.db.get_value(EVENT, event_id, "chapter")
        if chapter_id and check_if_chapter_member(chapter_id, session_user):
            return True

    # Allow if user is listed as an event member
    if frappe.db.exists(
        "FOSS Chapter Event Member",
        {
            "parent": event_id,
            "parenttype": EVENT,
            "email": session_user,
        },
    ):
        return True

    return False


@frappe.whitelist()
def get_ticket_tiers(event_id: str) -> list:
    """
    Get the list of ticket tiers for the event,
    including any manually created 'Free pass' tickets (like Speaker/Volunteer passes).
    """
    # Get all real tiers from FOSS Ticket Tier child table
    tiers = frappe.db.get_all(
        "FOSS Ticket Tier",
        filters={"parent": event_id, "parentfield": "tiers"},
        fields=["title", "maximum_tickets"],
    )

    # Check if there are tickets whose tier name contains 'Free pass'
    has_free_pass = frappe.db.exists(
        "FOSS Event Ticket",
        {
            "event": event_id,
            "tier": ["like", "%Free pass%"],
        },
    )

    if has_free_pass:
        # Add one virtual entry to represent all free-pass tickets
        tiers.append(
            {
                "title": "Free pass",
                "maximum_tickets": 0,
            }
        )

    return tiers


@frappe.whitelist(allow_guest=True)
def is_ticket_live(event_id: str) -> bool:
    """
    Check if the ticketing for the event is live or not

    Args:
        event_id (str): Event ID

    Returns:
        bool: True if ticketing is live, False otherwise
    """
    ticket_status = frappe.db.get_value(EVENT, event_id, "tickets_status")

    return ticket_status == "Live"


def get_free_pass_insights(event_id: str) -> dict:
    """
    Get total free pass tickets claimed for the event.
    """
    today = frappe.utils.nowdate()
    yesterday = frappe.utils.add_days(today, -1)

    stats = {
        "title": "Free Pass Tickets",
        "total_sold": frappe.db.count(
            EVENT_TICKET,
            filters={
                "event": event_id,
                "tier": ["like", "%Free pass%"],
            },
        ),
        "tickets_sold_today": frappe.db.count(
            EVENT_TICKET,
            filters={
                "event": event_id,
                "tier": ["like", "%Free pass%"],
                "creation": ["like", f"{today}%"],
            },
        ),
        "tickets_sold_yesterday": frappe.db.count(
            EVENT_TICKET,
            filters={
                "event": event_id,
                "tier": ["like", "%Free pass%"],
                "creation": ["like", f"{yesterday}%"],
            },
        ),
    }

    stats["percentage_change"] = get_percentage_change(
        float(stats["tickets_sold_today"]),
        float(stats["tickets_sold_yesterday"]),
    )

    return stats


@frappe.whitelist()
def get_event_free_codes(event):
    """Get all free ticket codes for an event"""

    if not has_valid_permission(event):
        frappe.throw("You are not authorized to view the tickets for this event")

    codes = frappe.get_all(
        FREE_TICKET_CODE,
        filters={"event": event},
        fields=[
            "name",
            "full_name",
            "mapped_email",
            "tier",
            "company",
            "other_tier",
            "used_count",
            "max_count",
            "is_used",
        ],
        order_by="tier asc, creation desc",
    )

    return codes


@frappe.whitelist(allow_guest=True)
def get_paid_events():
    """Get list of paid events for ticket search - Live or recently concluded (within 30 days)"""
    thirty_days_ago = add_days(now_datetime(), -30)

    return frappe.get_all(
        EVENT,
        filters={
            "is_paid_event": 1,
            "status": ["in", ["Live", "Concluded"]],
            "event_end_date": [">=", thirty_days_ago],
        },
        fields=["name", "event_name"],
        order_by="event_end_date desc",
    )


def search_tickets(search_term, event=None):
    """Search tickets by ticket_id, email, or coupon_id"""
    if not search_term:
        frappe.throw("Search term is required")

    search_term = search_term.strip()

    # Email search - requires event
    if "@" in search_term:
        if not event:
            frappe.throw("Please select an event to search by email")

        return frappe.get_all(
            EVENT_TICKET,
            filters={"event": event, "email": search_term},
            fields=["name", "full_name", "email", "tier", "organization"],
            order_by="full_name",
        )

    # Ticket ID - direct lookup, no event needed
    if frappe.db.exists(EVENT_TICKET, search_term):
        return [get_ticket_details(search_term)]

    coupon_event = frappe.db.get_value(FREE_TICKET_CODE, search_term, "event")
    if not coupon_event:
        return []

    coupon_apps = frappe.get_all(
        FREE_TICKET_APPLY,
        filters={"coupon_id": search_term, "event": coupon_event},
        fields=["email"],
        pluck="email",
    )

    if coupon_apps:
        return frappe.get_all(
            EVENT_TICKET,
            filters={"email": ["in", coupon_apps], "event": coupon_event},
            fields=["name", "full_name", "email", "tier", "organization"],
            order_by="full_name",
        )

    return []


@frappe.whitelist()
def download_ticket(ticket_id):
    """Download single ticket PDF"""
    if not frappe.db.exists(EVENT_TICKET, ticket_id):
        frappe.throw("Ticket not found")

    from frappe.utils.print_format import download_pdf

    return download_pdf(
        doctype=EVENT_TICKET,
        name=ticket_id,
        format="[Designer] Event Ticket",
        no_letterhead=1,
    )


@frappe.whitelist()
def download_all_tickets(ticket_ids):
    """Download multiple tickets as single PDF"""
    import json

    if isinstance(ticket_ids, str):
        ticket_ids = json.loads(ticket_ids)

    if not ticket_ids or not isinstance(ticket_ids, list):
        frappe.throw("No tickets provided")

    # Verify all tickets exist
    for ticket_id in ticket_ids:
        if not frappe.db.exists(EVENT_TICKET, ticket_id):
            frappe.throw(f"Ticket {ticket_id} not found")

    from frappe.utils.print_format import download_multi_pdf

    # download_multi_pdf returns the PDF content directly
    download_multi_pdf(
        doctype=EVENT_TICKET,
        name=json.dumps(ticket_ids),
        format="[Designer] Event Ticket",
        no_letterhead=True,
    )
