import frappe


def set_unique_username(doc, method):
    full_name = doc.full_name
    doc.first_name = full_name.split(" ")[0]
    doc.last_name = " ".join(full_name.split(" ")[1:])
    doc.username = generate_username(doc.full_name.replace(" ", "_"))


def create_profile_on_user_create(doc, method):
    """
    Automatically Create a FOSS User Profile on User Creation / Signup
    """
    if not frappe.db.exists(
        "FOSS User Profile",
        {"email": doc.email},
    ):
        profile = frappe.get_doc(
            {
                "doctype": "FOSS User Profile",
                "user": doc.name,
                "full_name": doc.full_name,
                "username": doc.username,
                "is_published": 1,
            }
        )
        profile.insert(ignore_permissions=True)


def generate_username(username, count=1):
    """
    Generate a Unique Username
    """
    if frappe.db.exists("FOSS User Profile", {"username": username}):
        return generate_username(username + str(count), count + 1)
    return username
