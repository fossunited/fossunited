"""
APIs for Tickets and Transfer Tickets
"""

import frappe

from fossunited.api.chapter import check_if_chapter_member


@frappe.whitelist(allow_guest=True)
def check_ticket_validity(ticket_id: str):
    """
    Check if the ticket is valid or not
    """
    is_ticket_valid = frappe.db.exists("FOSS Event Ticket", ticket_id)

    return bool(is_ticket_valid)


@frappe.whitelist(allow_guest=True)
def get_ticket_details(ticket_id: str):
    """
    Get the event for the ticket
    """
    ticket = frappe.db.get_value(
        "FOSS Event Ticket",
        ticket_id,
        ["event", "tier", "wants_tshirt", "tshirt_size"],
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
            "doctype": "FOSS Event Ticket Transfer",
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


@frappe.whitelist()
def get_transfer_doc_validity(transfer_id: str):
    """
    Check the validity of transfer doc/id
    """
    is_valid_id = frappe.db.exists("FOSS Event Ticket Transfer", transfer_id)

    return bool(is_valid_id)


@frappe.whitelist()
def get_transfer_details(id: str):
    """
    Get the transfer doc
    """
    doc = frappe.db.get_value(
        "FOSS Event Ticket Transfer",
        id,
        ["name", "status", "ticket"],
        as_dict=True,
    )
    return doc


@frappe.whitelist()
def change_transfer_status(transfer_id: str, status: str):
    """
    Change the status of the transfer request
    """
    doc = frappe.get_doc("FOSS Event Ticket Transfer", transfer_id)
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
    total_sold = frappe.db.count("FOSS Event Ticket", filters={"event": event_id})

    # Get the insights of the t-shirts
    tshirt_insights = get_tshirt_insights(event_id)

    # Get the percentage of increase or decrease in the tickets sold compared to till previous day
    tickets_sold_today = frappe.db.count(
        "FOSS Event Ticket",
        filters={
            "event": event_id,
            "creation": ["like", f"{frappe.utils.nowdate()}%"],
        },
    )
    tickets_sold_yesterday = frappe.db.count(
        "FOSS Event Ticket",
        filters={
            "event": event_id,
            "creation": [
                "like",
                f"{frappe.utils.add_days(frappe.utils.nowdate(), -1)}%",
            ],
        },
    )

    percentage_change = get_percentage_change(float(tickets_sold_today), float(tickets_sold_yesterday))

    tier_data = {}

    # Get the tickets insights for each tier
    tiers = frappe.db.get_all(
        "FOSS Ticket Tier",
        filters={"parent": event_id, "parentfield": "tiers"},
        fields=["*"],
    )
    for tier in tiers:
        tier_data[tier.title] = get_tier_insights(tier)

    return {
        "total_sold": total_sold,
        "tshirt_insights": tshirt_insights,
        "tickets_sold_today": tickets_sold_today,
        "total_percentage_change": percentage_change,
        "tier_data": tier_data,
    }


def get_tshirt_insights(event_id: str) -> dict:
    """
    Get the insights of the t-shirts for the event

    Returns:
        dict: Insights of the t-shirts
    """
    tshirts_sold = frappe.db.count(
        "FOSS Event Ticket",
        filters={"event": event_id, "wants_tshirt": 1},
    )

    # Group tshirts sold by size
    tshirt_sizes = frappe.db.get_all(
        "FOSS Event Ticket",
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
        "FOSS Event Ticket",
        filters={"event": tier.parent, "tier": tier.title},
    )
    stats["tickets_sold_today"] = frappe.db.count(
        "FOSS Event Ticket",
        filters={
            "event": tier.parent,
            "tier": tier.title,
            "creation": ["like", f"{frappe.utils.nowdate()}%"],
        },
    )
    stats["tickets_sold_yesterday"] = frappe.db.count(
        "FOSS Event Ticket",
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
def get_sold_tickets(event_id: str, filters: dict = {}) -> list:
    """
    Get the list of all tickets sold for the event.

    Args:
        event_id (str): Event ID

    Returns:
        list: List of tickets sold for the event
    """

    if not has_valid_permission(event_id):
        frappe.throw("You are not authorized to view the tickets for this event")
    print("Filters: ", filters)
    tickets = frappe.db.get_all(
        "FOSS Event Ticket",
        filters={"event": event_id, **filters},
        fields=[
            "tier",
            "wants_tshirt",
            "tshirt_size",
            "event",
            "full_name",
            "designation",
            "organization",
            "is_transfer_ticket",
        ],
        order_by="creation",
    )
    return tickets


def has_valid_permission(event_id: str) -> bool:
    """
    Check if the user has valid permission to view the tickets for the event

    Args:
        event_id (str): Event ID

    Returns:
        bool: True if the user has valid permission, False otherwise
    """
    session_user = frappe.session.user

    if not (
        bool(
            frappe.db.exists(
                "Has Role",
                {
                    "role": "Chapter Lead",
                    "parent": session_user,
                },
            )
        )
    ):
        return False

    chapter_id = frappe.db.get_value("FOSS Chapter Event", event_id, ["chapter"])
    if not check_if_chapter_member(chapter_id, session_user):
        return False

    return True


@frappe.whitelist()
def get_ticket_tiers(event_id: str) -> list:
    """
    Get the list of ticket tiers for the event

    Args:
        event_id (str): Event ID

    Returns:
        list: List of ticket tiers
    """
    tiers = frappe.db.get_all(
        "FOSS Ticket Tier",
        filters={"parent": event_id, "parentfield": "tiers"},
        fields=["title", "maximum_tickets"],
    )
    return tiers
