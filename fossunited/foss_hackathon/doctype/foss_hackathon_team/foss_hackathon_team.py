# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FOSSHackathonTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hackathon_team_member.foss_hackathon_team_member import (
            FOSSHackathonTeamMember,
        )

        hackathon: DF.Link
        localhost: DF.Link | None
        localhost_request_status: DF.Literal[
            "Pending", "Accepted", "Rejected"
        ]
        members: DF.Table[FOSSHackathonTeamMember]
        partner_project: DF.Link | None
        partner_project_status: DF.Literal[
            "", "Pending", "Accepted", "Rejected"
        ]
        project: DF.Link | None
        team_name: DF.Data
        wants_to_attend_locally: DF.Check
        working_on_partner_project: DF.Check
    # end: auto-generated types
    pass
