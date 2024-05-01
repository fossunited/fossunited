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
        email: DF.Data
        event: DF.Link
        full_name: DF.Data
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
                    "wants_tshirt": attendee.get("wants_tshirt", 0),
                    "tshirt_size": attendee.get("tshirt_size"),
                    "tier": payment_meta_data.get("tier", {}).get(
                        "title"
                    ),
                }
            ).insert()

            # add custom fields
            custom_fields = payment_meta_data.get("custom_fields", {})
            for k, v in custom_fields.items():
                ticket_doc.append(
                    "custom_fields", {"field_name": k, "data": str(v)}
                )
            ticket_doc.save()


def handle_payment_on_update(doc: "RazorpayPayment", event: str):
    if not is_foss_event(doc):
        return

    if tickets_already_created(doc):
        return

    if doc.status == "Captured":
        current_user = frappe.session.user
        frappe.set_user("Administrator")
        try:
            FOSSEventTicket.create_tickets_for_payment(doc)
        except:
            frappe.log_error("Ticket Creation Failed!")
        finally:
            frappe.set_user(current_user)


def is_foss_event(doc: "RazorpayPayment"):
    return doc.document_type == "FOSS Chapter Event"


def tickets_already_created(doc: "RazorpayPayment"):
    return frappe.db.exists(
        "FOSS Event Ticket", {"razorpay_payment": doc.name}
    )
