import frappe
from frappe.client import set_value
from pydantic import BaseModel

from fossunited.api.dashboard import get_session_user_profile
from fossunited.doctype_ids import RESTRICTED_USERNAME, USER_PROFILE


@frappe.whitelist()
def set_profile_image(file_url: str) -> bool:
    user_doc = get_session_user_profile()
    try:
        frappe.db.set_value(
            USER_PROFILE,
            user_doc.name,
            "profile_photo",
            file_url,
        )
        frappe.db.set_value(
            "User",
            frappe.session.user,
            "user_image",
            file_url,
        )
        return True
    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def set_cover_image(file_url):
    user_doc = get_session_user_profile()
    try:
        frappe.db.set_value(
            USER_PROFILE,
            user_doc.name,
            "cover_image",
            file_url,
        )
        return True
    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def toggle_profile_privacy(value):
    user_doc = get_session_user_profile()
    try:
        frappe.db.set_value(
            USER_PROFILE, user_doc.name, "is_private", value
        )
        return True
    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def update_profile(fields_dict):
    """
    Updates User Profile data.
    Combined with Full Name and Username updates in User doctype,
    whenever these fields are updated.
    """
    user_doc = get_session_user_profile()
    try:
        updated_fields = {
            "full_name": fields_dict.get("full_name"),
            "username": fields_dict.get("username"),
            "route": fields_dict.get("username"),
            "bio": fields_dict.get("bio"),
            "current_city": fields_dict.get("current_city"),
            "about": fields_dict.get("about"),
            "website": fields_dict.get("website"),
            "x": fields_dict.get("x"),
            "linkedin": fields_dict.get("linkedin"),
            "github": fields_dict.get("github"),
            "gitlab": fields_dict.get("gitlab"),
            "instagram": fields_dict.get("instagram"),
            "youtube": fields_dict.get("youtube"),
            "devto": fields_dict.get("devto"),
            "medium": fields_dict.get("medium"),
            "mastodon": fields_dict.get("mastodon"),
        }

        frappe.db.set_value(
            USER_PROFILE, user_doc.name, updated_fields
        )

        user_updates = {}
        if fields_dict.get("full_name") != user_doc.full_name:
            user_updates["full_name"] = fields_dict.get("full_name")

        if fields_dict.get("username") != user_doc.username:
            user_updates["username"] = fields_dict.get("username")

        if user_updates:
            frappe.db.set_value("User", user_doc.user, user_updates)

        return True

    except Exception as e:
        frappe.log_error(
            ("Error updating profile: {0}").format(str(e))
        )
        frappe.throw(
            (
                "An error occurred while updating the profile. Please try again."
            )
        )


@frappe.whitelist()
def is_valid_username(username: str, id: str) -> bool:
    """
    Check if the username is unique and not in restricted list

    Args:
        username: Username to check
        id: ID of the user profile

    Returns:
        bool: True if username is unique and not a restricted username
    """
    if (
        frappe.db.exists("FOSS Chapter", {"route": username})
        or frappe.db.exists(
            USER_PROFILE,
            {"route": username, "name": ["!=", id]},
        )
        or frappe.db.exists(
            RESTRICTED_USERNAME,
            {
                "username": username,
            },
        )
    ):
        return False

    return True
