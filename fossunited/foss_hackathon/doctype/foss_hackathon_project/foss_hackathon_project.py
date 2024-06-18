# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.fossunited.utils import get_doc_likes


class FOSSHackathonProject(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        demo_link: DF.Data | None
        description: DF.TextEditor
        hackathon: DF.Link
        is_contribution_project: DF.Check
        is_partner_project: DF.Check
        is_published: DF.Check
        partner_project: DF.Link | None
        repo_link: DF.Data | None
        route: DF.Data | None
        short_description: DF.SmallText | None
        team: DF.Link
        team_name: DF.Data | None
        title: DF.Data

    # end: auto-generated types
    def before_save(self):
        self.set_route()

    def set_route(self):
        hackathon = frappe.get_doc("FOSS Hackathon", self.hackathon)
        self.route = f"{hackathon.route}/p/{self.name}"

    def get_context(self, context):
        context.no_cache = 1
        context.hackathon = frappe.get_doc(
            "FOSS Hackathon", self.hackathon
        )
        context.nav_items = ["description", "team_members"]

        context.team = frappe.get_doc(
            "FOSS Hackathon Team", self.team
        )
        context.team_members = get_team_members(context.team)
        context.likes = get_doc_likes(self.doctype, self.name)
        context.liked_by_user = frappe.session.user in context.likes


def get_team_members(team):
    member_details = []
    for member in team.members:
        user = frappe.get_doc(
            "FOSS User Profile", {"user": member.member}, ["*"]
        ).as_dict()
        member_details.append(user)
    return member_details
