import frappe

from fossunited.doctype_ids import EVENT_CFP, PROPOSAL
from fossunited.fossunited.utils import filter_field_values


def get_context(context):
    context.submission = frappe.get_doc(PROPOSAL, frappe.form_dict["submission"])
    context.cfp = frappe.get_doc(EVENT_CFP, context.submission.linked_cfp)
    context.event = frappe.get_doc("FOSS Chapter Event", context.submission.event)

    frappe.form_dict["doctype"] = PROPOSAL
    frappe.form_dict["cfp"] = frappe.form_dict.submission
    context.form_fields = get_form_fields(context.submission.doctype, context.submission)
    context.no_cache = 1


def get_form_fields(doctype, submission):
    meta = frappe.get_meta(doctype).as_dict()
    form_fields = []
    current_section = None
    for field in meta["fields"]:
        if field["fieldtype"] == "Column Break":
            continue
        if field["fieldtype"] == "Section Break":
            current_section = field["label"]
            continue
        if current_section in [
            "Meta Info",
            "Custom Answers",
            "CFP Reviews",
            "Review Scores",
        ]:
            continue
        form_fields.append({k: v for k, v in field.items() if filter_field_values(k)})

    cfp_doc = frappe.get_doc(EVENT_CFP, submission.linked_cfp)
    for question in submission.custom_answers:
        form_fields.append(
            {
                "fieldname": f"custom_question_{question.idx}",
                "fieldtype": question.type,
                "label": question.question,
                "value": question.response,
                "options": cfp_doc.cfp_custom_questions[question.idx - 1].options,
                "reqd": cfp_doc.cfp_custom_questions[question.idx - 1].is_mandatory or 0,
                "description": cfp_doc.cfp_custom_questions[question.idx - 1].description,
            }
        )

    return form_fields
