import frappe

from fossunited.utils.payments import (
    get_in_razorpay_money,
    get_razorpay_client,
)


@frappe.whitelist(allow_guest=True)
def get_event(name: str) -> dict:
    return frappe.get_doc("FOSS Chapter Event", name)


@frappe.whitelist(allow_guest=True)
def get_states():
    return frappe.get_all(
        "State", fields=["name"], page_length=1000, order_by="name"
    )


@frappe.whitelist(allow_guest=True)
def create_razorpay_order(
    checkout_info: dict,
    meta_data=dict(),
    ref_doctype=None,
    ref_docname=None,
):
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
            "email": checkout_info["email"],
            "buyer_name": checkout_info.get("tax_details", {}).get(
                "buyer_name"
            ),
            "company_name": checkout_info.get("tax_details", {}).get(
                "company_name"
            ),
            "state": checkout_info.get("tax_details", {}).get(
                "state"
            ),
            "gstn": checkout_info.get("tax_details", {}).get("gstn"),
            "billing_address": checkout_info.get(
                "tax_details", {}
            ).get("billing_address"),
            "status": "Pending",
            "order_id": order["id"],
            "document_type": ref_doctype,
            "document_name": ref_docname,
            "meta_data": frappe.as_json(meta_data, indent=2),
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
