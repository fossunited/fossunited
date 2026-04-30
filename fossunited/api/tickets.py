"""
APIs for Tickets and Transfer Tickets
"""

from datetime import timedelta

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_days, now_datetime

from fossunited.api.chapter import check_if_chapter_member
from fossunited.doctype_ids import (
    EVENT,
    EVENT_CHECKIN,
    EVENT_TICKET,
    FREE_TICKET_APPLY,
    FREE_TICKET_CODE,
    RAZORPAY_PAYMENT,
    TICKET_TRANSFER,
)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60 * 12)
def check_ticket_validity(ticket_id: str):
    """
    Check if the ticket is valid or not
    """
    is_ticket_valid = frappe.db.exists(EVENT_TICKET, ticket_id)

    return bool(is_ticket_valid)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=2, seconds=60 * 60 * 12)
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=3, seconds=60 * 60 * 12)
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_transfer_doc_validity(transfer_id: str):
    """
    Check the validity of transfer doc/id
    """
    is_valid_id = frappe.db.exists(TICKET_TRANSFER, transfer_id)

    return bool(is_valid_id)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=4, seconds=60 * 60 * 12)
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=3, seconds=60 * 60 * 12)
def change_transfer_status(transfer_id: str, status: str):
    """
    Change the status of the transfer request
    """
    if frappe.session.user == "Guest":
        frappe.throw(
            _("Please login with your FOSS United account to process this transfer"),
            frappe.AuthenticationError,
        )

    doc = frappe.get_doc(TICKET_TRANSFER, transfer_id)
    ticket = frappe.get_doc(EVENT_TICKET, doc.ticket)
    if frappe.session.user not in [ticket.email, doc.receiver_email]:
        frappe.throw(
            _("You are not authorized to modify this transfer"),
            frappe.PermissionError,
        )

    if status not in ["Completed", "Cancelled"]:
        frappe.throw(_("Invalid status provided for ticket transfer"))

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


@frappe.whitelist()
def get_checkin_insights(event_id: str) -> dict:
    """
    Get check-in counts for each day from event start to end date

    Returns:
        dict: {"daily_data": [{"title": date, "total_sold": count, "tickets_sold_today": 0}, ...]}
    """
    event_start_date, event_end_date = frappe.db.get_value(
        EVENT, event_id, ["event_start_date", "event_end_date"]
    )

    # Get all tickets for this event
    tickets = frappe.get_all(EVENT_TICKET, filters={"event": event_id}, pluck="name")

    if not tickets:
        return {"daily_data": []}

    start_date = frappe.utils.get_datetime(event_start_date).date()
    end_date = frappe.utils.get_datetime(event_end_date).date()

    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        count = frappe.db.count(
            EVENT_CHECKIN,
            filters={
                "parent": ["in", tickets],
                "parenttype": EVENT_TICKET,
                "parentfield": "check_ins",
                "check_in_time": [
                    "between",
                    [f"{date_str} 00:00:00", f"{date_str} 23:59:59"],
                ],
            },
        )
        daily_data.append(
            {
                "title": frappe.utils.formatdate(date_str, "dd MMM"),
                "total_sold": count,  # Using total_sold to match checked-in
            }
        )
        current_date += timedelta(days=1)

    return {"daily_data": daily_data}


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
def get_tickets_with_custom_fields(event_id: str) -> list:
    """
    Get all tickets with their custom field answers merged as dynamic fields.

    Args:
        event_id (str): Event ID
        filters (dict): Additional filters for tickets

    Returns:
        dict: Dictionary containing tickets list and custom field names
    """
    if not has_valid_permission(event_id):
        frappe.throw(_("You are not authorized to view the tickets for this event"))

    from frappe.query_builder import DocType
    from frappe.query_builder.functions import Coalesce

    tickets = DocType(EVENT_TICKET)
    custom = DocType("FOSS Ticket Custom Field")

    results = (
        frappe.qb.from_(tickets)
        .left_join(custom)
        .on(
            (custom.parent == tickets.name)
            & (custom.parenttype == EVENT_TICKET)
            & (custom.parentfield == "custom_fields")
        )
        .select(
            tickets.name,
            tickets.tier,
            tickets.full_name,
            tickets.organization,
            tickets.designation,
            tickets.wants_tshirt,
            tickets.tshirt_size,
            Coalesce(custom.field_name, "").as_("question"),
            Coalesce(custom.data, "").as_("response"),
        )
        .where(tickets.event == event_id)
        .orderby(tickets.creation)
        .orderby(custom.idx)
    ).run(as_dict=True)

    if not results:
        return []

    # flatten the structure
    # the raw results will have dup items with each custom fields
    tickets_map = {}
    for row in results:
        ticket_id = row["name"]
        if ticket_id not in tickets_map:
            tickets_map[ticket_id] = {
                k: v for k, v in row.items() if k not in ("question", "response", "name")
            }
        if row["question"]:
            tickets_map[ticket_id][row["question"]] = row["response"] or ""

    return list(tickets_map.values())


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


# nosemgrep: guest-whitelisted-method
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
def get_event_free_codes(event: str):
    """Get all free ticket codes for an event"""

    if not has_valid_permission(event):
        frappe.throw(_("You are not authorized to view the tickets for this event"))

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


# nosemgrep: guest-whitelisted-method
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


# should be defensive with rate limit and we only allow based on IDs
# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60 * 10)
def search_tickets(search_term: str, event: str | None = None) -> dict:
    """
    Search tickets by ticket_id, Razorpay order_id, or coupon code.

    Rate limit: 10 requests per 3 hours per IP

    Args:
        search_term (str): Ticket ID, Razorpay order ID, or coupon code
        event (str, optional): Unused — kept for backwards compatibility

    Returns:
        list: List of ticket dictionaries

    Raises:
        ValidationError: If search_term is empty
        RateLimitExceededError: If rate limit is exceeded
    """
    if not search_term:
        frappe.throw(_("Search term is required"))

    search_term = search_term.strip()

    # Direct ticket ID lookup
    if frappe.db.exists(EVENT_TICKET, search_term):
        return [get_ticket_details(search_term)]

    # Razorpay order ID lookup — order IDs are hard to guess (not enumerable)
    payment_name = frappe.db.get_value(RAZORPAY_PAYMENT, {"order_id": search_term}, "name")
    if payment_name:
        return frappe.get_all(
            EVENT_TICKET,
            filters={"razorpay_payment": payment_name},
            fields=["name", "full_name", "email", "tier", "organization"],
            order_by="full_name",
        )

    # Coupon-based search
    coupon_event = frappe.db.get_value(FREE_TICKET_CODE, search_term, "event")
    if not coupon_event:
        return []

    # Get all emails that applied with this coupon
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


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60 * 5)
def download_ticket(ticket_id: str):
    """
    Download single ticket PDF.

    Rate limit: 5 requests per 5 hours per IP

    Args:
        ticket_id (str): ID of the ticket to download

    Raises:
        ValidationError: If ticket doesn't exist
        RateLimitExceededError: If rate limit is exceeded
    """
    if not frappe.db.exists(EVENT_TICKET, ticket_id):
        frappe.throw(_("Ticket not found"))

    frappe.local.flags.ignore_print_permissions = True

    pdf_file = frappe.get_print(
        EVENT_TICKET,
        ticket_id,
        "[Designer] Event Ticket",
        no_letterhead=1,
        as_pdf=True,
    )

    frappe.local.response.filename = "event-ticket.pdf"
    frappe.local.response.filecontent = pdf_file
    frappe.local.response.type = "download"


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=3, seconds=60 * 60 * 12)
def download_all_tickets(ticket_ids: str | list):
    """
    Download multiple tickets as single PDF.

    Rate limit: 3 requests per 12 hours per IP
    (Lower limit due to higher resource usage)

    Args:
        ticket_ids (str|list): JSON string or list of ticket IDs

    Raises:
        ValidationError: If no tickets provided or invalid format
        RateLimitExceededError: If rate limit is exceeded
    """
    import json

    if isinstance(ticket_ids, str):
        try:
            ticket_ids = json.loads(ticket_ids)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid ticket IDs format"))

    if not ticket_ids or not isinstance(ticket_ids, list):
        frappe.throw(_("No tickets provided"))

    from frappe.utils.print_format import download_multi_pdf

    frappe.local.flags.ignore_print_permissions = True

    download_multi_pdf(
        doctype=EVENT_TICKET,
        name=json.dumps(ticket_ids),
        format="[Designer] Event Ticket",
        no_letterhead=True,
    )
    frappe.local.response.type = "download"
