import frappe


def get_context(context):
    context.no_cache = 1
    context.event = frappe.get_doc(
        "FOSS Chapter Event",
        {"event_permalink": frappe.form_dict.event_permalink},
        ["*"],
    ).as_dict()

    context.cfp_submissions = frappe.get_all(
        "FOSS Event CFP Submission",
        {"event": context.event.name},
        ["*"],
        page_length=9999,
    )
