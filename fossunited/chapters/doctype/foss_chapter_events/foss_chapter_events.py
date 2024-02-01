# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSChapterEvents(WebsiteGenerator):
    def on_update(self):
        if self.status == "Approved":
            self.create_email_group()

        if self.status == "Cancelled":
            self.delete_email_group()

    def create_email_group(self):
        new_list = frappe.new_doc("Email Group")
        new_list.title = self.event_name
        new_list.insert()

    def delete_email_group(self):
        del_list = frappe.delete_doc("Email Group", self.event_name)
