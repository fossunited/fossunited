# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
import json

import frappe
from frappe.model.document import Document


class ConferenceTickets(Document):
    # function to validate the payment.
    def on_update(self):
        if self.payment_captured == True:
            self.add_user_to_list()

    def add_user_to_list(self):
        print(self.event_name)
        details = frappe.get_doc('Conference Tickets', self.name )

        add_user = frappe.get_doc({
            'doctype': 'Email Group Member',
            'email_group': details.event_name, 
            'email': details.email 
        }).insert(ignore_permissions=True)