import frappe

from fossunited.doctype_ids import HACKATHON, HACKATHON_PROJECT


def get_context(context):
    context.hackathon = frappe.get_doc(HACKATHON, {"permalink": frappe.form_dict.permalink})
    context.projects = frappe.get_all(
        HACKATHON_PROJECT,
        {"hackathon": context.hackathon.name},
        ["*"],
        page_length=9999,
    )
