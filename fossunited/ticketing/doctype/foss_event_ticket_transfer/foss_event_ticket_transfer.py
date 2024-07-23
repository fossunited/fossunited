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
        if not frappe.db.exists("FOSS Event Ticket", self.ticket):
            frappe.throw("Ticket not found", frappe.DoesNotExistError)

    def validate_status_is_pending(self):
        if self.status != "Pending Approval":
            frappe.throw(
                "Invalid status change. Status should be 'Pending Approval'. Current status is {0}".format(
                    self.status
                ),
                frappe.ValidationError,
            )

    def transfer_ticket(self):
        self.validate_ticket_exists()
        try:
            frappe.db.set_value(
                "FOSS Event Ticket",
                self.ticket,
                {
                    "full_name": self.receiver_name,
                    "email": self.receiver_email,
                    "designation": self.designation,
                    "organization": self.organization,
                    "wants_tshirt": self.wants_tshirt,
                    "tshirt_size": self.tshirt_size,
                    "is_transfer_ticket": 1,
                },
            )
        except Exception as e:
            frappe.throw(str(e), frappe.ValidationError)
