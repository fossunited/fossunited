import frappe

from fossunited.doctype_ids import CHAPTER, EVENT


def execute():
    """
    This patch updates all documents of the specified doctypes to remove the 'Lead' role
    and convert them to 'Core Team Member' role for the respective members attribute.
    """

    # Map doctype to the member attribute name
    doctype_members_map = {CHAPTER: "chapter_members", EVENT: "event_members"}

    for doctype, members_attr in doctype_members_map.items():
        docnames = frappe.get_all(doctype, pluck="name")

        try:
            for docname in docnames:
                doc = frappe.get_doc(doctype, docname)
                updated = False

                members = getattr(doc, members_attr, [])
                for member in members:
                    if member.role == "Lead":
                        # Convert role value
                        member.role = "Core Team Member"
                        updated = True

                        """
                        # Revoke legacy 'Chapter Lead' user role
                        user = frappe.db.get_value(USER_PROFILE, member.chapter_member, "user")
                        if user:
                            frappe.db.delete(
                                "Has Role",
                                {"parent": user, "parenttype": "User", "role": "Chapter Lead"},
                            )
                        """

                if updated:
                    doc.save()
                    # Commit after each doc to keep changes granular; acceptable for one-off patch
                    frappe.db.commit()
                    frappe.logger().info(f"Updated {doctype} {docname}: Lead roles.")

        except Exception:
            frappe.log_error(
                title=f"Error changing roles for doctype {doctype}",
                message=frappe.get_traceback(),
            )
