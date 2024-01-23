import base64
import json

import frappe
from frappe.integrations.utils import (
    make_get_request,
    make_post_request,
)

# getting conference name data


def get_context(context):
    context.events = frappe.get_all(
        "FOSS Chapter Events",
        filters={
            "status": "approved",
            "event_type": "CityFOSS Conference",
        },
        fields=["event_name", "event_type"],
    )


# Script Script for creating order ID


@frappe.whitelist()
def add_ticket_to_doc(ticketsData):
    values = json.loads(ticketsData)

    print(values)

    # events = frappe.get_doc("Conference Tickets", values['events'])
    student_tickets = values["student_tickets"]
    general_tickets = values["general_tickets"]

    total_tickets_selected = int(student_tickets) + int(
        general_tickets
    )
    max_tickets_allowed = frappe.db.get_value(
        "FOSS Chapter Events", values.get("event_name"), "max_tickets"
    )
    tickets_sold = frappe.db.get_value(
        "FOSS Chapter Events",
        values.get("event_name"),
        "tickets_sold",
    )

    tickets_remaining = max(max_tickets_allowed - tickets_sold, 0)
    if total_tickets_selected > tickets_remaining:
        frappe.throw(
            f"only {tickets_remaining} tickets left, please reduce the number of tickets."
        )

    ticket = frappe.get_doc(
        {
            "doctype": "Conference Tickets",
            "event_name": values.get("event_name"),
            "first_name": values.get("first_name"),
            "last_name": values.get("last_name"),
            "pin_code": values.get("pin_code"),
            "email": values.get("email"),
            "phone": values.get("phone"),
            "state": values.get("state"),
            "general_tickets": values.get("general_tickets"),
            "student_tickets": values.get("student_tickets"),
            "general_ticket_price": values.get(
                "general_ticket_price"
            ),
            "student_ticket_price": values.get(
                "student_ticket_price"
            ),
            "total_amount": values.get("total_amount"),
        }
    )

    ticket.insert()
    ticket.order_id = makeOrderId(ticket.name, ticket.total_amount)
    ticket.save()

    print(values.get("total_amount"))

    return {
        "ticket_id": ticket.name,
        "order_id": ticket.order_id,
        "amount": ticket.total_amount,
        "currency": "INR",
        "fullname": ticket.first_name + " " + ticket.last_name,
        "email": ticket.email,
    }


doc = frappe.db.get_all(
    "Conference Tickets",
    fields=[
        "order_id",
        "payment_id",
        "first_name",
        "last_name",
        "email",
        "general_ticket_price",
        "student_ticket_price",
        "general_tickets",
        "student_tickets",
        "total_amount",
    ],
)


@frappe.whitelist()
def makeOrderId(ticket_id, total_amount):
    rzp_creds = frappe.get_single("Razorpay Keys")
    rzp_keys = rzp_creds.rzp_key

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
def capture_payment():
    doc = frappe.get_doc(
        "Conference Tickets", frappe.form_dict.ticket_id
    )

    if not doc.payment_captured:
        doc.razorpay_payment_id = frappe.form_dict.razorpay_payment_id
        doc.razorpay_signature = frappe.form_dict.razorpay_signature

        razorpay_key = frappe.db.get_single_value(
            "Razorpay Keys", "rzp_key"
        )
        basic_auth = f"Basic {createBase()}"

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
            if doc.total_amount != order["amount_paid"] / 100:
                frappe.throw(
                    f"invalid amounts {doc.total_amount} {order['amount_paid'] / 100}"
                )

        tickets_booked = int(
            frappe.db.get_value(
                "FOSS Chapter Events", doc.event_name, "tickets_sold"
            )
        )
        frappe.db.set_value(
            "FOSS Chapter Events",
            doc.event_name,
            "tickets_sold",
            int(doc.student_tickets)
            + int(doc.general_tickets)
            + tickets_booked,
        )
    doc.save(ignore_permissions=True)
