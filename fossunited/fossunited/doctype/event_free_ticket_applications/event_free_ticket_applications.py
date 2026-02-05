# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT_TICKET, FREE_TICKET_CODE


class EventFreeTicketApplications(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        coupon_id: DF.Link
        designation: DF.Data | None
        email: DF.Data
        event: DF.Link | None
        full_name: DF.Data
        organization: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        """Executed automatically before inserting the document."""
        if not self.event and self.coupon_id:
            event = frappe.db.get_value(FREE_TICKET_CODE, self.coupon_id, "event")
            if not event:
                frappe.throw("Selected coupon has no linked event. Please contact organizers")
            self.event = event

        self.validate_email_not_used()
        coupon_data = self.validate_coupon()
        ticket_tier = self.get_ticket_tier(coupon_data)
        self.create_free_ticket(ticket_tier)
        self.update_coupon_usage(coupon_data)

    def validate_coupon(self):
        """Ensure the provided coupon is valid and not overused."""
        if not frappe.db.exists(
            FREE_TICKET_CODE,
            {"name": self.coupon_id, "event": self.event},
        ):
            frappe.throw("Invalid or Deleted Coupon provided.")

        coupon_data = frappe.db.get_value(
            FREE_TICKET_CODE,
            self.coupon_id,
            ["max_count", "used_count", "tier", "other_tier", "is_used"],
            as_dict=True,
        )

        if not coupon_data:
            frappe.throw("Coupon not found or inactive.")

        if coupon_data.is_used or (coupon_data.used_count >= coupon_data.max_count):
            frappe.throw("Reached max count of coupon usage.")

        return coupon_data

    def get_ticket_tier(self, coupon_data):
        """Derive ticket tier name from coupon info."""
        if coupon_data.tier == "Other":
            return f"{coupon_data.other_tier} Free Pass"
        return f"{coupon_data.tier} Free Pass"

    def create_free_ticket(self, ticket_tier):
        """Create a FOSS Event Ticket for the user."""
        try:
            ticket = frappe.get_doc(
                {
                    "doctype": EVENT_TICKET,
                    "event": self.event,
                    "full_name": self.full_name,
                    "email": self.email,
                    "tier": ticket_tier,
                    "designation": self.designation,
                    "organization": self.organization,
                    "subscribe_chapter_mailing": 1,
                }
            )
            ticket.insert(ignore_permissions=True)
        except frappe.ValidationError as e:
            frappe.throw(f"Error creating free ticket: {e}")
        except Exception as e:
            frappe.log_error(f"Unexpected error creating free ticket: {e}")
            frappe.throw("An unexpected error occurred while creating your free ticket.")

    def update_coupon_usage(self, coupon_data):
        """Increment coupon usage and mark as used if max reached."""
        new_used_count = int(coupon_data.used_count or 0) + 1
        frappe.db.set_value(FREE_TICKET_CODE, self.coupon_id, "used_count", new_used_count)

        if new_used_count >= int(coupon_data.max_count):
            frappe.db.set_value(FREE_TICKET_CODE, self.coupon_id, "is_used", 1)

    def validate_email_not_used(self):
        """Ensure the email has not already claimed a free ticket for this event."""
        if frappe.db.exists(
            EVENT_TICKET,
            {
                "event": self.event,
                "email": self.email,
            },
        ):
            frappe.throw("This email already has a ticket for this event!")
