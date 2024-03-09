import base64
import json

import frappe
from frappe.integrations.utils import (
    make_get_request,
    make_post_request,
)


# getting conference name data
def get_context(context):
    context.event = frappe.get_doc(
        "FOSS Chapter Events",
        {"event_permalink": frappe.form_dict.event_permalink},
    ).as_dict()
    context.session_user = frappe.get_doc(
        "User", frappe.session.user
    ).as_dict()
    context.no_cache = 1


# Script Script for creating order ID
@frappe.whitelist()
def add_ticket_to_doc(ticketsData):
    values = json.loads(ticketsData)

    student_ticket_price = frappe.db.get_value(
        "FOSS Chapter Events", values["event"], "student_ticket_price"
    )
    general_ticket_price = frappe.db.get_value(
        "FOSS Chapter Events", values["event"], "general_ticket_price"
    )

    student_tickets = values["student_tickets"]
    general_tickets = values["general_tickets"]

    total_tickets_selected = int(student_tickets) + int(
        general_tickets
    )

    max_tickets_allowed = frappe.db.get_value(
        "FOSS Chapter Events", values["event"], "max_tickets"
    )
    tickets_sold = frappe.db.get_value(
        "FOSS Chapter Events", values["event"], "tickets_sold"
    )

    tickets_remaining = max(max_tickets_allowed - tickets_sold, 0)
    if total_tickets_selected > tickets_remaining:
        frappe.throw(
            f"only {tickets_remaining} tickets left, please reduce the number of tickets."
        )

    ticket = frappe.get_doc(
        {
            "doctype": "Conference Tickets",
            "event": values["event"],
            "event_name": values["event_name"],
            "first_name": values.get("first_name"),
            "last_name": values.get("last_name"),
            "pin_code": values.get("pin_code"),
            "email": values.get("email"),
            "phone": values.get("phone"),
            "state": values.get("state"),
            "general_tickets": values.get("general_tickets"),
            "student_tickets": values.get("student_tickets"),
        }
    )

    total_amount = (
        float(student_ticket_price) * int(ticket.student_tickets)
    ) + (float(general_ticket_price) * int(ticket.general_tickets))

    ticket.total_amount = total_amount

    ticket.insert()
    ticket.order_id = makeOrderId(ticket.name, total_amount)
    ticket.save()

    return {
        "ticket_id": ticket.name,
        "order_id": ticket.order_id,
        "amount": ticket.total_amount,
        "razorpay_key": frappe.db.get_single_value(
            "Razorpay Keys", "rzp_key"
        ),
        "currency": "INR",
        "fullname": ticket.first_name + " " + ticket.last_name,
        "email": ticket.email,
    }


@frappe.whitelist()
def makeOrderId(ticket_id, total_amount):
    rzp_basic_auth = f"Basic {createBase()}"

    order = make_post_request(
        f"https://api.razorpay.com/v1/orders",
        headers={
            "Authorization": rzp_basic_auth,
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "amount": total_amount * 100,
                "currency": "INR",
                "notes": {"ticket_id": ticket_id},
            }
        ),
    )

    return order["id"]


@frappe.whitelist()
def getPaymentId(order_id):
    rzp_basic_auth = f"Basic {createBase()}"

    payment = make_get_request(
        f"https://api.razorpay.com/v1/orders/{order_id}/payments",
        headers={
            "Authorization": rzp_basic_auth,
            "Content-Type": "application/json",
        },
    )

    return payment["items"][0]["id"]


# Function to auomate the formatting of api_key:api_secret
def createBase():
    key_id = frappe.db.get_single_value("Razorpay Keys", "rzp_key")
    secretKey = frappe.get_single("Razorpay Keys")
    key_secret = secretKey.get_password("key_secret")
    basic_auth = base64.b64encode(
        f"{key_id}:{key_secret}".encode()
    ).decode()

    return basic_auth


# Function to update captured payment state
@frappe.whitelist()
def capture_payment(doctype, ticket_id):
    doc = frappe.get_doc("Conference Tickets", ticket_id)

    basic_auth = f"Basic {createBase()}"

    if not doc.payment_captured:
        doc.razorpay_payment_id = getPaymentId(doc.order_id)

        order = make_get_request(
            f"https://api.razorpay.com/v1/orders/{doc.order_id}",
            headers={
                "Authorization": basic_auth,
                "Content-Type": "application/json",
            },
        )

        doc.payment_captured = (
            True if order["status"] == "paid" else False
        )

        if doc.payment_captured:
            if float(doc.total_amount) != float(
                order["amount_paid"] / 100
            ):
                frappe.throw(f"Invalid Amount, payment not captured")

        tickets_sold = int(
            frappe.db.get_value(
                "FOSS Chapter Events", doc.event, "tickets_sold"
            )
        )

        frappe.db.set_value(
            "FOSS Chapter Events",
            doc.event,
            "tickets_sold",
            int(doc.student_tickets)
            + int(doc.general_tickets)
            + int(tickets_sold),
        )

    doc.save(ignore_permissions=True)
