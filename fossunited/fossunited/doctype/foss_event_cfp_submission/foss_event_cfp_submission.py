# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventCFPSubmission(WebsiteGenerator):
    def before_save(self):
        self.set_route()

    def set_route(self):
        event_route = frappe.db.get_value(
            "FOSS Chapter Events", self.event, "route"
        )
        self.route = f"{event_route}/cfp/{self.name}"
