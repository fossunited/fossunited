import frappe
from frappe import _
from frappe.utils import getdate, now_datetime, today

from fossunited.doctype_ids import EVENT_TICKET
from fossunited.utils.decorators import require_chapter_or_event_member


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def get_attendee_with_checkin_data(event_id: str, filters: dict | None = None) -> dict:
    """
    Get the attendees of the event with their checkin details

    Args:
        event_id (str): The event id
        user (str): The user who is requesting the data

    Returns:
        dict: The attendees of the event with their checkin details
    """
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
@require_chapter_or_event_member(event_id="event_id")
def checkin_attendee(event_id: str, attendee: dict, assign_tshirt: bool = False):
    """
    Check-in the attendee for the event.

    Args:
        event_id (str): The event ID
        attendee (dict): The attendee details / ticket details
        assign_tshirt (bool): Whether to assign a T-shirt to the attendee
    """
    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])

    already_checked_in = check_if_already_checked_in(attendee["name"])

    if already_checked_in:
        if assign_tshirt and ticket.get("wants_tshirt") and not ticket.get("tshirt_delivered"):
            # Only update tshirt_delivered, do not add another check-in
            ticket.tshirt_delivered = True
            ticket.save(ignore_permissions=True)
            return  # Success, exit early
        else:
            frappe.throw(_("Attendee is already checked in"), frappe.ValidationError)

    # Perform full check-in
    ticket.append("check_ins", {"check_in_time": frappe.utils.now()})
    if assign_tshirt:
        ticket.tshirt_delivered = True
    ticket.save(ignore_permissions=True)


def check_if_already_checked_in(attendee_id: str) -> bool:
    """
    Check if the attendee is already checked in

    Args:
        attendee_id (str): The attendee / ticket id

    Returns:
        bool: True if the attendee is already checked in, False otherwise
    """
    checkins = frappe.db.get_all(
        "Event Check In",
        {"parent": attendee_id, "parenttype": EVENT_TICKET, "parentfield": "check_ins"},
        ["check_in_time"],
    )

    if not checkins:
        return False

    today_date = getdate(today())
    for checkin in checkins:
        if getdate(checkin["check_in_time"]) == today_date:
            return True

    return False


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def undo_attendee_checkin(event_id: str, attendee: dict):
    """
    Undo the check-in for the attendee

    Args:
        attendee (dict): The attendee details / ticket details
        user (str): The user who is undoing the check-in
    """
    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])
    ticket.check_ins.pop()
    ticket.save(ignore_permissions=True)


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def assign_tshirt(event_id: str, attendee: dict):
    """
    Assign Tshirt to the attendee

    Args:
        event_id (str): The event id
        attendee (dict): The attendee details / ticket details
        user (str): The user who is assigning the Tshirt
    """
    ticket = frappe.get_doc(EVENT_TICKET, attendee["name"])
    ticket.tshirt_delivered = True
    ticket.save(ignore_permissions=True)


# for event checkins
def has_checked_in_today(doc):
    """Check if document has a check-in today"""
    today = getdate()
    for check_in in doc.check_ins:
        if getdate(check_in.check_in_time) == today:
            return True
    return False


def add_checkin(doc):
    """Add a check-in to document"""
    if has_checked_in_today(doc):
        frappe.throw(_("Already checked in today"))
    doc.append("check_ins", {"check_in_time": now_datetime()})
    doc.save()


def remove_today_checkin(doc):
    """Remove today's check-in from document"""
    today = getdate()
    for check_in in reversed(doc.check_ins):
        if getdate(check_in.check_in_time) == today:
            doc.remove(check_in)
            doc.save()
            return True
    frappe.throw(_("No check-in found for today"))
