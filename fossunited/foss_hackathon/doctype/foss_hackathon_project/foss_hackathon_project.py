# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_PARTICIPANT,
    HACKATHON_PARTNER_PROJECT,
    HACKATHON_PROJECT,
    HACKATHON_TEAM,
    USER_PROFILE,
)
from fossunited.fossunited.utils import get_doc_likes, sanitize_text_content


class FOSSHackathonProject(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.hackathon_project_issue_pr.hackathon_project_issue_pr import (
            HackathonProjectIssuePR,
        )

        demo_link: DF.Data | None
        description: DF.TextEditor
        hackathon: DF.Link
        is_contribution_project: DF.Check
        is_partner_project: DF.Check
        is_published: DF.Check
        issue_pr_table: DF.Table[HackathonProjectIssuePR]
        license: DF.Data | None
        partner_project: DF.Link | None
        repo_link: DF.Data | None
        route: DF.Data | None
        short_description: DF.SmallText | None
        team: DF.Link
        team_name: DF.Data | None
        title: DF.Data

    # end: auto-generated types
    def validate(self):
        """Validate project data"""
        self.check_hackathon_not_ended()
        self.description = sanitize_text_content(self.description)
        self.validate_one_project_per_team()
        self.validate_team_belongs_to_hackathon()

    def before_save(self):
        self.set_route()

    def check_hackathon_not_ended(self):
        """Raise PermissionError if hackathon has ended (System Manager/Administrator bypass)"""
        user = frappe.session.user
        if user == "Administrator" or "System Manager" in frappe.get_roles(user):
            return
        end_date = frappe.db.get_value(HACKATHON, self.hackathon, "end_date")
        if end_date and frappe.utils.now_datetime() > frappe.utils.get_datetime(end_date):
            frappe.throw(
                frappe._("The hackathon has ended. Project cannot be modified."),
                frappe.PermissionError,
            )

    def set_route(self):
        hackathon = frappe.get_doc(HACKATHON, self.hackathon)
        self.route = f"{hackathon.route}/p/{self.name}"

    def validate_one_project_per_team(self):
        """Ensure only one project per team"""
        if self.is_new():
            existing = frappe.db.exists(
                HACKATHON_PROJECT,
                {
                    "hackathon": self.hackathon,
                    "team": self.team,
                    "name": ["!=", self.name],
                },
            )
            if existing:
                frappe.throw(_("This team already has a project for this hackathon"))

    def validate_team_belongs_to_hackathon(self):
        """Ensure team belongs to the same hackathon"""
        team_hackathon = frappe.db.get_value(HACKATHON_TEAM, self.team, "hackathon")
        if team_hackathon != self.hackathon:
            frappe.throw(_("Team does not belong to this hackathon"))

    def has_permission(self, ptype="read", user=None):
        """Only team members can edit/delete project"""
        user = user or frappe.session.user
        # everyone can read
        if ptype not in ["write", "delete"]:
            return True
        if user == "Administrator" or "System Manager" in frappe.get_roles(user):
            return True

        if not self.team:
            return False

        team_doc = frappe.get_doc(HACKATHON_TEAM, self.team)

        team_emails = {m.email for m in team_doc.members if m.email}
        if user in team_emails:
            return True

        participant_ids = [m.member for m in team_doc.members if m.member]
        if not participant_ids:
            return False

        participant_users = frappe.get_all(
            HACKATHON_PARTICIPANT,
            filters={"name": ["in", participant_ids]},
            pluck="user",
        )

        return user in participant_users

    def get_context(self, context):
        context.no_cache = 1
        context.hackathon = frappe.get_doc(HACKATHON, self.hackathon)

        context.team = frappe.get_doc(HACKATHON_TEAM, self.team)
        context.team_members = self.get_team_members(context.team)
        context.likes = get_doc_likes(self.doctype, self.name)
        context.liked_by_user = frappe.session.user in context.likes

        context.winner_status = frappe.db.get_value(
            "Hackathon Result",
            {"parent": self.hackathon, "project": self.name},
            "status",
        )
        context.results_route = "/fosshack/results?year=2026"

        if self.is_partner_project:
            context.partner_project = frappe.get_doc(
                HACKATHON_PARTNER_PROJECT, self.partner_project
            )

    @staticmethod
    def get_team_members(team):
        member_details = []
        for member in team.members:
            profile_id = frappe.db.get_value(
                HACKATHON_PARTICIPANT,
                member.member,
                "user_profile",
            )
            profile = frappe.db.get_value(
                USER_PROFILE,
                profile_id,
                ["route", "full_name", "username", "profile_photo"],
                as_dict=True,
            )
            member_details.append(profile)
        return member_details
