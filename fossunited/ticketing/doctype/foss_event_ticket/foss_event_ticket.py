# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING

import frappe
from frappe.model.document import Document

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

        from fossunited.ticketing.doctype.foss_ticket_custom_field.foss_ticket_custom_field import (
            FOSSTicketCustomField,
        )

        custom_fields: DF.Table[FOSSTicketCustomField]
        customer: DF.Data | None
        designation: DF.Data | None
        email: DF.Data
        event: DF.Link
        full_name: DF.Data
        is_transfer_ticket: DF.Check
        organization: DF.Data | None
        razorpay_payment: DF.Link | None
        tier: DF.Data | None
        tshirt_size: DF.Data | None
        wants_tshirt: DF.Check
    # end: auto-generated types

    @staticmethod
    def create_tickets_for_payment(payment: "RazorpayPayment"):
        payment_meta_data: dict = frappe.parse_json(payment.meta_data)
        attendees = payment_meta_data.get("attendees", [])

        for attendee in attendees:
            ticket_doc = frappe.get_doc(
                {
                    "doctype": "FOSS Event Ticket",
                    "razorpay_payment": payment.name,
                    "event": payment.document_name,
                    "full_name": attendee.get("full_name"),
                    "email": attendee.get("email"),
                    "organization": attendee.get("organization"),
                    "designation": attendee.get("designation"),
                    "wants_tshirt": attendee.get("wants_tshirt", 0),
                    "tshirt_size": attendee.get("tshirt_size"),
                    "tier": payment_meta_data.get("tier", {}).get(
                        "title"
                    ),
                    "custom_fields": [],
                }
            )

            # add custom fields
            custom_fields = payment_meta_data.get("custom_fields", {})
            for k, v in custom_fields.items():
                if k and v:
                    ticket_doc.append(
                        "custom_fields",
                        {"field_name": k, "data": str(v)},
                    )
            ticket_doc.save(ignore_permissions=True)

    def after_insert(self):
        self.check_max_tickets()

    def check_max_tickets(self):
        event = frappe.get_doc("FOSS Chapter Event", self.event)
        tickets_count = frappe.db.count(
            "FOSS Event Ticket",
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
        except:
            frappe.log_error("Ticket Creation Failed!")


def validate_payment_before_insert(
    doc: "RazorpayPayment", event: str
):
    # calculate total amount
    calculated_amount = 0
    payment_meta_data: dict = frappe.parse_json(doc.meta_data)
    attendees = payment_meta_data.get("attendees", [])
    tier = payment_meta_data.get("tier", {}).get("name")
    price, event_name = frappe.db.get_value(
        "FOSS Ticket Tier", tier, ["price", "parent"]
    )

    tshirt_price = frappe.db.get_value(
        "FOSS Chapter Event", event_name, "t_shirt_price"
    )

    for attendee in attendees:
        wants_tshirt = attendee.get("wants_tshirt", 0)
        calculated_amount += price

        if wants_tshirt:
            calculated_amount += tshirt_price

    if calculated_amount != doc.amount:
        frappe.throw(
            "Looks like you did some funny stuff in the frontend and amounts don't match!"
        )


def is_foss_event(doc: "RazorpayPayment"):
    return doc.document_type == "FOSS Chapter Event"


def tickets_already_created(doc: "RazorpayPayment"):
    return frappe.db.exists(
        "FOSS Event Ticket", {"razorpay_payment": doc.name}
    )
