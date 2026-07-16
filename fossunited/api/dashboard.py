import frappe
from frappe import _

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_TICKET,
    RAZORPAY_PAYMENT,
    TICKET_TIER,
    USER_PROFILE,
)
from fossunited.utils.payments import (
    get_in_razorpay_money,
    get_razorpay_client,
)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_event(name: str, by_route: bool = False) -> dict:
    if by_route:
        if not name.startswith("c/"):
            name = f"c/{name}"

        event_id = frappe.db.get_value(EVENT, {"route": name}, "name")
        if not event_id:
            return {}
    else:
        event_id = name

    doc = frappe.get_doc(EVENT, event_id)
    data = doc.as_dict()
    # Remove members table
    data.pop("event_members", None)

    if doc.chapter:
        data["chapter_email"] = frappe.db.get_value(CHAPTER, doc.chapter, "email")

    for tier in data.get("tiers", []):
        if tier.get("maximum_tickets"):
            tier["sold_count"] = frappe.db.count(
                EVENT_TICKET,
                {"event": event_id, "tier": tier.get("title")},
            )

    return data


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_event_from_permalink(permalink: str, fields: list) -> dict:
    return frappe.db.get_value(EVENT, {"event_permalink": permalink}, fields, as_dict=1)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_states():
    return frappe.get_all("State", fields=["name"], page_length=1000, order_by="name")


def _compute_order_amount(meta_data: dict, ref_doctype: str, ref_docname: str) -> float:
    """Compute order total server-side from tier prices + t-shirt costs."""
    tier_counts = meta_data.get("tier_counts") or {}
    total = 0.0

    for tier_name, count in tier_counts.items():
        count = int(count or 0)
        if count <= 0:
            continue
        price = frappe.db.get_value(TICKET_TIER, tier_name, "price") or 0
        total += float(price) * count

    if ref_doctype == EVENT and ref_docname:
        event_doc = frappe.db.get_value(
            EVENT,
            ref_docname,
            ["paid_tshirts_available", "t_shirt_price"],
            as_dict=True,
        )
        if event_doc and event_doc.paid_tshirts_available:
            attendees = meta_data.get("attendees") or []
            tier_tshirt_included = {
                tier_name: bool(frappe.db.get_value(TICKET_TIER, tier_name, "tshirt_included"))
                for tier_name in (meta_data.get("tier_counts") or {}).keys()
            }
            num_tshirts = sum(
                1
                for a in attendees
                if a.get("wants_tshirt")
                and not tier_tshirt_included.get(a.get("ticket_type"), False)
            )
            total += float(event_doc.t_shirt_price or 0) * num_tshirts

    return total


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def create_razorpay_order(
    checkout_info: dict,
    meta_data: dict | None = None,
    ref_doctype: str | None = None,
    ref_docname: str | None = None,
):
    if meta_data is None:
        meta_data = {}
    amount = _compute_order_amount(meta_data, ref_doctype, ref_docname)
    if amount <= 0:
        frappe.throw(frappe._("Order amount must be greater than zero."), frappe.ValidationError)

    client_amount = float(checkout_info.get("amount") or 0)
    if abs(client_amount - amount) > 1:
        frappe.throw(
            frappe._("Amount mismatch - please refresh and try again."),
            frappe.ValidationError,
        )

    client = get_razorpay_client()
    order = client.order.create(
        data={
            "amount": get_in_razorpay_money(amount),
            "currency": "INR",
        }
    )

    frappe.get_doc(
        {
            "doctype": RAZORPAY_PAYMENT,
            "amount": amount,
            "email": checkout_info["email"],
            "buyer_name": checkout_info.get("tax_details", {}).get("buyer_name"),
            "company_name": checkout_info.get("tax_details", {}).get("company_name"),
            "state": checkout_info.get("tax_details", {}).get("state"),
            "gstn": checkout_info.get("tax_details", {}).get("gstn"),
            "billing_address": checkout_info.get("tax_details", {}).get("billing_address"),
            "status": "Pending",
            "order_id": order["id"],
            "document_type": ref_doctype,
            "document_name": ref_docname,
            "meta_data": frappe.as_json(meta_data, indent=2),
        }
    ).insert(ignore_permissions=True)

    return {"key_id": client.auth[0], "order_id": order["id"]}


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def handle_payment_success(order_id: str, payment_id: str, signature: str):
    client = get_razorpay_client()

    client.utility.verify_payment_signature(
        {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }
    )

    # update payment
    payment = frappe.get_doc(RAZORPAY_PAYMENT, {"order_id": order_id})
    payment.status = "Captured"
    payment.payment_id = payment_id
    payment.save(ignore_permissions=True)


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def handle_payment_failed(order_id: str):
    client = get_razorpay_client()
    try:
        order = client.order.fetch(order_id)
    except Exception:
        frappe.throw(frappe._("Invalid order."), frappe.ValidationError)

    if order.get("status") == "paid":
        return

    payment = frappe.get_doc(RAZORPAY_PAYMENT, {"order_id": order_id})
    if payment.status == "Captured":
        return
    payment.status = "Failed"
    payment.save(ignore_permissions=True)


@frappe.whitelist()
def get_session_user_profile():
    """
    Used mainly for dashboard header.
    Returns some basic information about the user profile.
    """
    user = frappe.db.get_value(
        USER_PROFILE,
        {"user": frappe.session.user},
        ["*"],
        as_dict=1,
    )

    return user


@frappe.whitelist()
def get_profile_data(username: str | None = None, email: str | None = None) -> dict:
    """
    Returns the profile data of the given username.
    """
    if not username and not email:
        frappe.throw(_("Username or email is required"))

    user = frappe.db.get_value(
        USER_PROFILE,
        {"user": username, "email": email or ""},
        [
            "full_name",
            "username",
            "profile_photo",
            "route",
        ],
        as_dict=1,
    )

    return user


@frappe.whitelist()
def get_user_profile_list(filters: dict | None = None, search_term: str | None = None) -> list:
    """
    Returns the list of user profiles based on the given filters and optional search term.
    """
    if not filters:
        filters = {}

    if search_term and len(search_term.strip()) >= 2:
        search_term = search_term.strip()
        or_filters = [
            ["username", "like", f"%{search_term}%"],
            ["full_name", "like", f"%{search_term}%"],
        ]

        profiles = frappe.db.get_all(
            USER_PROFILE,
            filters=filters,
            or_filters=or_filters,
            fields=[
                "full_name",
                "profile_photo",
                "route",
                "username",
                "name",
            ],
            page_length=50,
            order_by="username asc",
        )
    else:
        profiles = []

    return profiles
