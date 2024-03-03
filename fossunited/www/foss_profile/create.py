import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to={frappe.request.url}#signup"
        )
        raise frappe.Redirect
    if frappe.db.exists(
        "FOSS User Profile", {"email": frappe.session.user}
    ):
        if frappe.form_dict.get("redirect-to"):
            frappe.local.flags.redirect_location = (
                frappe.form_dict.get("redirect-to")
            )
        else:
            frappe.local.flags.redirect_location = "/me"
        raise frappe.Redirect

    user = frappe.get_doc("User", frappe.session.user)
    context.full_name = user.full_name
    context.email = user.email
