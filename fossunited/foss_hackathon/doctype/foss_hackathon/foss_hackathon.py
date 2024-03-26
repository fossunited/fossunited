# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FOSSHackathon(Document):
    def before_save(self):
        self.set_route()

    def set_route(self):
        if self.permalink:
            self.route = f"hack/{self.permalink}"
        else:
            self.route = f'hack/{self.hackathon_name.to_lower().replace(" ", "-")}'
