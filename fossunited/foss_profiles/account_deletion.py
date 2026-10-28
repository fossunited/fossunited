"""Profile child data that cannot be matched by email in user_data_fields."""

import frappe

from fossunited.doctype_ids import USER_PROFILE

PROFILE_CHILD_FIELDS = {
    "FOSS User Profile Education": [
        "institution",
        "degree",
        "field_of_study",
        "start_year",
        "end_year",
    ],
    "FOSS User Profile Work Experience": [
        "title",
        "company",
        "company_website",
        "city",
        "country",
        "description",
        "start_date",
        "end_date",
    ],
    "FOSS User Projects": ["project_name", "tagline", "project_link", "cover_image"],
}


def redact_profile_children(request, method=None):
    """Redact by profile membership after Frappe completes account anonymization.

    Child-row owners identify the editor, who may be an administrator or another
    user. Matching their parent instead keeps unrelated profiles untouched.
    Frappe calls on_change when it db_sets the request status to Deleted.
    """
    if request.status != "Deleted":
        return

    profiles = frappe.get_all(USER_PROFILE, filters={"user": request.name}, pluck="name")
    if not profiles:
        return

    for doctype, fields in PROFILE_CHILD_FIELDS.items():
        values = request.generate_anonymization_dict({"doctype": doctype, "redact_fields": fields})
        rows = frappe.get_all(
            doctype,
            filters={"parenttype": USER_PROFILE, "parent": ["in", profiles]},
            pluck="name",
        )
        for name in rows:
            frappe.db.set_value(doctype, name, values, modified_by="Administrator")

    for profile in profiles:
        frappe.clear_document_cache(USER_PROFILE, profile)
