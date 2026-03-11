# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

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

    def on_update(self):
        self.update_member_team_links()
        self.auto_delete_if_empty()

    def on_trash(self):
        """Clear team link when team is deleted"""
        for participant in self.members:
            if participant.member:
                frappe.db.set_value(
                    HACKATHON_PARTICIPANT,
                    participant.member,
                    "team",
                    None,
                    update_modified=False,
                )

    def validate_team_size(self):
        """Check team size limits"""
        max_size = frappe.db.get_value(HACKATHON, self.hackathon, "max_team_members")
        if not max_size:
            return

        old_doc = self.get_doc_before_save()

        if old_doc and len(self.members) <= len(old_doc.members):
            return

        if len(self.members) > max_size:
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

    def auto_delete_if_empty(self):
        """Delete team if it has no members or no project"""
        if frappe.flags.in_test:
            return
        has_content = bool(self.members or self.project or self.partner_project)
        if not has_content:
            frappe.db.after_commit.add(lambda: delete_team_if_exists(self.name))

    def update_member_team_links(self):
        """Update team link for added members, clear for removed members"""
        old_doc = self.get_doc_before_save()

        # Get current member IDs
        current_member_ids = {m.member for m in self.members if m.member}

        # Get previous member IDs
        old_member_ids = set()
        if old_doc:
            old_member_ids = {m.member for m in old_doc.members if m.member}

        # Added members: Set team link
        added_members = current_member_ids - old_member_ids
        for member_id in added_members:
            frappe.db.set_value(
                HACKATHON_PARTICIPANT,
                member_id,
                "team",
                self.name,
                update_modified=False,
            )

        # Removed members: Clear team link
        removed_members = old_member_ids - current_member_ids
        for member_id in removed_members:
            frappe.db.set_value(
                HACKATHON_PARTICIPANT,
                member_id,
                "team",
                None,
                update_modified=False,
            )


def delete_team_if_exists(team_name):
    """Helper function to delete team"""
    try:
        if frappe.db.exists(HACKATHON_TEAM, team_name):
            frappe.delete_doc(
                HACKATHON_TEAM,
                team_name,
                ignore_permissions=True,
                force=True,
            )
    except Exception:
        pass
