import frappe


@frappe.whitelist(allow_guest=True)
def like(reference_doctype, reference_name, like):
    like = frappe.parse_json(like)

    if like:
        liked = add_like(reference_doctype, reference_name)
    else:
        liked = delete_like(reference_doctype, reference_name)

    return liked


def add_like(reference_doctype, reference_name):
    user = frappe.session.user

    like = frappe.new_doc("Comment")
    like.comment_type = "Like"
    like.comment_email = user
    like.reference_doctype = reference_doctype
    like.reference_name = reference_name
    like.content = "Liked by: " + user
    if user == "Guest":
        like.ip_address = frappe.local.request_ip
    like.save(ignore_permissions=True)
    return True


def delete_like(reference_doctype, reference_name):
    user = frappe.session.user

    filters = {
        "comment_type": "Like",
        "comment_email": user,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    }

    if user == "Guest":
        filters["ip_address"] = frappe.local.request_ip

    frappe.db.delete("Comment", filters)
    return False
