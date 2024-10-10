# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

from fossunited.api.hackathon import get_count_team_members_and_max_count


class FOSSHackathonTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hackathon_team_member.foss_hackathon_team_member import (  # noqa: E501
            FOSSHackathonTeamMember,
        )

        hackathon: DF.Link
        looking_for_members: DF.Check
        members: DF.Table[FOSSHackathonTeamMember]
        partner_project: DF.Link | None
        partner_project_status: DF.Literal["", "Pending", "Accepted", "Rejected"]  # noqa: F722, F821
        project: DF.Link | None
        team_name: DF.Data
        working_on_partner_project: DF.Check
    # end: auto-generated types
    pass

    def before_save(self):
        # Handle the case for a newly created team
        if self.is_new():
            return

        if self.has_value_changed("members"):
            team_count = get_count_team_members_and_max_count(self.hackathon, self.name)
            current_members = len(self.members)
            max_size = team_count["max_team_size"]

            if current_members > max_size:
                frappe.throw(
                    f"Maximum team size of {max_size} members reached. Cannot add more members."
                )
