import frappe
from frappe import _

from fossunited.doctype_ids import (
    CHAPTER,
    CORE_TEAM,
    EVENT,
    EVENT_TICKET,
    RAZORPAY_PAYMENT,
    TICKET_TIER,
    USER_PROFILE,
)
from fossunited.fossunited.permissions import _ctm_chapters
from fossunited.payments.doctype.razorpay_payment.razorpay_payment import (
    capture_payment,
    fail_payment,
)
from fossunited.utils.payments import (
    get_in_razorpay_money,
    get_razorpay_client,
)


def _resolve_event_id(name: str, by_route: bool, by_permalink: bool) -> str | None:
    if by_route:
        if not name.startswith("c/"):
            name = f"c/{name}"
        return frappe.db.get_value(EVENT, {"route": name}, "name")
    if by_permalink:
        return frappe.db.get_value(EVENT, {"event_permalink": name}, "name")
    return name


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_event(name: str, by_route: bool = False, by_permalink: bool = False) -> dict:
    event_id = _resolve_event_id(name, by_route, by_permalink)
    if not event_id:
        return {}

    doc = frappe.get_doc(EVENT, event_id)

    user = frappe.session.user
    is_privileged = "System Manager" in frappe.get_roles(user) or doc.chapter in _ctm_chapters(
        user
    )
    if not doc.is_published and not is_privileged:
        # Same message either way: don't reveal that an unpublished event exists.
        frappe.throw(_("Event not found"), frappe.DoesNotExistError)

    # Drop anything above permlevel 0 (e.g. event_data) the caller has no role for.
    doc.apply_fieldlevel_read_permissions()
    data = doc.as_dict()

    internal_fields = ("_comments", "_assign", "_liked_by", "owner", "modified_by")
    data.pop("event_members", None)
    for field in internal_fields:
        data.pop(field, None)

    # Every child table carries the same per-row metadata
    for table_field in doc.meta.get_table_fields():
        for row in data.get(table_field.fieldname) or []:
            for field in internal_fields:
                row.pop(field, None)

    if doc.chapter:
        data["chapter_email"] = frappe.db.get_value(CHAPTER, doc.chapter, "email")

    capped_tiers = [tier for tier in data.get("tiers", []) if tier.get("maximum_tickets")]
    if capped_tiers:
        sold_counts = {
            row.tier: row.count
            for row in frappe.get_all(
                EVENT_TICKET,
                filters={"event": event_id},
                group_by="tier",
                fields=["tier", {"COUNT": "name", "as": "count"}],
            )
        }
        for tier in capped_tiers:
            tier["sold_count"] = sold_counts.get(tier.get("title"), 0)

    return data


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

    return {"status": capture_payment(order_id, payment_id)}


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

    fail_payment(order_id)


@frappe.whitelist()
def get_session_user_profile():
    """
    Used mainly for dashboard header.
    Returns some basic information about the user profile.
    """
    user = frappe.db.get_value(
        USER_PROFILE,
        {"user": frappe.session.user},
        [
            "name",
            "full_name",
            "username",
            "profile_photo",
            "cover_image",
            "bio",
            "route",
            "user",
            "email",
        ],
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
def get_user_profile_list(search_term: str | None = None, exclude: list | None = None) -> list:
    """
    Profiles for the dashboard "Add member" picker, matched on username or full name.
    Only chapter team members and event Core Team Members (the two places the picker is used) may search.
    """
    user = frappe.session.user
    is_event_core = frappe.db.exists(
        "FOSS Chapter Event Member", {"email": user, "role": CORE_TEAM}
    )
    if not (_ctm_chapters(user) or is_event_core):
        frappe.throw(
            _("Only chapter or event team members can search for members."),
            frappe.PermissionError,
        )

    search_term = (search_term or "").strip().lstrip("@")
    if len(search_term) < 2:
        return []

    query = frappe.qb.get_query(
        USER_PROFILE,
        fields=["full_name", "profile_photo", "route", "username", "name"],
        filters={"name": ["not in", exclude]} if exclude else None,
        order_by="username asc",
        limit=50,
    )
    # each word must match the username or full name, in any order ("imu nerona" finds "nerona imu")
    profile = frappe.qb.DocType(USER_PROFILE)
    for word in search_term.split():
        query = query.where(
            profile.username.like(f"%{word}%") | profile.full_name.like(f"%{word}%")
        )
    return query.run(as_dict=True)
