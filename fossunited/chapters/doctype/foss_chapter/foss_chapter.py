# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSChapter(WebsiteGenerator):
    def before_save(self):
        for member in self.chapter_members:
            if member.role == "Lead":
                self.chapter_lead = member.chapter_member
                break
