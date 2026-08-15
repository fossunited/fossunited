# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT, RAZORPAY_PAYMENT
from fossunited.utils.payments import (
    get_in_razorpay_money,
    get_razorpay_client,
)


class RazorpayPayment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        billing_address: DF.Text | None
        buyer_name: DF.Data | None
        company_name: DF.Data | None
        currency: DF.Literal["INR"]
        document_name: DF.DynamicLink | None
        document_type: DF.Link | None
        email: DF.Data
        gstn: DF.Data | None
        meta_data: DF.Code | None
        order_id: DF.Data | None
        payment_id: DF.Data | None
        refund_id: DF.Data | None
        state: DF.Data | None
        status: DF.Literal[
            "Captured",
            "Failed",
            "Pending",
            "Refund Pending",
            "Refunded",
        ]

    # end: auto-generated types

    @frappe.whitelist()
    def refund(self):
        frappe.only_for("System Manager")

        if not self.is_paid:
            frappe.throw(_("Refunds Can be Made Only on Captured Payments!"))

        client = get_razorpay_client()
        refund_amount = int(get_in_razorpay_money(self.amount))
        refund = client.payment.refund(self.payment_id, refund_amount)

        self.refund_id = refund["id"]
        if refund["status"] == "processed":
            self.status = "Refunded"
        elif refund["status"] == "pending":
            self.status = "Refund Pending"

        self.save()

        return refund["status"]

    @frappe.whitelist()
    def sync_status(self):
        client = get_razorpay_client()
        order = client.order.fetch(self.order_id)
        payments = client.order.payments(self.order_id).get("items", [])

        if order["status"] == "paid":
            frappe.errprint(payments)
            if payments[0]["status"] == "captured":
                capture_payment(self.order_id, payments[0]["id"])
            elif payments[0]["status"] == "refunded":
                self.status = "Refunded"
                self.save()

    @property
    def is_paid(self):
        return self.status == "Captured"

    def before_insert(self):
        if self.document_type == EVENT:
            ticket_status = frappe.db.get_value(
                EVENT, {"name": self.document_name}, "tickets_status"
            )
            if ticket_status == "Closed":
                frappe.throw(_("Ticket sale are closed for this event!"), frappe.PermissionError)


def process_refund(payment_name: str):
    payment = frappe.get_doc(RAZORPAY_PAYMENT, payment_name)
    if payment.status != "Refund Pending" or payment.refund_id:
        return payment.status

    client = get_razorpay_client()
    refund = client.payment.refund(
        payment.payment_id,
        {
            "amount": int(get_in_razorpay_money(payment.amount)),
            "receipt": f"auto-refund-{payment.name}",
        },
        headers={"X-Refund-Idempotency": f"fossunited-{payment.name}"},
    )

    frappe.db.get_value(RAZORPAY_PAYMENT, payment.name, "name", for_update=True)
    payment.reload()
    if payment.status == "Refunded":
        return payment.status
    payment.refund_id = refund["id"]
    payment.status = "Refunded" if refund["status"] == "processed" else "Refund Pending"
    payment.save(ignore_permissions=True)
    return payment.status


def capture_payment(order_id: str, payment_id: str):
    payment_name = frappe.db.get_value(
        RAZORPAY_PAYMENT,
        {"order_id": order_id},
        "name",
        for_update=True,
    )
    if not payment_name:
        return

    payment = frappe.get_doc(RAZORPAY_PAYMENT, payment_name)
    if payment.status not in ["Pending", "Failed"]:
        return payment.status

    payment.status = "Captured"
    payment.payment_id = payment_id
    payment.save(ignore_permissions=True)
    return payment.status


def retry_pending_refunds():
    payments = frappe.get_all(
        RAZORPAY_PAYMENT,
        filters={"status": "Refund Pending", "refund_id": ["is", "not set"]},
        pluck="name",
    )
    for payment_name in payments:
        frappe.enqueue(process_refund, payment_name=payment_name)
