# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSHackathonTeam(WebsiteGenerator):
    def after_insert(self):
        participant = frappe.db.get_value(
            "FOSS Hackathon Participant",
            {
                "participant_email": frappe.session.user,
                "hackathon_name": self.hackathon_name,
            },
            "name",
        )
        team_owner_doc = frappe.get_doc(
            "FOSS Hackathon Participant", participant
        )
        team_owner_doc.team_name = self.name
        team_owner_doc.is_lead = 1
        team_owner_doc.save()
