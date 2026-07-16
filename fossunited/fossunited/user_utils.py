import re

import frappe
from frappe import _

from fossunited.doctype_ids import DEFAULT_USER_PHOTO, USER_PROFILE

_PROFILE_FIELDS = ["name", "full_name", "profile_photo", "bio", "route", "email"]


def fetch_user_profiles(identifiers, fallback_bio="", force_bio=False):
    """Fetch FOSS User Profiles by email or profile docname. Preserves input order."""
    if not identifiers:
        return []

    emails = [i for i in identifiers if "@" in i]
    names = [i for i in identifiers if "@" not in i]

    found = {}
    if emails:
        for p in frappe.db.get_all(USER_PROFILE, {"email": ["in", emails]}, _PROFILE_FIELDS):
            found[p.email] = p
    if names:
        for p in frappe.db.get_all(USER_PROFILE, {"name": ["in", names]}, _PROFILE_FIELDS):
            found.setdefault(p.name, p)

    result = []
    for identifier in identifiers:
        p = found.get(identifier)
        if p:
            result.append(
                {
                    "full_name": p.full_name,
                    "profile_photo": p.profile_photo or DEFAULT_USER_PHOTO,
                    "bio": fallback_bio if force_bio else (p.bio or fallback_bio),
                    "route": f"/{p.route}" if p.route else "#",
                }
            )
        elif "@" not in identifier:
            # Plain name with no matching profile - show as static card
            result.append(
                {
                    "full_name": identifier,
                    "profile_photo": DEFAULT_USER_PHOTO,
                    "bio": fallback_bio,
                    "route": "#",
                }
            )
    return result


def set_unique_username(doc, method):
    full_name = doc.full_name.lower()
    doc.first_name = full_name.split(" ")[0]
    doc.last_name = " ".join(full_name.split(" ")[1:])
    initial_username = re.sub(r"[^a-z0-9_]", "", full_name.replace(" ", "_"))
    doc.username = generate_username(initial_username)


def create_profile_on_user_create(doc, method):
    """
    Automatically Create a FOSS User Profile on User Creation / Signup
    """
    if not frappe.db.exists(
        USER_PROFILE,
        {"email": doc.email},
    ):
        profile = frappe.get_doc(
            {
                "doctype": USER_PROFILE,
                "user": doc.name,
                "full_name": doc.full_name,
                "username": doc.username,
                "is_published": 0,
            }
        )
        profile.insert(ignore_permissions=True)

    try:
        frappe.db.set_value(
            "User", profile.user, "username", profile.username, update_modified=False
        )
    except Exception as e:
        frappe.throw(_(f"Error updating username. Error: {e}"))


def generate_username(username, count=1):
    """
    Generate a Unique Username between 3 and 30 characters
    """
    if len(username) < 3:
        username = username.ljust(3, "_")

    username = username[:30]
    if frappe.db.exists(USER_PROFILE, {"username": username}):
        return generate_username(username.lower() + str(count), count + 1)
    return username
