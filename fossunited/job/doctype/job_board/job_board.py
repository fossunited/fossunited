# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.utils import add_days, now_datetime
from frappe.website.website_generator import WebsiteGenerator


class JobBoard(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        application_link: DF.Data
        company_name: DF.Data
        company_vcs: DF.Data | None
        company_website: DF.Data
        email: DF.Data
        is_published: DF.Check
        job_description: DF.MarkdownEditor | None
        job_location: DF.Data
        job_title: DF.Data
        job_type: DF.Literal["Full Time", "Part Time", "Intern", "Freelance", "Contract"]
        publish_date: DF.Datetime | None
        route: DF.Data | None
        status: DF.Literal["Received", "Approved", "Rejected", "Expired"]
    # end: auto-generated types

    def before_save(self):
        """Auto-generate a route if not set."""
        if not self.route or self.has_value_changed("name"):
            self.route = f"jobs/{self.name}"

        self.handle_publish_status()

    def handle_publish_status(self):
        """
        Automatically publish/unpublish job based on status changes.
        """
        if not self.has_value_changed("status"):
            return

        if self.status == "Approved":
            self.is_published = 1

            if not self.publish_date:
                self.publish_date = now_datetime()

        elif self.status in ["Expired", "Rejected", "Received"]:
            self.is_published = 0

    def get_context(self, context):
        """Context for rendering job detail page"""
        context.title = f"{self.job_title} at {self.company_name}"
        context.posted_on = self.publish_date or self.creation
        context.closed_on = add_days(context.posted_on, 90)
