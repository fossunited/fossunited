"""Re-sync cached identity copies in chapter rosters after account anonymization.

``FOSS Chapter Lead Team Member`` (``chapter_member``) and ``FOSS Chapter Event
Member`` (``member``) cache ``full_name``/``email`` from the linked profile via
``fetch_from``. The chapter page (``/c/<chapter>``) and the event organizer list
read those cached copies directly, and they don't refresh when the profile is
anonymized — so the person's real name would stay visible there.

When a Personal Data Deletion Request reaches ``Deleted``, point the cached
copies at the (already-anonymized) profile. Wired to the request's ``on_change``
(hooks.py); idempotent.
"""

import frappe

from fossunited.doctype_ids import CHAPTER_MEMBER, EVENT_VOLUNTEER, USER_PROFILE

# roster doctype -> the field linking a row to a FOSS User Profile
ROSTER_LINK_FIELD = {
    CHAPTER_MEMBER: "chapter_member",
    EVENT_VOLUNTEER: "member",
}


def scrub_chapter_rosters(request, method=None):
    if request.status != "Deleted":
        return

    for profile in frappe.get_all(USER_PROFILE, filters={"user": request.name}, pluck="name"):
        anon = frappe.db.get_value(USER_PROFILE, profile, ["full_name", "email"], as_dict=True)
        parents = set()
        for doctype, link_field in ROSTER_LINK_FIELD.items():
            for row in frappe.get_all(
                doctype,
                filters={link_field: profile},
                fields=["name", "parenttype", "parent"],
            ):
                frappe.db.set_value(
                    doctype,
                    row.name,
                    {"full_name": anon.full_name, "email": anon.email},
                )
                parents.add((row.parenttype, row.parent))

        # The chapter/event page reads children from the parent's document cache.
        for parenttype, parent in parents:
            frappe.clear_document_cache(parenttype, parent)
