import frappe

from fossunited.doctype_ids import USER_PROFILE


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = f"/login?redirect-to={frappe.request.url}#signup"
    elif frappe.session.user == "Administrator":
        frappe.local.flags.redirect_location = "/desk"
    else:
        redirect_route = frappe.db.get_value(
            USER_PROFILE,
            {"email": frappe.session.user},
            "route",
        )
        if redirect_route not in [None, ""]:
            frappe.local.flags.redirect_location = redirect_route
        else:
            frappe.throw(
                "There's been an error in the creation of your FOSS Profile. "
                "Please contact administrator"
            )

    raise frappe.Redirect
