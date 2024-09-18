# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT_TICKET


class FOSSEventTicketTransfer(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        designation: DF.Data | None
        event: DF.Link | None
        organization: DF.Data | None
        owner_email: DF.Data | None
        owner_name: DF.Data | None
        receiver_email: DF.Data
        receiver_name: DF.Data
        status: DF.Literal["Pending Approval", "Completed", "Cancelled"]  # noqa: F722, F821
        ticket: DF.Link
        tshirt_size: DF.Data | None
        wants_tshirt: DF.Check
    # end: auto-generated types
    pass

    def before_insert(self):
        self.validate_ticket_exists()
        self.validate_status_is_pending()

    def before_save(self):
        if self.has_value_changed("status"):
            if self.status == "Completed":
                self.validate_ticket_exists()
                self.transfer_ticket()

    def validate(self):
        self.validate_ticket_exists()

    def validate_ticket_exists(self):
        if not frappe.db.exists(EVENT_TICKET, self.ticket):
            frappe.throw("Ticket not found", frappe.DoesNotExistError)

    def validate_status_is_pending(self):
        if self.status != "Pending Approval":
            frappe.throw(
                (
                    "Invalid status change. Status should be 'Pending Approval'. "
                    f"Current status is {self.status}"
                ),
                frappe.ValidationError,
            )

    def transfer_ticket(self):
        try:
            ticket = frappe.get_doc(EVENT_TICKET, self.ticket)
            self.handle_already_transferred_ticket(ticket)
            ticket.full_name = self.receiver_name
            ticket.email = self.receiver_email
            ticket.designation = self.designation
            ticket.organization = self.organization
            ticket.wants_tshirt = self.wants_tshirt
            ticket.tshirt_size = self.tshirt_size
            ticket.is_transfer_ticket = 1
            ticket.save(ignore_permissions=True)
        except Exception as e:
            frappe.throw(str(e), frappe.ValidationError)

    def handle_already_transferred_ticket(self, ticket):
        """
        If the ticket that is to be transferred, is already a transferred ticket,
        then set the `is_transfer_ticket` to 0 (unchecked).

        This is done, so that any notification / doc events associated with change in
        `is_transfer_ticket` field can be triggered again.
        """
        if not ticket.is_transfer_ticket:
            return

        ticket.is_transfer_ticket = 0
        ticket.save(ignore_permissions=True)
