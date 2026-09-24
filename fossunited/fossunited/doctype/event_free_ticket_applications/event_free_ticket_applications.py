# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT_TICKET, FREE_TICKET_CODE

TSHIRT_SKIPPED = "Skip T-shirt"


class EventFreeTicketApplications(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.ticketing.doctype.foss_ticket_custom_field.foss_ticket_custom_field import (
            FOSSTicketCustomField,
        )

        coupon_id: DF.Link
        custom_fields: DF.Table[FOSSTicketCustomField]
        designation: DF.Data | None
        email: DF.Data
        event: DF.Link | None
        full_name: DF.Data
        organization: DF.Data | None
        tshirt_size: DF.Literal["", "XS", "S", "M", "L", "XL", "2XL", "3XL", "Skip T-shirt"]
    # end: auto-generated types

    def before_insert(self):
        """Executed automatically before inserting the document."""
        if not self.event and self.coupon_id:
            event = frappe.db.get_value(FREE_TICKET_CODE, self.coupon_id, "event")
            if not event:
                frappe.throw(_("Selected coupon has no linked event. Please contact organizers"))
            self.event = event

        self.validate_email_not_used()
        coupon_data = self.validate_coupon()
        # Claim the coupon use before creating the ticket, so a concurrent
        # redemption that lost the race never gets a ticket.
        self.update_coupon_usage()
        ticket_tier = self.get_ticket_tier(coupon_data)
        self.create_free_ticket(ticket_tier, coupon_data)

    def validate_coupon(self):
        """Ensure the provided coupon is valid and not overused."""
        if not frappe.db.exists(
            FREE_TICKET_CODE,
            {"name": self.coupon_id, "event": self.event},
        ):
            frappe.throw(_("Invalid or Deleted Coupon provided."))

        coupon_data = frappe.db.get_value(
            FREE_TICKET_CODE,
            self.coupon_id,
            [
                "max_count",
                "used_count",
                "tier",
                "other_tier",
                "is_used",
                "tshirt_included",
                "mapped_email",
            ],
            as_dict=True,
        )

        if not coupon_data:
            frappe.throw(_("Coupon not found or inactive."))

        if coupon_data.is_used or (coupon_data.used_count >= coupon_data.max_count):
            frappe.throw(_("Reached max count of coupon usage."))

        self.validate_email_matches_coupon(coupon_data)
        self.validate_tshirt_size(coupon_data)

        return coupon_data

    def validate_email_matches_coupon(self, coupon_data):
        """A single-use coupon is issued to one person, so only the email it
        was sent to can redeem it. Without this, anyone the code is forwarded
        to (or who sees it posted) could claim the pass under their own email.

        Multi-use coupons (max_count > 1) are meant to be shared - e.g. a
        sponsor handing passes to their team - and one email can only hold
        one ticket per event, so they can't be bound to `mapped_email`.

        Comparison is case-insensitive: the web form keeps whatever casing
        the claimant typed. The error doesn't reveal `mapped_email`, since
        whoever is holding the code may not be its owner.
        """
        if int(coupon_data.max_count or 0) != 1:
            return

        mapped_email = (coupon_data.mapped_email or "").strip().lower()
        if mapped_email and (self.email or "").strip().lower() != mapped_email:
            frappe.throw(
                _(
                    "This coupon was issued to a different email address. Please "
                    "use the email the coupon was sent to, or contact the organizers."
                ),
                frappe.ValidationError,
            )

    def validate_tshirt_size(self, coupon_data):
        """Require a t-shirt choice only when the coupon includes a t-shirt.

        The web form hides the field for coupons without a t-shirt, so a size
        sent for such a coupon is discarded here instead of reaching the ticket.
        Claimants who do not want one pick "Skip T-shirt", which stays on the
        application as a deliberate choice but leaves the ticket without a size.
        """
        if not coupon_data.tshirt_included:
            self.tshirt_size = None
            return

        if not self.tshirt_size:
            frappe.throw(
                _("Select a t-shirt size, or choose {0} if you do not want one.").format(
                    _(TSHIRT_SKIPPED)
                )
            )

    def get_ticket_tier(self, coupon_data):
        """Derive ticket tier name from coupon info."""
        if coupon_data.tier == "Other":
            return f"{coupon_data.other_tier} Free Pass"
        return f"{coupon_data.tier} Free Pass"

    def create_free_ticket(self, ticket_tier, coupon_data):
        """Create a FOSS Event Ticket for the user."""
        wants_tshirt = int(
            bool(coupon_data.tshirt_included) and self.tshirt_size != TSHIRT_SKIPPED
        )
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
                    "wants_tshirt": wants_tshirt,
                    "tshirt_size": self.tshirt_size if wants_tshirt else None,
                    "subscribe_chapter_mailing": 1,
                    "custom_fields": [
                        {"field_name": row.field_name, "data": row.data}
                        for row in self.custom_fields
                        if row.field_name and row.data
                    ],
                }
            )
            ticket.insert(ignore_permissions=True)
        except frappe.ValidationError as e:
            frappe.throw(f"Error creating free ticket: {e}")
        except Exception as e:
            frappe.log_error(f"Unexpected error creating free ticket: {e}")
            frappe.throw(_("An unexpected error occurred while creating your free ticket."))

    def update_coupon_usage(self):
        """
        Increment coupon usage and mark as used if max reached.

        Re-reads the coupon with a row lock (SELECT ... FOR UPDATE) instead of
        trusting the counts read in validate_coupon: otherwise two concurrent
        redemptions could both see the last free use and both get a ticket.
        The lock is held until the request's transaction ends, so a second
        redemption waits here and then sees the updated count.
        """
        coupon = frappe.db.get_value(
            FREE_TICKET_CODE,
            self.coupon_id,
            ["used_count", "max_count", "is_used"],
            as_dict=True,
            for_update=True,
        )
        used_count = int(coupon.used_count or 0)
        max_count = int(coupon.max_count or 0)
        if coupon.is_used or used_count >= max_count:
            frappe.throw(_("Reached max count of coupon usage."))

        new_used_count = used_count + 1
        frappe.db.set_value(
            FREE_TICKET_CODE,
            self.coupon_id,
            {"used_count": new_used_count, "is_used": int(new_used_count >= max_count)},
        )

    def validate_email_not_used(self):
        """Ensure the email has not already claimed a free ticket for this event."""
        if frappe.db.exists(
            EVENT_TICKET,
            {
                "event": self.event,
                "email": self.email,
            },
        ):
            frappe.throw(_("This email already has a ticket for this event!"))
