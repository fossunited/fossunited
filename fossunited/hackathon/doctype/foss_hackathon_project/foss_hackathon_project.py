# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSHackathonProject(WebsiteGenerator):
    def before_save(self):
        self.set_route()

    def set_route(self):
        self.route = f"hackathon/{self.hackathon_permalink_name}/{self.project_name.lower().replace(' ', '-')}"
