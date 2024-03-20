import frappe

from fossunited.fossunited.utils import filter_field_values


def get_context(context):
    context.submission = frappe.get_doc(
        "FOSS Event RSVP Submission", frappe.form_dict.submission
    )
    context.event = frappe.get_doc(
        "FOSS Chapter Event", context.submission.event
    )
    frappe.form_dict["rsvp"] = frappe.form_dict.submission
    frappe.form_dict["doctype"] = "FOSS Event RSVP Submission"
    context.form_fields = get_form_fields(
        context.submission.doctype, context.submission
    )
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
        if current_section in ["Meta Info", "Custom Answers"]:
            continue
        form_fields.append(
            {k: v for k, v in field.items() if filter_field_values(k)}
        )

    rsvp_doc = frappe.get_doc(
        "FOSS Event RSVP", submission.linked_rsvp
    )
    for question in submission.custom_answers:
        form_fields.append(
            {
                "fieldname": f"custom_question_{question.idx}",
                "fieldtype": question.type,
                "label": question.question,
                "value": question.response,
                "options": rsvp_doc.custom_questions[
                    question.idx - 1
                ].options,
                "reqd": rsvp_doc.custom_questions[
                    question.idx - 1
                ].is_mandatory
                or 0,
                "description": rsvp_doc.custom_questions[
                    question.idx - 1
                ].description,
            }
        )

    return form_fields
