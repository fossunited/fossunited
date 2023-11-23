# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventCFPSubmission(WebsiteGenerator):
    def before_save(self):
        self.set_route()
        self.is_published = 1

    def set_route(self):
        self.route = f"{self.event}/cfp/{self.name}"
