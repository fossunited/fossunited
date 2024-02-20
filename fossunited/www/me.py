import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to={frappe.request.url}#signup"
        )
    elif frappe.session.user == "Administrator":
        frappe.local.flags.redirect_location = "/desk"
    else:
        redirect_route = frappe.db.get_value(
            "FOSS User Profile",
            {"email": frappe.session.user},
            "route",
        )
        frappe.local.flags.redirect_location = redirect_route

    raise frappe.Redirect
