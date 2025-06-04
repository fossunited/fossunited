import frappe

from fossunited.doctype_ids import EVENT, EVENT_CFP, PROPOSAL
from fossunited.id.roles import REVIEWER


@frappe.whitelist(allow_guest=True)
def get_cfp_from_route(route: str) -> dict:
    event = frappe.db.get_value(
        EVENT,
        {"route": f"c/{route}"},
        [
            "route",
            "name",
            "event_name",
            "event_logo",
            "event_location",
            "event_start_date",
            "event_end_date",
        ],
        as_dict=True,
    )

    cfp = frappe.get_doc(EVENT_CFP, {"event": event.name}).as_dict()
    cfp.event = event

    return cfp


@frappe.whitelist(allow_guest=True)
def get_global_cfp_guidelines() -> dict:
    """
    Get the global CFP guidelines.
    """
    return frappe.db.get_value("Global CFP Settings", None, "guidelines", as_dict=True)


@frappe.whitelist()
def get_proposal_filter_fields(event_id: str) -> list:
    fields = frappe.get_meta(PROPOSAL).fields

    fieldtypes_to_remove = ["Section Break", "Tab Break", "Column Break"]
    fields_to_remove = [
        "is_published",
        "route",
        "linked_cfp",
        "chapter",
        "event",
        "submitted_by",
        "event_name",
        "attendance_confirmed",
        "first_name",
        "last_name",
        "talk_reference",
        "full_name",
        "email",
        "picture_url",
        "designation",
        "organization",
        "bio",
        "positive_reviews",
        "negative_reviews",
        "unsure_reviews",
        "approvability",
    ]

    fieldnames_to_remove = set(fields_to_remove)
    filtered_fields = [
        field
        for field in fields
        if field.fieldtype not in fieldtypes_to_remove
        and field.fieldname not in fieldnames_to_remove
    ]

    cfp = frappe.get_doc(EVENT_CFP, {"event": event_id})

    for question in cfp.cfp_custom_questions:
        custom_field = {
            "fieldname": "custom_question_" + str(question.idx),
            "fieldtype": question.type,
            "label": question.question + " (Custom question)",
            "options": question.options,
            "reqd": question.is_mandatory or 0,
            "description": question.description,
        }

        filtered_fields.append(custom_field)

    if REVIEWER in frappe.get_roles(frappe.session.user):
        # appending _is_reviewed field
        filtered_fields[:0] = [
            {
                "fieldname": "_is_reviewed",
                "fieldtype": "Check",
                "label": "Only show reviewed (By Me)",
                "reqd": 0,
            },
            {
                "fieldname": "_is_not_reviewed",
                "fieldtype": "Check",
                "label": "Only show not reviewed (By Me)",
                "reqd": 0,
            },
        ]

    return filtered_fields
