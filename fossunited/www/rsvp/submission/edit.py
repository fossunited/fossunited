import frappe


def get_context(context):
    context.submission = frappe.get_doc(
        "FOSS Event RSVP Submission", frappe.form_dict["rsvp"]
    )
    context.event = frappe.get_doc(
        "FOSS Chapter Events", frappe.form_dict["event"]
    )
