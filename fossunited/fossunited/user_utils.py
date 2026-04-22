import re

import frappe

from fossunited.doctype_ids import USER_PROFILE

APPROVAL_EMAIL = "dilip@fossunited.org"


def set_unique_username(doc, method):
    full_name = doc.full_name.lower()
    doc.first_name = full_name.split(" ")[0]
    doc.last_name = " ".join(full_name.split(" ")[1:])
    initial_username = re.sub(r"[^a-z0-9_]", "", full_name.replace(" ", "_"))
    doc.username = generate_username(initial_username)


def handle_user_signup(doc, method):
    """
    After insert hook for User:
    - Web signups (Website User): disable + queue for approval + notify
    - Desk-created users: create profile immediately (original behavior)
    """
    if doc.user_type == "Website User":
        # Disable until approved
        frappe.db.set_value("User", doc.name, "enabled", 0, update_modified=False)

        # Notify user: pending
        frappe.sendmail(
            recipients=[doc.email],
            subject="Your FOSS United account is pending approval",
            message=f"""<p>Hi {frappe.utils.escape_html(doc.full_name)},</p>
<p>Thank you for signing up on FOSS United! Your account is currently <strong>pending review</strong> by our team.</p>
<p>We'll email you once approved. This usually takes 1–2 working days.</p>
<p>In case you need account ASAP, please contact us via telegram public channel or mail to <a href="mailto:{APPROVAL_EMAIL}">{APPROVAL_EMAIL}</a>.</p>
<p>— FOSS United Team</p>""",
        )

    else:
        # Desk-created system users: create profile immediately
        _create_profile(doc)


@frappe.whitelist()
def approve_user(user):
    frappe.only_for("System Manager")

    user_doc = frappe.get_doc("User", user)
    already_approved = user_doc.enabled and frappe.db.exists(USER_PROFILE, {"user": user})

    frappe.db.set_value("User", user, "enabled", 1)

    if not frappe.db.exists(USER_PROFILE, {"user": user}):
        _create_profile(user_doc)

    if not already_approved:
        frappe.sendmail(
            recipients=[user_doc.email],
            subject="Your FOSS United account has been approved!",
            message=f"""<p>Hi {frappe.utils.escape_html(user_doc.full_name)},</p>
<p>Your FOSS United account has been <strong>approved</strong>.</p>
<p>You can now <a href="{frappe.utils.get_url()}/login">log in here</a>.</p>
<p>— FOSS United Team</p>""",
        )

    return "approved"


@frappe.whitelist()
def deny_user(user, reason="", notify=True):
    frappe.only_for("System Manager")

    if not frappe.db.exists("User", user):
        return "denied"

    user_doc = frappe.get_doc("User", user)

    if frappe.utils.cint(notify):
        reason_html = (
            f"<p><strong>Reason:</strong> {frappe.utils.escape_html(reason)}</p>" if reason else ""
        )
        frappe.sendmail(
            recipients=[user_doc.email],
            subject="Your FOSS United account signup was not approved",
            message=f"""<p>Hi {frappe.utils.escape_html(user_doc.full_name)},</p>
<p>Unfortunately, your account signup on FOSS United was not approved.</p>
{reason_html}
<p>If you think this is a mistake, contact us at <a href="mailto:{APPROVAL_EMAIL}">{APPROVAL_EMAIL}</a>.</p>
<p>— FOSS United Team</p>""",
        )

    frappe.delete_doc("User", user, ignore_permissions=True, force=True)

    return "denied"


@frappe.whitelist()
def delete_user_and_profile(user):
    frappe.only_for("System Manager")

    if not frappe.db.exists("User", user):
        return "deleted"

    profile_name = frappe.db.get_value(USER_PROFILE, {"user": user}, "name")
    if profile_name:
        # on_trash on FOSSUserProfile also deletes the User — so just delete profile
        frappe.delete_doc(USER_PROFILE, profile_name, ignore_permissions=True, force=True)
    else:
        frappe.delete_doc("User", user, ignore_permissions=True, force=True)

    return "deleted"


def _create_profile(doc):
    """Create FOSS User Profile for a user doc."""
    if frappe.db.exists(USER_PROFILE, {"user": doc.name}):
        return

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

    frappe.db.set_value("User", doc.name, "username", profile.username, update_modified=False)


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
