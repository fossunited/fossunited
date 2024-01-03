# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSUserProfile(WebsiteGenerator):
    def get_context(self, context):
        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(
                experience.as_dict()
            )
        context.experiences_dict = experiences_dict
