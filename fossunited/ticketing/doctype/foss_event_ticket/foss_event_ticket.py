# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from datetime import datetime
from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document

from fossunited.api.emailing import handle_email_group_subscription
from fossunited.doctype_ids import EVENT, EVENT_TICKET, TICKET_TIER

if TYPE_CHECKING:
    from fossunited.payments.doctype.razorpay_payment.razorpay_payment import (
        RazorpayPayment,
    )


class FOSSEventTicket(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.event_check_in.event_check_in import (
            EventCheckIn,
        )
        from fossunited.ticketing.doctype.foss_ticket_custom_field.foss_ticket_custom_field import (
            FOSSTicketCustomField,
        )

        accept_coc: DF.Check
        check_ins: DF.Table[EventCheckIn]
        custom_fields: DF.Table[FOSSTicketCustomField]
        customer: DF.Data | None
        designation: DF.Data | None
        email: DF.Data
        event: DF.Link
        full_name: DF.Data
        is_transfer_ticket: DF.Check
        organization: DF.Data | None
        razorpay_payment: DF.Link | None
        subscribe_chapter_mailing: DF.Check
        tier: DF.Data | None
        tshirt_delivered: DF.Check
        tshirt_size: DF.Data | None
        wants_tshirt: DF.Check
    # end: auto-generated types

    @staticmethod
    def create_tickets_for_payment(payment: "RazorpayPayment"):
        """
        Create tickets for a successful payment.
        Handles both global custom fields (applied to all attendees)
        and individual custom fields (per attendee).
        """
        payment_meta_data: dict = frappe.parse_json(payment.meta_data)
        attendees = payment_meta_data.get("attendees", [])

        # Check if custom fields should be applied to all attendees
        custom_fields_apply_to_all = payment_meta_data.get("custom_fields_apply_to_all", False)
        global_custom_fields = payment_meta_data.get("global_custom_fields", {})

        tier_names = {a.get("ticket_type") for a in attendees if a.get("ticket_type")}
        tshirt_included_by_tier = {
            name: bool(frappe.db.get_value(TICKET_TIER, name, "tshirt_included"))
            for name in tier_names
        }

        for attendee in attendees:
            tier_name = attendee.get("ticket_type")
            wants_tshirt = int(attendee.get("wants_tshirt", 0)) or int(
                tshirt_included_by_tier.get(tier_name, False)
            )

            ticket_doc = frappe.get_doc(
                {
                    "doctype": EVENT_TICKET,
                    "razorpay_payment": payment.name,
                    "event": payment.document_name,
                    "full_name": attendee.get("full_name"),
                    "email": attendee.get("email"),
                    "subscribe_chapter_mailing": attendee.get("subscribe_chapter_mailing"),
                    "organization": attendee.get("organization"),
                    "designation": attendee.get("designation"),
                    "wants_tshirt": wants_tshirt,
                    "tshirt_size": attendee.get("tshirt_size") if wants_tshirt else None,
                    "accept_coc": attendee.get("accept_coc", 0),
                    "tier": frappe.db.get_value(TICKET_TIER, attendee.get("ticket_type"), "title")
                    or (payment_meta_data.get("tiers_snapshot") or {})
                    .get(attendee.get("ticket_type"), {})
                    .get("title"),
                    "custom_fields": [],
                }
            )

            # Determine which custom fields to use
            if custom_fields_apply_to_all:
                # Use global custom fields for all attendees
                custom_fields = global_custom_fields
            else:
                # Use individual attendee's custom fields
                custom_fields = attendee.get("custom_fields", {})

            # Add custom fields to ticket
            for k, v in custom_fields.items():
                if k and v:
                    ticket_doc.append(
                        "custom_fields",
                        {"field_name": k, "data": str(v)},
                    )

            ticket_doc.save(ignore_permissions=True)

    def before_insert(self):
        if not self.is_ticket_live():
            frappe.throw(_("Ticket sale are closed for this event!"), frappe.PermissionError)

    def after_insert(self):
        self.check_max_tickets()
        self.handle_add_to_email_group()

    def before_save(self):
        if self.has_value_changed("subscribe_chapter_mailing"):
            self.handle_add_to_email_group()

    def handle_add_to_email_group(self):
        # Check if user should be subscribed
        if not self.email:
            return

        event_doc = frappe.get_doc(EVENT, self.event)
        handle_email_group_subscription(
            emails=[self.email],
            chapter=event_doc.chapter,
            event=self.event,
            subscribe_to_chapter=self.subscribe_chapter_mailing,
            subscribe_to_event=self.subscribe_chapter_mailing,
            document_type_event=EVENT,
        )

    def is_ticket_live(self):
        tickets_status = frappe.db.get_value(
            EVENT,
            {"name": self.event},
            "tickets_status",
        )
        return bool(tickets_status == "Live")

    def check_max_tickets(self):
        event = frappe.get_doc(EVENT, self.event)
        tickets_count = frappe.db.count(
            EVENT_TICKET,
            {"event": self.event, "tier": self.tier},
        )

        for tier in event.tiers:
            if (
                tier.title == self.tier
                and tier.maximum_tickets
                and (tickets_count >= tier.maximum_tickets)
            ):
                event.tiers[tier.idx - 1].enabled = 0
                event.save(ignore_permissions=True)
                return


def handle_payment_on_update(doc: "RazorpayPayment", event: str):
    if not is_foss_event(doc):
        return

    if tickets_already_created(doc):
        return

    if doc.status == "Captured":
        try:
            FOSSEventTicket.create_tickets_for_payment(doc)
        except Exception as e:
            frappe.log_error(
                title="Ticket Creation Failed",
                message=f"Payment: {doc.name}\nEvent: {doc.document_name}\nAmount: {doc.amount}\nError: {e}\nMeta: {doc.meta_data}",
            )
            raise


class TicketTierMismatchError(frappe.ValidationError):
    pass


def validate_payment_before_insert(doc: "RazorpayPayment", event: str):
    payment_meta_data: dict = frappe.parse_json(doc.meta_data)
    tier_counts: dict = payment_meta_data.get("tier_counts") or {}
    attendees = payment_meta_data.get("attendees", [])
    event_name = payment_meta_data.get("event")

    if not tier_counts:
        frappe.throw(_("No ticket tiers selected."), TicketTierMismatchError)

    calculated_amount = 0.0
    tshirt_included_by_tier: dict[str, bool] = {}

    for tier_name, count in tier_counts.items():
        count = int(count or 0)
        if count <= 0:
            continue

        price, tier_event = frappe.db.get_value(TICKET_TIER, tier_name, ["price", "parent"])
        if tier_event != event_name:
            frappe.throw(_("A tier does not belong to this event."), TicketTierMismatchError)

        tier_details = frappe.get_doc(TICKET_TIER, tier_name)
        tshirt_included_by_tier[tier_name] = bool(tier_details.tshirt_included)

        if not tier_details.enabled:
            frappe.throw(
                f"Ticket tier '{tier_details.title}' is not enabled.",
                TicketTierMismatchError,
            )

        if tier_details.valid_till and tier_details.valid_till < datetime.today().date():
            frappe.throw(
                f"Ticket tier '{tier_details.title}' has expired.",
                TicketTierMismatchError,
            )

        existing_count = frappe.db.count(
            EVENT_TICKET,
            filters={"tier": tier_details.title, "event": event_name},
        )
        if (
            tier_details.maximum_tickets
            and (existing_count + count) > tier_details.maximum_tickets
        ):
            frappe.throw(
                f"Not enough seats in '{tier_details.title}'. Houseful!",
                TicketTierMismatchError,
            )

        calculated_amount += float(price) * count

    paid_tshirts_available, tshirt_price = frappe.db.get_value(
        EVENT, event_name, ["paid_tshirts_available", "t_shirt_price"]
    )
    if paid_tshirts_available:
        num_tshirts = sum(
            1
            for a in attendees
            if a.get("wants_tshirt")
            and not tshirt_included_by_tier.get(a.get("ticket_type"), False)
        )
        calculated_amount += float(tshirt_price or 0) * num_tshirts

    if abs(calculated_amount - float(doc.amount)) > 1:
        frappe.log_error(
            title="Payment Amount Mismatch",
            message=f"Event: {event_name}\nDoc amount: {doc.amount}\nCalculated: {calculated_amount}\nTier counts: {tier_counts}\nTshirt included by tier: {tshirt_included_by_tier}",
        )
        frappe.throw(
            _("Amount mismatch - please refresh and try again."),
            TicketTierMismatchError,
        )


def is_foss_event(doc: "RazorpayPayment"):
    return doc.document_type == EVENT


def tickets_already_created(doc: "RazorpayPayment"):
    return frappe.db.exists(EVENT_TICKET, {"razorpay_payment": doc.name})
