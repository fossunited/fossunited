import frappe
from frappe.utils.password import get_decrypted_password

from fossunited.utils.payments import get_razorpay_client


@frappe.whitelist(allow_guest=True)
def handle_razorpay_webhook():
    form_dict = frappe.local.form_dict
    payload = frappe.request.get_data()

    verify_webhook_signature(payload)  # for security purposes

    current_user = frappe.session.user
    frappe.set_user("Administrator")

    payment_entity = form_dict["payload"]["payment"]["entity"]
    razorpay_order_id = payment_entity["order_id"]
    razorpay_payment_id = payment_entity["id"]
    customer_email = payment_entity["email"]
    event = form_dict.get("event")

    # Create webhook log
    frappe.get_doc(
        {
            "doctype": "Razorpay Webhook Log",
            "event": event,
            "order_id": razorpay_order_id,
            "payment_id": razorpay_payment_id,
            "payload": frappe.as_json(form_dict, indent=2),
        }
    ).insert().submit()

    order_exists = frappe.db.exists(
        "Razorpay Payment", {"order_id": razorpay_order_id}
    )

    if not order_exists:
        return

    payment_doc = frappe.get_doc(
        "Razorpay Payment", {"order_id": razorpay_order_id}
    )
    if (
        event == "payment.captured"
        and not payment_doc.status != "Captured"
    ):
        payment_doc.status = "Captured"
        payment_doc.save()

    frappe.set_user(current_user)


def verify_webhook_signature(payload):
    signature = frappe.get_request_header("X-Razorpay-Signature")
    webhook_secret = get_decrypted_password(
        "Razorpay Settings", "Razorpay Settings", "webhook_secret"
    )

    client = get_razorpay_client()
    client.utility.verify_webhook_signature(
        payload.decode(), signature, webhook_secret
    )
