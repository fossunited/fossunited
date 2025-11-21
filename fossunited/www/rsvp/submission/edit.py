import frappe
from frappe.utils import get_datetime, getdate

from fossunited.doctype_ids import EVENT, EVENT_RSVP, RSVP_RESPONSE
from fossunited.fossunited.utils import filter_field_values

IGNORE_FIELDNAMES = {
    "confirm_attendance",
    "check_ins",
}

IGNORE_FIELD_LABEL_SECTIONS = {
    "Meta Info",
    "Custom Answers",
}

IGNORE_FIELDTYPES = {
    "Column Break",
}


def get_context(context):
    context.submission = frappe.get_doc(RSVP_RESPONSE, frappe.form_dict.submission)
    context.event = frappe.get_doc(EVENT, context.submission.event)
    frappe.form_dict["rsvp"] = frappe.form_dict.submission
    frappe.form_dict["doctype"] = RSVP_RESPONSE
    context.confirm_attendance = context.submission.confirm_attendance
    context.form_fields = get_form_fields(context.submission.doctype, context.submission)

    # Check-in logic
    context.can_check_in = can_check_in_now(context.event)
    context.checked_in_today = has_checked_in_today(context.submission)
    context.show_check_in_button = context.can_check_in and not context.checked_in_today

    context.no_cache = 1


@frappe.whitelist()
def can_check_in_now(event):
    """Check if check-in is currently allowed for this event"""
    if not event.event_start_date or not event.event_end_date:
        return False

    now = get_datetime()
    start = get_datetime(event.event_start_date)
    end = get_datetime(event.event_end_date)

    return start <= now <= end


def has_checked_in_today(submission):
    """Check if user has already checked in today"""
    if not submission.check_ins:
        return False

    today = getdate()
    for check_in in submission.check_ins:
        if getdate(check_in.check_in_time) == today:
            return True

    return False


def get_form_fields(doctype, submission):
    meta = frappe.get_meta(doctype).as_dict()
    form_fields = []
    current_section = None

    for field in meta["fields"]:
        # Skip unwanted fieldtypes
        if field["fieldtype"] in IGNORE_FIELDTYPES:
            continue

        # Section logic
        if field["fieldtype"] == "Section Break":
            current_section = field.get("label")
            continue

        # Skip entire sections
        if current_section in IGNORE_FIELD_LABEL_SECTIONS:
            continue

        # Skip specific fieldnames
        if field["fieldname"] in IGNORE_FIELDNAMES:
            continue

        # Special case — dynamic label
        if field["fieldname"] == "subscribe_chapter_mailing":
            field["label"] = (
                f"Yes, I'd like to receive updates about future events from {submission.chapter}."
            )

        form_fields.append({k: v for k, v in field.items() if filter_field_values(k)})

    rsvp_doc = frappe.get_doc(EVENT_RSVP, submission.linked_rsvp)

    # Create a mapping of question -> response for quick lookup
    answer_map = {ans.question: ans.response for ans in submission.custom_answers}

    # Iterate through RSVP questions (not submission answers) to avoid duplicates
    for idx, question in enumerate(rsvp_doc.custom_questions, start=1):
        form_fields.append(
            {
                "fieldname": f"custom_question_{idx}",
                "fieldtype": question.type,
                "label": question.question,
                "value": answer_map.get(question.question, ""),
                "options": question.options,
                "reqd": question.is_mandatory or 0,
                "description": question.description,
            }
        )

    return form_fields
