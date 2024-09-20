import frappe
from frappe.utils.password import get_decrypted_password

from fossunited.doctype_ids import RAZORPAY_PAYMENT, RAZORPAY_SETTINGS, RAZORPAY_WEBHOOK_LOG
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
    event = form_dict.get("event")

    # Create webhook log
    frappe.get_doc(
        {
            "doctype": RAZORPAY_WEBHOOK_LOG,
            "event": event,
            "order_id": razorpay_order_id,
            "payment_id": razorpay_payment_id,
            "payload": frappe.as_json(form_dict, indent=2),
        }
    ).insert().submit()

    order_exists = frappe.db.exists(RAZORPAY_PAYMENT, {"order_id": razorpay_order_id})

    if not order_exists:
        return

    payment_doc = frappe.get_doc(RAZORPAY_PAYMENT, {"order_id": razorpay_order_id})

    if event == "payment.captured" and payment_doc.status != "Captured":
        payment_doc.status = "Captured"
        payment_doc.save()
    elif event == "refund.processed" and not payment_doc.status == "Refunded":
        refund_entity = form_dict["payload"]["refund"]["entity"]
        payment_doc.status = "Refunded"
        payment_doc.refund_id = refund_entity["id"]
        payment_doc.save()

    frappe.set_user(current_user)


def verify_webhook_signature(payload):
    signature = frappe.get_request_header("X-Razorpay-Signature")
    webhook_secret = get_decrypted_password(RAZORPAY_SETTINGS, RAZORPAY_SETTINGS, "webhook_secret")

    client = get_razorpay_client()
    client.utility.verify_webhook_signature(payload.decode(), signature, webhook_secret)
