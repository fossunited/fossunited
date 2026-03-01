# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

from fossunited.api.hackathon import get_count_team_members_and_max_count
from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_PARTICIPANT,
    HACKATHON_TEAM,
    HACKATHON_TEAM_MEMBER,
)


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

    def validate(self):
        """Validate runs on both insert and save"""
        self.validate_team_size()
        self.validate_no_duplicate_members()
        self.validate_new_members_not_in_other_teams()

    def before_save(self):
        """Runs on both insert and save"""
        if not self.is_new() and self.has_value_changed("members"):
            team_count = get_count_team_members_and_max_count(self.hackathon, self.name)
            current_members = len(self.members)
            max_size = team_count["max_team_size"]

            if current_members >= max_size:
                frappe.throw(
                    f"Maximum team size of {max_size} members reached. Cannot add more members."
                )

    def on_update(self):
        self.delete_if_empty_team()

    def validate_team_size(self):
        """Check team size limits"""
        max_size = frappe.db.get_value(HACKATHON, self.hackathon, "max_team_members")
        if not max_size:
            return
        if len(self.members) >= max_size:
            frappe.throw(f"Team cannot have more than {max_size} members")

    def validate_no_duplicate_members(self):
        """Ensure no duplicate members in this team"""
        member_ids = [m.member for m in self.members if m.member]
        if len(member_ids) != len(set(member_ids)):
            frappe.throw("Cannot add the same member twice to a team")

    def check_member_not_in_other_team(self, member_id):
        """Check if member is already in another team for this hackathon"""
        other_team = frappe.db.exists(
            HACKATHON_TEAM,
            [
                [HACKATHON_TEAM_MEMBER, "member", "=", member_id],
                ["hackathon", "=", self.hackathon],
                ["name", "!=", self.name],
            ],
        )

        if other_team:
            member_email = frappe.db.get_value(HACKATHON_PARTICIPANT, member_id, "email")
            other_team = frappe.db.get_value(HACKATHON_TEAM, other_team, "team_name")
            frappe.throw(
                f"Member {member_email} is already part of team '{other_team}' in this hackathon"
            )

    def validate_new_members_not_in_other_teams(self):
        """Only validate newly added members"""
        old_doc = self.get_doc_before_save()

        if self.is_new() or not old_doc:
            members_to_check = [m.member for m in self.members if m.member]
        else:
            old_member_ids = {m.member for m in old_doc.members if m.member}
            members_to_check = [
                m.member for m in self.members if m.member and m.member not in old_member_ids
            ]

        for member_id in members_to_check:
            self.check_member_not_in_other_team(member_id)

    def has_permission(self, ptype="read", user=None):
        """Only team members can edit"""

        user = user or frappe.session.user
        if user == "Administrator" or "System Manager" in frappe.get_roles(user):
            return True

        if ptype not in ("write", "delete"):
            return True

        team_name = self.name

        email_member = frappe.db.exists(
            HACKATHON_TEAM_MEMBER,
            {
                "parent": team_name,
                "email": user,
            },
        )
        if email_member:
            return True

        participant_ids = [m.member for m in self.members if m.member]
        if not participant_ids:
            return False

        participant_users = frappe.get_all(
            HACKATHON_PARTICIPANT,
            filters={"name": ["in", participant_ids]},
            pluck="user",
        )

        return user in participant_users

    def delete_if_empty_team(self):
        """Auto-delete team if it becomes empty after having content."""
        prev_doc = self.get_doc_before_save()

        if not prev_doc:
            return
        # Only delete if team had members before
        previously_had_content = bool(
            prev_doc.members or prev_doc.project or prev_doc.partner_project
        )

        if not previously_had_content:
            return

        is_now_empty = not (self.members or self.project or self.partner_project)

        if is_now_empty:
            frappe.delete_doc(
                HACKATHON_TEAM,
                self.name,
                ignore_permissions=True,
                force=True,
            )
