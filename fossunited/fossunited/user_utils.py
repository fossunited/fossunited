import re

import frappe

from fossunited.doctype_ids import USER_PROFILE

APPROVAL_EMAIL = "dilip@fossunited.org"


def set_unique_username(doc: "frappe.Document", method: str | None) -> None:
    full_name = doc.full_name.lower()
    doc.first_name = full_name.split(" ")[0]
    doc.last_name = " ".join(full_name.split(" ")[1:])
    initial_username = re.sub(r"[^a-z0-9_]", "", full_name.replace(" ", "_"))
    doc.username = generate_username(initial_username)


def handle_user_signup(doc: "frappe.Document", method: str | None) -> None:
    """
    After insert hook for User:
    - Web signups (Website User): disable + persist username + queue for approval + notify
    - Desk-created users: create profile immediately (original behavior)
    """
    if doc.user_type == "Website User" and not doc.flags.get("skip_approval_flow"):
        frappe.db.set_value("User", doc.name, "enabled", 0, update_modified=False)
        # set_unique_username sets doc.username in memory only - persist it so
        # approve_user / _create_profile receive the correct username later
        frappe.db.set_value("User", doc.name, "username", doc.username, update_modified=False)

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
        _create_profile(doc)


@frappe.whitelist()
def approve_user(user: str) -> str:
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
def deny_user(user: str, reason: str = "", notify: bool = True) -> str:
    frappe.only_for("System Manager")

    user_exists = frappe.db.exists("User", user)

    if user_exists and frappe.utils.cint(notify):
        user_doc = frappe.get_doc("User", user)
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

    # Delete profiles first; FOSSUserProfile.on_trash applies to User
    for profile in frappe.get_all(USER_PROFILE, filters={"user": user}, pluck="name"):
        frappe.delete_doc(USER_PROFILE, profile, ignore_permissions=True, force=True)

    # User may already be gone via on_trash; delete if still present
    if frappe.db.exists("User", user):
        frappe.delete_doc("User", user, ignore_permissions=True, force=True)

    return "denied"


@frappe.whitelist()
def delete_user_and_profile(user: str) -> str:
    frappe.only_for("System Manager")

    # Delete profiles first; on_trash applies to User
    for profile in frappe.get_all(USER_PROFILE, filters={"user": user}, pluck="name"):
        frappe.delete_doc(USER_PROFILE, profile, ignore_permissions=True, force=True)

    if frappe.db.exists("User", user):
        frappe.delete_doc("User", user, ignore_permissions=True, force=True)

    return "deleted"


def _create_profile(doc: "frappe.Document") -> None:
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


def generate_username(username: str, count: int = 1) -> str:
    """Generate a unique username between 3 and 30 characters."""
    if len(username) < 3:
        username = username.ljust(3, "_")

    username = username[:30]
    if frappe.db.exists(USER_PROFILE, {"username": username}) or frappe.db.exists(
        "User", {"username": username}
    ):
        return generate_username(username.lower() + str(count), count + 1)
    return username
