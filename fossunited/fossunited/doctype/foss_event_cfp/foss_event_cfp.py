# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventCFP(WebsiteGenerator):
    def before_save(self):
        self.set_route()
        self.enable_cfp_tab()

    def set_route(self):
        event_route = frappe.db.get_value(
            "FOSS Chapter Events", self.event, "route"
        )
        self.route = f"{event_route}/cfp"

    def enable_cfp_tab(self):
        frappe.db.set_value(
            "FOSS Chapter Events", self.event, "show_cfp", 1
        )
