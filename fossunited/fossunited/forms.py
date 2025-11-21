import json

import frappe

from fossunited.doctype_ids import PROPOSAL, RSVP_RESPONSE, USER_PROFILE

"""
Some utils and APIs for forms such as RSVP, CFP etc.
"""


def is_valid_doctype(doctype: str):
    """
    Validate the doctype to be either PROPOSAL or RSVP_RESPONSE
    """
    return doctype in (RSVP_RESPONSE, PROPOSAL)


@frappe.whitelist()
def update_submission(doctype, submission, fields, custom):
    """Update submission fields and upsert custom answers (update existing, append new)."""
    if not is_valid_doctype(doctype):
        frappe.log("Unauthorized usage of update_submission")
        frappe.throw("You are not permitted to use this resource", frappe.PermissionError)

    if not check_if_submitter(doctype, submission):
        frappe.throw("You are not authorized to update this submission", frappe.PermissionError)

    fields = json.loads(fields or "{}")
    custom = json.loads(custom or "[]")

    doc = frappe.get_doc(doctype, submission)

    # Update only fields that exist on the doctype (avoid creating unknown fields)
    meta = frappe.get_meta(doctype)
    for k, v in fields.items():
        if meta.get_field(k):
            doc.set(k, v)
        else:
            frappe.logger("rsvp_update").debug(f"Ignored unknown field: {k}")

    # Build map of existing custom answers (question -> row)
    existing = {row.question: row for row in (doc.custom_answers or [])}

    for item in custom:
        q = item.get("question")
        resp = item.get("response")
        ftype = item.get("type")

        if not q:
            continue

        if q in existing:
            row = existing[q]
            row.response = resp
            if ftype is not None:
                row.type = ftype
        else:
            doc.append(
                "custom_answers",
                {
                    "question": q,
                    "response": resp,
                    **({"type": ftype} if ftype is not None else {}),
                },
            )

    doc.save()  # runs validations/hooks
    return {"status": "success"}


@frappe.whitelist()
def check_if_submitter(doctype, docname):
    """
    Check if the current user is the submitter of the given docname.
    Only used for RSVP and CFP
    """
    return frappe.db.get_value(doctype, docname, "submitted_by") == frappe.session.user


@frappe.whitelist()
def post_review(submission, to_approve, remarks):
    """
    Post a review for a particular CFP Submission

    :params submission: CFP Submission docname
    :params to_approve: Reviewer's decision
    :params remarks: Reviewer's remarks
    """
    reviewer = frappe.get_doc(USER_PROFILE, {"email": frappe.session.user})

    submission_doc = frappe.get_doc(PROPOSAL, submission)
    submission_doc.append(
        "reviews",
        {
            "reviewer": reviewer.username,
            "reviewer_profile": reviewer.name,
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
    if not is_valid_doctype(doctype):
        frappe.log("Unauthorized usage of publish_form")
        frappe.throw(
            "You are not permitted to use this resource",
            frappe.PermissionError,
        )

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
    if not is_valid_doctype(doctype):
        frappe.log("Unauthorized usage of unpublish_form")
        frappe.throw(
            "You are not permitted to use this resource",
            frappe.PermissionError,
        )

    doc = frappe.get_doc(doctype, docname)
    doc.is_published = 0
    doc.save(ignore_permissions=True)
    return doc
