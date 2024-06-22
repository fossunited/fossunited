# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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
        status: DF.Literal[
            "Pending Approval", "Completed", "Cancelled"
        ]
        ticket: DF.Link
    # end: auto-generated types
    pass

    def before_save(self):
        if self.has_value_changed("status"):
            if self.status == "Completed":
                self.transfer_ticket()

    def transfer_ticket(self):
        try:
            ticket = frappe.get_doc("FOSS Event Ticket", self.ticket)
        except frappe.DoesNotExistError:
            frappe.throw("Ticket not found")
            return

        ticket.full_name = self.receiver_name
        ticket.email = self.receiver_email
        ticket.designation = self.designation
        ticket.organization = self.organization
        ticket.is_transfer_ticket = 1
        ticket.save()
