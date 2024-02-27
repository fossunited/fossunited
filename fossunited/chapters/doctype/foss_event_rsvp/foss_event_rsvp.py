# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventRSVP(WebsiteGenerator):
    def before_save(self):
        self.set_route()
        self.enable_rsvp_tab()

    def on_update(self):
        if self.rsvp_count >= self.max_rsvp_count:
            self.is_published = 0
        else:
            self.is_published = 1

    def set_route(self):
        event_route = frappe.db.get_value(
            "FOSS Chapter Events", self.event, "route"
        )
        self.route = f"{event_route}/rsvp"

    def enable_rsvp_tab(self):
        frappe.db.set_value(
            "FOSS Chapter Events", self.event, "show_rsvp", 1
        )
