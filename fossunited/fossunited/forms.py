import json

import frappe

"""
Some utils and APIs for forms such as RSVP, CFP etc.
"""


@frappe.whitelist()
def create_submission(fields):
    """
    Used for RSVP and CFPS
    Create a new submission for the given doctype with the given fields.
    Fields variable should have the doctype values as well
    """
    doc = frappe.get_doc(fields)
    doc.insert(ignore_permissions=True)

    return doc


@frappe.whitelist()
def update_submission(doctype, submission, fields, custom):
    """
    Used for RSVP and CFPS
    Update the given submission with the given fields and custom answers
    """
    fields = json.loads(fields)
    custom = json.loads(custom)
    frappe.db.set_value(doctype, submission, fields)

    doc = frappe.get_doc(doctype, submission).as_dict()
    for field in doc.custom_answers:
        frappe.db.set_value(
            "FOSS Custom Answer",
            field.name,
            "response",
            custom[field.idx - 1]["response"],
        )


@frappe.whitelist()
def check_if_submitter(doctype, docname):
    """
    Check if the current user is the submitter of the given docname.
    Only used for RSVP and CFP
    """
    return (
        frappe.db.get_value(doctype, docname, "submitted_by")
        == frappe.session.user
    )


@frappe.whitelist()
def post_review(submission, to_approve, remarks):
    """
    Post a review for a particular CFP Submission

    :params submission: CFP Submission docname
    :params to_approve: Reviewer's decision
    :params remarks: Reviewer's remarks
    """
    reviewer = frappe.get_doc(
        "FOSS User Profile", {"email": frappe.session.user}
    )

    submission_doc = frappe.get_doc(
        "FOSS Event CFP Submission", submission
    )
    submission_doc.append(
        "reviews",
        {
            "reviewer": reviewer.username,
            "email": frappe.session.user,
            "to_approve": to_approve,
            "remarks": remarks,
        },
    )
    submission_doc.save(ignore_permissions=True)


@frappe.whitelist()
def publish_form(doctype, docname):
    """
    Used to Publish RSVP and CFP forms by the user.
    This bypasses the permissions required to publish the form.
    """
    doc = frappe.get_doc(doctype, docname)
    doc.is_published = 1
    doc.save(ignore_permissions=True)
    return doc


@frappe.whitelist()
def unpublish_form(doctype, docname):
    """
    Used to Unpublish RSVP and CFP forms by the user.
    This bypasses the permissions required to unpublish the form.
    """
    doc = frappe.get_doc(doctype, docname)
    doc.is_published = 0
    doc.save(ignore_permissions=True)
    return doc
