import io

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils.file_manager import save_file
from PIL import Image

from fossunited.api.dashboard import get_session_user_profile
from fossunited.doctype_ids import CHAPTER, RESTRICTED_USERNAME, USER_PROFILE

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def convert_image_to_webp(image_content: bytes) -> bytes:
    """
    Convert the given image content to WebP format using Pillow.
    Returns the converted image as bytes.
    """
    try:
        with Image.open(io.BytesIO(image_content)) as img:
            img = img.convert("RGB")
            webp_io = io.BytesIO()
            img.save(webp_io, format="WEBP", quality=80)
            return webp_io.getvalue()
    except Image.DecompressionBombError:
        frappe.throw(_("Image exceeds maximum allowed dimensions."))
    except Exception as e:
        frappe.throw(f"Failed to process image: {e!s}")


@frappe.whitelist()
@rate_limit(key="user", limit=10, seconds=300)
def set_profile_image(file_url: str) -> bool:
    """
    Download the image from file_url, convert it to WebP, save it using Frappe's file handling,
    and update the user's profile image.
    """
    user_doc = get_session_user_profile()
    try:
        file_path = frappe.get_site_path("public", file_url.lstrip("/"))
        with open(file_path, "rb") as f:  # nosemgrep: frappe-security-file-traversal
            original_image = f.read()

        if len(original_image) > MAX_IMAGE_SIZE_BYTES:
            frappe.throw(_("Image file size must not exceed 10 MB."))

        webp_image = convert_image_to_webp(original_image)
        filename = f"profile_{user_doc.name}.webp"

        saved_file = save_file(
            fname=filename,
            content=webp_image,
            dt=USER_PROFILE,
            dn=user_doc.name,
            is_private=False,
        )

        frappe.db.set_value(USER_PROFILE, user_doc.name, "profile_photo", saved_file.file_url)
        frappe.db.set_value("User", frappe.session.user, "user_image", saved_file.file_url)
        return True

    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
@rate_limit(key="user", limit=10, seconds=300)
def set_cover_image(file_url: str) -> bool:
    """
    Download the image from file_url, convert it to WebP, save it using Frappe's file handling,
    and update the cover image in the user's profile.
    """
    user_doc = get_session_user_profile()
    try:
        if len(file_url) == 0:
            frappe.db.set_value(USER_PROFILE, user_doc.name, "cover_image", "")
            return True
        file_path = frappe.get_site_path("public", file_url.lstrip("/"))
        with open(file_path, "rb") as f:  # nosemgrep: frappe-security-file-traversal
            original_image = f.read()

        if len(original_image) > MAX_IMAGE_SIZE_BYTES:
            frappe.throw(_("Image file size must not exceed 10 MB."))

        webp_image = convert_image_to_webp(original_image)
        filename = f"cover_{user_doc.name}.webp"

        saved_file = save_file(
            fname=filename,
            content=webp_image,
            dt=USER_PROFILE,
            dn=user_doc.name,
            is_private=False,
        )

        frappe.db.set_value(USER_PROFILE, user_doc.name, "cover_image", saved_file.file_url)
        return True

    except Exception as e:
        frappe.throw(str(e))


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
        frappe.db.exists(CHAPTER, {"route": username})
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
