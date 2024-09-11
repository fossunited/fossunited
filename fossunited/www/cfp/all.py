import frappe


def get_context(context):
    event_permalink = frappe.form_dict.get("event_permalink")

    frappe.local.flags.redirect_location = f"/dashboard/cfp/{event_permalink}"

    raise frappe.Redirect
