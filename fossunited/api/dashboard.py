import frappe
import razorpay


def get_razorpay_client():
    razorpay_settings = frappe.get_cached_doc("Razorpay Settings")
    key_id = razorpay_settings.key_id
    key_secret = razorpay_settings.get_password("key_secret")
    return razorpay.Client(auth=(key_id, key_secret))


def get_in_razorpay_money(amount):
    return amount * 100


@frappe.whitelist(allow_guest=True)
def get_event(name: str) -> dict:
    return frappe.get_doc("FOSS Chapter Event", name)


@frappe.whitelist(allow_guest=True)
def create_razorpay_order(checkout_info: dict):
    client = get_razorpay_client()
    order = client.order.create(
        data={
            "amount": get_in_razorpay_money(checkout_info["amount"]),
            "currency": "INR",
        }
    )

    frappe.get_doc(
        {
            "doctype": "Razorpay Payment",
            "amount": checkout_info["amount"],
            "status": "Pending",
            "email": checkout_info["email"],
            "order_id": order["id"],
        }
    ).insert(ignore_permissions=True)

    return {"key_id": client.auth[0], "order_id": order["id"]}


@frappe.whitelist(allow_guest=True)
def handle_payment_success(
    order_id: str, payment_id: str, signature: str
):
    client = get_razorpay_client()

    client.utility.verify_payment_signature(
        {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }
    )

    # update payment
    payment = frappe.get_doc(
        "Razorpay Payment", {"order_id": order_id}
    )
    payment.status = "Captured"
    payment.payment_id = payment_id
    payment.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def handle_payment_failed(order_id):
    payment = frappe.get_doc(
        "Razorpay Payment", {"order_id": order_id}
    )
    payment.status = "Failed"
    payment.save(ignore_permissions=True)
