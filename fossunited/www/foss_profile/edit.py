import frappe

from fossunited.doctype_ids import USER_PROFILE


def get_context(context):
    context.foss_user = frappe.get_doc(
        USER_PROFILE,
        {"username": frappe.form_dict["foss_user"]},
    )
