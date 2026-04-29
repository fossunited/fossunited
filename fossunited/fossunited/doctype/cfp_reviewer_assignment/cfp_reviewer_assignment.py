# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CFPReviewerAssignment(Document):
    def after_insert(self):
        # Email notification to reviewer logic
        # Implement Pretalx's notification hook here
        reviewer_doc = frappe.get_doc("FOSS User Profile", self.reviewer)
        proposal_doc = frappe.get_doc("FOSS Event CFP Submission", self.proposal)
        
        # In a real app we would use frappe.sendmail or frappe templates
        # frappe.sendmail(...)
        pass
