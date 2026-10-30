"""Finish FOSS User Profile anonymization for a completed deletion request.

Frappe's ``user_data_fields`` hook (see hooks.py) redacts the profile's plain
Data fields and renames the User. This handler covers what that mechanism can't
express cleanly, once the request reaches ``Deleted``:

* Fields whose type-based placeholder would be broken are cleared to ``None``
  instead of the literal field name: images (``profile_photo``/``cover_image``),
  the ``current_city`` Link, and the long-text ``bio``/``about``.
* The profile's own child rows (education, work experience, projects, skills) are
  pure PII with no incoming links, so they are deleted rather than redacted.
* The profile is unpublished and its name-derived ``username``/``route`` are
  regenerated, so ``/u/<username>`` 404s and no public listing exposes the person.
* Uploaded ``File`` records attached to the profile are deleted; otherwise the
  photos stay publicly downloadable at ``/files/...``.

Wired to the request's ``on_change`` (hooks.py); it is idempotent and only acts
once the status is ``Deleted``.
"""

import frappe

from fossunited.doctype_ids import USER_PROFILE

# Redacting these would leave a broken placeholder (a broken image src, a dangling
# City link, or the literal "bio"/"about"), so clear them instead of redacting.
PROFILE_NULL_FIELDS = ("profile_photo", "cover_image", "current_city", "bio", "about")

# Child tables owned entirely by the profile, with nothing linking in -> delete.
PROFILE_CHILD_DOCTYPES = (
    "FOSS User Profile Education",
    "FOSS User Profile Work Experience",
    "FOSS User Projects",
    "FOSS User Skill Multiselect",
)


def finalize_profile_anonymization(request, method=None):
    """Delete child rows, clear broken fields, unpublish, and drop uploaded files
    for the profile of a Deleted Personal Data Deletion Request."""
    if request.status != "Deleted":
        return

    profiles = frappe.get_all(USER_PROFILE, filters={"user": request.name}, pluck="name")
    for profile in profiles:
        _finalize(profile)


def _finalize(profile):
    # Keep the token stable across re-runs so on_change firing more than once
    # stays idempotent (child/file deletes below are naturally idempotent).
    username = frappe.db.get_value(USER_PROFILE, profile, "username") or ""
    token = (
        username
        if username.startswith("deleted_")
        else f"deleted_{frappe.generate_hash(length=12)}"
    )
    frappe.db.set_value(
        USER_PROFILE,
        profile,
        {
            **dict.fromkeys(PROFILE_NULL_FIELDS, None),
            "is_published": 0,
            "is_private": 1,
            # username/route are derived from the person's name; regenerate both to
            # a safe token so the public route no longer leaks it.
            "username": token,
            "route": f"u/{token}",
        },
        modified_by="Administrator",
    )

    # The profile normally syncs its username to the User, but we wrote via
    # db.set_value (no on_update), so clear the handle on the User too — it's the
    # person's chosen name and Frappe's rename leaves User.username intact.
    user = frappe.db.get_value(USER_PROFILE, profile, "user")
    if user:
        frappe.db.set_value("User", user, "username", token, modified_by="Administrator")

    for doctype in PROFILE_CHILD_DOCTYPES:
        frappe.db.delete(doctype, {"parenttype": USER_PROFILE, "parent": profile})

    for file in frappe.get_all(
        "File",
        filters={"attached_to_doctype": USER_PROFILE, "attached_to_name": profile},
        pluck="name",
    ):
        frappe.delete_doc("File", file, force=True, ignore_permissions=True)

    frappe.clear_document_cache(USER_PROFILE, profile)
