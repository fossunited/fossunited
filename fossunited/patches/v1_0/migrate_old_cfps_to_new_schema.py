import frappe

from fossunited.doctype_ids import PROPOSAL, USER_PROFILE


def execute():
    cfps = frappe.get_all(PROPOSAL, pluck="name", page_length=99999)

    for cfp in cfps:
        doc = frappe.get_doc(PROPOSAL, cfp)

        try:
            linked_user_profile = ""
            if doc.submitted_by:
                linked_user_profile = frappe.db.get_value(
                    USER_PROFILE, {"user": doc.submitted_by}, "name"
                )
            doc.append(
                "speakers",
                {
                    "photo": doc.picture_url or "",
                    "full_name": doc.full_name or "",
                    "email": doc.email or "",
                    "designation": doc.designation or "",
                    "organization": doc.organization or "",
                    "social_link": "",
                    "bio": doc.bio,
                    "linked_user": linked_user_profile or "",
                },
            )
            doc.save()

            if doc.talk_reference:
                doc.append(
                    "references",
                    {
                        "link": doc.talk_reference,
                    },
                )

            doc.save()
        except Exception as e:
            frappe.log_error(f"Error while processing CFP: {cfp}", str(e))
            continue
