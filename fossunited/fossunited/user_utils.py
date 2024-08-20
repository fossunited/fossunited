import re

import frappe

from fossunited.doctype_ids import USER_PROFILE


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
                "is_published": 1,
            }
        )
        profile.insert(ignore_permissions=True)

    try:
        frappe.db.set_value("User", profile.user, "username", profile.username, update_modified=False)
    except Exception:
        frappe.throw("Error updating username")


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
