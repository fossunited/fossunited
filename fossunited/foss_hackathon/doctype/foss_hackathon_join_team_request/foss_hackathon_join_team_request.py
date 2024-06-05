# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FOSSHackathonJoinTeamRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        hackathon: DF.Link | None
        hackathon_name: DF.Data | None
        is_outgoing_request: DF.Check
        reciever_email: DF.Data | None
        requested_by: DF.Link | None
        sender_name: DF.Data | None
        status: DF.Literal["Pending", "Accepted", "Rejected"]
        team: DF.Link | None
        team_name: DF.Data | None
    # end: auto-generated types
    pass

    def before_save(self):
        if self.has_value_changed("status"):
            if self.status == "Accepted":
                self.add_member_to_team()

    def add_member_to_team(self):
        # get participant doc
        try:
            participant_doc = frappe.get_doc(
                "FOSS Hackathon Participant",
                {
                    "email": self.reciever_email,
                    "hackathon": self.hackathon,
                },
            )
        except frappe.DoesNotExistError:
            frappe.throw("Participant not found")
            return

        team_doc = frappe.get_doc("FOSS Hackathon Team", self.team)
        team_doc.append("members", {"member": participant_doc.name})
        team_doc.save()
