# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FOSSHackathonProject(Document):
    def before_save(self):
        self.set_route()

    def set_route(self):
        hackathon = frappe.get_doc("FOSS Hackathon", self.hackathon)
        self.route = f"{hackathon.route}/p/{self.name}"
