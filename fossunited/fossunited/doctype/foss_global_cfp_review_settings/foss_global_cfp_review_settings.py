# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FOSSGlobalCFPReviewSettings(Document):
    def before_save(self):
        # assign 'CFP Reviewer' role to all members
        self.assign_reviewer_role()

    def on_update(self):
        # unassign 'CFP Reviewer role to all the members removed
        self.unassign_reviewer_role()

    def assign_reviewer_role(self):
        for member in self.members:
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(
                    "FOSS User Profile", member.profile, "user"
                ),
            )
            user.add_roles("CFP Reviewer")

    def unassign_reviewer_role(self):
        for old_member in self.get_doc_before_save().members:
            if old_member not in self.members:
                user = frappe.get_doc(
                    "User",
                    frappe.db.get_value(
                        "FOSS User Profile",
                        old_member.profile,
                        "user",
                    ),
                )
                user.remove_roles("CFP Reviewer")
