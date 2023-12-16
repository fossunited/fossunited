import frappe


def get_context(context):
    context.submission = frappe.get_doc(
        "FOSS Event CFP Submission", frappe.form_dict["cfp"]
    )
    context.event = frappe.get_doc(
        "FOSS Chapter Events", frappe.form_dict["event"]
    )
