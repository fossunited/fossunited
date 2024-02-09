import frappe
from frappe.website.utils import is_signup_disabled


@frappe.whitelist(allow_guest=True)
def sign_up(username, email, full_name, gender, new_password):
    if is_signup_disabled():
        frappe.throw(_("Sign Up is disabled"), _("Not Allowed"))

    user = frappe.db.get("User", {"email": email})
    if user:
        if user.enabled:
            return 0, "Already Registered"
        else:
            return 0, "Registered but disabled"
    else:
        if frappe.db.get_creation_count("User", 60) > 300:
            frappe.respond_as_web_page(
                title="Temporarily Disabled",
                html="Too many users signed up recently, so the registration is disabled. Please try back in an hour",
                http_status_code=429,
            )

    user = frappe.get_doc(
        {
            "doctype": "User",
            "username": username,
            "email": email,
            "first_name": full_name.split(" ", 1)[0]
            if " " in full_name
            else full_name,
            "last_name": full_name.split(" ", 1)[1]
            if " " in full_name
            else "",
            "country": "",
            "gender": gender,
            "enabled": 1,
            "new_password": new_password,
            "user_type": "Website User",
        }
    )
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.send_welcome_email = 0
    user.flags.no_welcome_email = True
    user.insert()

    # create FOSS User Profile
    foss_profile = frappe.get_doc(
        {
            "doctype": "FOSS User Profile",
            "user": user.name,
            "username": user.username,
            "is_published": 1,
        }
    )
    foss_profile.flags.ignore_permissions = True
    foss_profile.insert()

    frappe.cache.hset(
        "redirect_after_login", user.name, f"/{foss_profile.route}"
    )

    # set default signup role as per Portal Settings
    default_role = frappe.db.get_value(
        "Portal Settings", None, "default_role"
    )
    if default_role:
        user.add_roles(default_role)
    return 1, "Account Created Successfully"
