import frappe
from frappe.rate_limiter import rate_limit


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(key="reference_name", limit=10, seconds=60 * 60)
def like(reference_doctype: str, reference_name: str, like: str):
    like = frappe.parse_json(like)

    if like:
        liked = add_like(reference_doctype, reference_name)
    else:
        liked = delete_like(reference_doctype, reference_name)

    return liked


def like_filters(reference_doctype, reference_name):
    user = frappe.session.user
    filters = {
        "comment_type": "Like",
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    }

    if user == "Guest":
        # Use ip_address to identify guest
        filters["ip_address"] = frappe.local.request_ip
    else:
        filters["comment_email"] = user

    return filters


def add_like(reference_doctype, reference_name):
    """
    Return True if a like was created, False if it already existed.
    """
    filters = like_filters(reference_doctype, reference_name)

    # Check first to avoid duplicates
    exists = frappe.db.exists("Comment", filters)
    if exists:
        # Already liked by this identity
        return False

    # Create the like
    user = frappe.session.user
    like = frappe.new_doc("Comment")
    like.comment_type = "Like"
    like.comment_email = user
    like.reference_doctype = reference_doctype
    like.reference_name = reference_name
    like.content = "Liked by: " + user
    if user == "Guest":
        like.ip_address = frappe.local.request_ip

    # save and return True
    like.save(ignore_permissions=True)
    # optionally re-check or log created id
    return True


def delete_like(reference_doctype, reference_name):
    """
    Return True if a like was deleted, False if none found.
    """
    filters = like_filters(reference_doctype, reference_name)

    # Use delete and return whether anything was removed
    exists = frappe.db.exists("Comment", filters)
    if not exists:
        return False

    frappe.db.delete("Comment", filters)
    return True
