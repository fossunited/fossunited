# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSUserProfile(WebsiteGenerator):
    def validate(self):
        self.validate_username()
        self.set_route()

    def validate_username(self):
        self.username = self.username.lower().replace("-", "_")

    def set_route(self):
        self.route = self.username.lower().replace("-", "_")

    def get_context(self, context):
        if self.is_anonymous and frappe.session.user not in [
            "Administrator",
            self.user,
        ]:
            frappe.redirect("/404")
            return

        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(
                experience.as_dict()
            )
        context.experiences_dict = experiences_dict
        context.no_cache = 1

    def on_trash(self):
        frappe.delete_doc("User", self.user, force=True)
