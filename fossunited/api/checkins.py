import frappe
from frappe import _
from frappe.utils import getdate, now_datetime, today

from fossunited.doctype_ids import EVENT_TICKET
from fossunited.utils.decorators import require_chapter_or_event_member


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def get_attendee_with_checkin_data(event_id: str, filters: dict | None = None) -> list:
    """
    Get the attendees of the event with their checkin details (bulk queried)

    Args:
        event_id (str): The event id
        filters (dict | None): Optional search filters

    Returns:
        list: The attendees of the event with their checkin details
    """
    ALLOWED_FILTER_KEYS = {
        "name",
        "full_name",
        "email",
        "designation",
        "organization",
        "tier",
        "tshirt_size",
    }
    _filters = {"event": event_id}
    if filters:
        for key, value in filters.items():
            if key in ALLOWED_FILTER_KEYS and value:
                _filters[key] = ["like", f"%{value}%"]

    tickets = frappe.db.get_all(
        EVENT_TICKET,
        _filters,
        [
            "name",
            "full_name",
            "email",
            "designation",
            "organization",
            "wants_tshirt",
            "tier",
            "tshirt_delivered",
            "tshirt_size",
        ],
        order_by="creation desc",
    )

    ticket_names = [t["name"] for t in tickets]
    checkins_by_ticket = {}
    if ticket_names:
        all_checkins = frappe.db.get_all(
            "Event Check In",
            filters={"parent": ["in", ticket_names], "parenttype": EVENT_TICKET},
            fields=["parent", "check_in_time", "owner"],
            order_by="check_in_time asc",
        )
        for c in all_checkins:
            checkins_by_ticket.setdefault(c["parent"], []).append(
                {
                    "check_in_time": c["check_in_time"],
                    "checked_in_by": c.get("owner"),
                }
            )

    for ticket in tickets:
        ticket["checkin_data"] = checkins_by_ticket.get(ticket["name"], [])

    return tickets


def get_checkin_data(attendee_id: str) -> list:
    """
    Get the checkin data for a single attendee
    """
    return frappe.db.get_all(
        "Event Check In",
        {"parent": attendee_id, "parenttype": EVENT_TICKET, "parentfield": "check_ins"},
        ["check_in_time", "owner"],
        order_by="check_in_time asc",
    )


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def checkin_attendee(
    event_id: str, attendee: dict, assign_tshirt: bool = False, tshirt_size: str | None = None
):
    """
    Check-in the attendee for the event.

    Args:
        event_id (str): The event ID
        attendee (dict): The attendee details / ticket details
        assign_tshirt (bool): Whether to assign a T-shirt to the attendee
        tshirt_size (str | None): Optional T-shirt size if previously unspecified
    """
    ticket_name = attendee.get("name") if isinstance(attendee, dict) else str(attendee)
    ticket = frappe.get_doc(EVENT_TICKET, ticket_name)
    if ticket.event != event_id:
        frappe.throw(_("Ticket does not belong to this event"), frappe.ValidationError)

    already_checked_in = check_if_already_checked_in(ticket_name)

    if already_checked_in:
        if assign_tshirt and ticket.get("wants_tshirt") and not ticket.get("tshirt_delivered"):
            effective_size = tshirt_size or ticket.tshirt_size
            if not effective_size:
                frappe.throw(
                    _("T-shirt size is required to assign a T-shirt"), frappe.ValidationError
                )
            # Only update tshirt_delivered, do not add another check-in
            ticket.tshirt_delivered = True
            ticket.tshirt_size = effective_size
            ticket.save(ignore_permissions=True)
            return {
                "name": ticket.name,
                "tshirt_delivered": 1,
                "tshirt_size": ticket.tshirt_size,
            }
        else:
            frappe.throw(_("Attendee is already checked in"), frappe.ValidationError)

    # Perform full check-in
    ticket.append("check_ins", {"check_in_time": frappe.utils.now()})
    if assign_tshirt and ticket.get("wants_tshirt"):
        effective_size = tshirt_size or ticket.tshirt_size
        if not effective_size:
            frappe.throw(_("T-shirt size is required to assign a T-shirt"), frappe.ValidationError)
        ticket.tshirt_delivered = True
        ticket.tshirt_size = effective_size
    elif assign_tshirt:
        ticket.tshirt_delivered = True
        if tshirt_size:
            ticket.tshirt_size = tshirt_size
    ticket.save(ignore_permissions=True)
    return {
        "name": ticket.name,
        "tshirt_delivered": bool(ticket.tshirt_delivered),
        "tshirt_size": ticket.tshirt_size,
    }


def check_if_already_checked_in(attendee_id: str) -> bool:
    """
    Check if the attendee is already checked in
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
    """
    ticket_name = attendee.get("name") if isinstance(attendee, dict) else str(attendee)
    ticket = frappe.get_doc(EVENT_TICKET, ticket_name)
    if ticket.event != event_id:
        frappe.throw(_("Ticket does not belong to this event"), frappe.ValidationError)
    if ticket.check_ins:
        ticket.check_ins.pop()
        ticket.save(ignore_permissions=True)


@frappe.whitelist()
@require_chapter_or_event_member(event_id="event_id")
def assign_tshirt(event_id: str, attendee: dict, tshirt_size: str | None = None):
    """
    Assign Tshirt to the attendee, optionally recording size
    """
    ticket_name = attendee.get("name") if isinstance(attendee, dict) else str(attendee)
    ticket = frappe.get_doc(EVENT_TICKET, ticket_name)
    if ticket.event != event_id:
        frappe.throw(_("Ticket does not belong to this event"), frappe.ValidationError)
    effective_size = tshirt_size or ticket.tshirt_size
    if not effective_size:
        frappe.throw(_("T-shirt size is required to assign a T-shirt"), frappe.ValidationError)
    ticket.tshirt_delivered = True
    ticket.tshirt_size = effective_size
    ticket.save(ignore_permissions=True)
    return {
        "name": ticket.name,
        "tshirt_delivered": 1,
        "tshirt_size": ticket.tshirt_size,
    }


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
