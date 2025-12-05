import frappe

from fossunited.api.tickets import has_valid_permission
from fossunited.doctype_ids import EVENT_TICKET


@frappe.whitelist()
def get_attendee_with_checkin_data(event_id: str, filters: dict = {}) -> dict:
    """
    Get the attendees of the event with their checkin details

    Args:
        event_id (str): The event id
        user (str): The user who is requesting the data

    Returns:
        dict: The attendees of the event with their checkin details
    """
    if not has_valid_permission(event_id):
        frappe.throw("You do not have permission to access this resource", frappe.PermissionError)

    _filters = {"event": event_id}
    # Map the items in filters to be like "key": ["like", value]
    _filters.update({key: ["like", f"%{value}%"] for key, value in filters.items()})

    tickets = frappe.db.get_all(
        EVENT_TICKET,
        _filters,
        [
            "name",
            "full_name",
            "designation",
            "organization",
            "wants_tshirt",
            "tier",
            "tshirt_delivered",
            "tshirt_size",
        ],
    )

    for ticket in tickets:
        ticket["checkin_data"] = get_checkin_data(ticket["name"])

    return tickets


def get_checkin_data(attendee_id: str) -> dict:
    """
    Get the checkin data for the attendee

    Args:
        attendee_id (str): The attendee / ticket id

    Returns:
        dict: The checkin data for the attendee
    """

    checkin_data = frappe.db.get_all(
        "Event Check In",
        {"parent": attendee_id, "parenttype": EVENT_TICKET, "parentfield": "check_ins"},
        ["check_in_time"],
    )

    return checkin_data


@frappe.whitelist()
def checkin_attendee(event_id: str, attendee: dict, assign_tshirt: bool = False):
    """
    Check-in the attendee for the event.

    Args:
        event_id (str): The event ID
        attendee (dict): The attendee details / ticket details
        assign_tshirt (bool): Whether to assign a T-shirt to the attendee
    """
    if not has_valid_permission(event_id):
        frappe.throw("You do not have permission to access this resource", frappe.PermissionError)

    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])

    # Check if already checked in today
    today = frappe.utils.getdate(frappe.utils.now_datetime())
    already_checked_in_today = any(
        frappe.utils.getdate(checkin.check_in_time) == today
        for checkin in ticket.get("check_ins", [])
    )

    if already_checked_in_today:
        if assign_tshirt and ticket.get("wants_tshirt") and not ticket.get("tshirt_delivered"):
            # Only update tshirt_delivered, do not add another check-in
            ticket.tshirt_delivered = True
            ticket.save(ignore_permissions=True)
            return  # Success, exit early
        else:
            frappe.throw("Attendee is already checked in", frappe.ValidationError)

    # Perform full check-in
    ticket.append("check_ins", {"check_in_time": frappe.utils.now()})
    if assign_tshirt:
        ticket.tshirt_delivered = True
    ticket.save(ignore_permissions=True)


@frappe.whitelist()
def undo_attendee_checkin(event_id: str, attendee: dict):
    """
    Undo the check-in for the attendee

    Args:
        attendee (dict): The attendee details / ticket details
        user (str): The user who is undoing the check-in
    """
    if not has_valid_permission(event_id):
        frappe.throw("You do not have permission to access this resource", frappe.PermissionError)

    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])
    ticket.check_ins.pop()
    ticket.save(ignore_permissions=True)


@frappe.whitelist()
def assign_tshirt(event_id: str, attendee: dict):
    """
    Assign Tshirt to the attendee

    Args:
        event_id (str): The event id
        attendee (dict): The attendee details / ticket details
        user (str): The user who is assigning the Tshirt
    """
    if not has_valid_permission(event_id):
        frappe.throw("You do not have permission to access this resource", frappe.PermissionError)

    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])
    ticket.tshirt_delivered = True
    ticket.save(ignore_permissions=True)
