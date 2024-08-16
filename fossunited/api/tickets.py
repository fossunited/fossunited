"""
APIs for Tickets and Transfer Tickets
"""

import frappe


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
