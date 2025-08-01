# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import markdown, sanitize_html
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import (
    EVENT,
    EVENT_SPONSOR,
    HACKATHON,
    JOB,
    JOB_STATUS_APPROVED,
    JOB_STATUS_EXPIRED,
    USER_PROFILE,
)


class Organization(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        bluesky: DF.Data | None
        country_of_origin: DF.Data | None
        discord: DF.Data | None
        discourse: DF.Data | None
        github: DF.Data | None
        instagram: DF.Data | None
        linkedin: DF.Data | None
        mastodon: DF.Data | None
        matrix: DF.Data | None
        org_about: DF.MarkdownEditor
        org_banner: DF.AttachImage | None
        org_email: DF.Data
        org_lead: DF.Link | None
        org_logo: DF.AttachImage | None
        org_name: DF.Data
        org_type: DF.Data | None
        org_website: DF.Data
        published: DF.Check
        route: DF.Data | None
        telegram: DF.Data | None
        x: DF.Data | None
        youtube: DF.Data | None
        # end: auto-generated types

    def get_social_links(self):
        socials = {}
        # Get social fields from type annotations to stay in sync
        # D_TODO: Consider making social fields configurable.
        # or better get these svgs into assets dir rather than external calls
        social_fields = [
            "github",
            "x",
            "bluesky",
            "discord",
            "discourse",
            "instagram",
            "linkedin",
            "mastodon",
            "matrix",
            "telegram",
            "youtube",
        ]

        for field in social_fields:
            value = getattr(self, field, None)
            if value:
                if field == "matrix":
                    display_name = "matrix-light"
                elif field == "github":
                    display_name = "github_light"
                else:
                    display_name = field

                socials[display_name] = value

        return socials

    def get_members(self):
        members = []
        org_members = frappe.get_all(USER_PROFILE, filters={"org_link": self.org_name})

        for member in org_members:
            try:
                # Get the actual document object
                profile = frappe.get_doc(USER_PROFILE, member.name)
            except frappe.DoesNotExistError:
                # Skip members with missing profiles
                continue

            members.append(
                {
                    "full_name": profile.full_name,
                    "role": profile.org_role,
                    "profile_picture": (
                        profile.profile_photo
                        or "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.route,
                }
            )

        return members

    def get_org_jobs(self, status):
        """
        Simple enough function to fetch jobs from this organization (company_name).
        """
        return frappe.get_all(
            JOB, filters={"status": status, "company_name": self.org_name}, fields=["*"]
        )

    def get_sponsored_docs(
        self,
        doctype,
        type=None,
        limit=999,
    ):
        """
        Fetch docs (Event, Hackathon, etc.) sponsored by this Organization.

        Parameters:
            doctype (str): Main doctype (e.g., "Event", "FOSS Hackathon")
            type (str): "past", "now", or None
            status (str): Optional status filter for events
            limit (int): Number of records to fetch
            fields (list): Optional list of fields to fetch

        Returns:
            List of dicts containing the sponsored venue
        """

        sponsor_name = self.org_name

        sponsored_docs = frappe.get_all(
            EVENT_SPONSOR, filters={"sponsor_name": sponsor_name}, pluck="parent"
        )

        if not sponsored_docs:
            return []

        filters = {"name": ["in", sponsored_docs]}

        time_now = frappe.utils.now()

        if doctype == EVENT:
            if type == "past":
                filters.update({"event_end_date": ("<", time_now), "status": "Concluded"})
            else:
                filters.update({"event_end_date": (">=", time_now), "status": "Live"})

        elif doctype == HACKATHON:
            if type == "past":
                filters.update({"is_published": 1, "end_date": ["<", time_now]})
            else:
                filters.update({"is_published": 1, "end_date": [">=", time_now]})

        return frappe.get_all(
            doctype,
            filters=filters,
            fields=["*"],
            # order_by=order,
            page_length=limit,
        )

    def get_context(self, context):
        context.members = self.get_members()
        context.social_links = self.get_social_links()
        context.org_active_jobs = self.get_org_jobs(JOB_STATUS_APPROVED)
        context.org_expired_jobs = self.get_org_jobs(JOB_STATUS_EXPIRED)

        context.past_sponsored_events = self.get_sponsored_docs(doctype=EVENT, type="past")

        context.present_sponsored_events = self.get_sponsored_docs(doctype=EVENT, type="now")

        context.past_sponsored_hackathons = self.get_sponsored_docs(
            doctype=HACKATHON,
            type="past",
        )

        context.present_sponsored_hackathons = self.get_sponsored_docs(
            doctype=HACKATHON,
            type="now",
        )

        # NOTE: Falling back to city images until organization graphics are made
        context.default_org_logo = "/assets/fossunited/images/chapter/city_profile.svg"
        context.default_org_banner = "/assets/fossunited/images/chapter/city_community_banner.png"

        context.org_about_html = sanitize_html(markdown(self.org_about))
