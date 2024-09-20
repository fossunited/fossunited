import frappe
import razorpay

from fossunited.doctype_ids import RAZORPAY_SETTINGS


def get_razorpay_client():
    razorpay_settings = frappe.get_cached_doc(RAZORPAY_SETTINGS)
    key_id = razorpay_settings.key_id
    key_secret = razorpay_settings.get_password("key_secret")

    if not (key_id or key_secret):
        frappe.throw(
            f"Please set API keys in {frappe.bold('Razorpay Settings')} "
            "before trying to create a razorpay client!"
        )

    return razorpay.Client(auth=(key_id, key_secret))


def get_in_razorpay_money(amount):
    return amount * 100
