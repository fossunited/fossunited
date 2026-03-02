# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_ISSUE_PR,
    HACKATHON_PROJECT,
    HACKATHON_TEAM_MEMBER,
)


class FOSSHackathonPartnerProject(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.hackathon_project_issue_pr.hackathon_project_issue_pr import (  # noqa: E501
            HackathonProjectIssuePR,
        )

        about: DF.SmallText | None
        description: DF.MarkdownEditor | None
        hackathon: DF.Link | None
        is_published: DF.Check
        issue_pr_table: DF.Table[HackathonProjectIssuePR]
        logo: DF.AttachImage | None
        poc_email: DF.Data | None
        project_name: DF.Data | None
        repo_link: DF.Data | None
        route: DF.Data | None
    # end: auto-generated types

    def before_save(self):
        self.set_route()

    def set_route(self):
        """route as /fosshack/year/partner-project/project_name"""
        start_date = frappe.db.get_value(HACKATHON, self.hackathon, "start_date")
        event_year = str(start_date.year)
        self.route = f"fosshack/{event_year}/partner-projects/{frappe.scrub(self.project_name)}"

    def get_context(self, context):
        """Enhance the web page context with additional data"""
        context.no_cache = 1

        hackathon = frappe.get_doc(HACKATHON, self.hackathon)
        context.hackathon = hackathon

        # Get all participant projects linked to this partner project
        participant_projects = frappe.get_all(
            HACKATHON_PROJECT,
            filters={
                "hackathon": self.hackathon,
                "partner_project": self.name,
                "is_published": 1,
            },
            fields=["name", "title", "short_description", "route", "team"],
            order_by="creation desc",
        )

        # Enrich participant projects with team size and likes
        for project in participant_projects:
            # Get team size
            project.team_size = frappe.db.count(
                HACKATHON_TEAM_MEMBER, filters={"parent": project.team}
            )
            project.contributions = frappe.db.count(
                HACKATHON_ISSUE_PR, filters={"parent": project.name}
            )

        context.participant_projects = participant_projects

        return context
