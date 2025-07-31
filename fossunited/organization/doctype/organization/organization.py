# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import USER_PROFILE


class Organization(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.organization.doctype.organization_team_member.organization_team_member import (  # noqa: E501
            OrganizationTeamMember,
        )

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
        org_lead: DF.Data | None
        org_logo: DF.AttachImage | None
        org_members: DF.Table[OrganizationTeamMember]
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
        # TODO: Consider making social fields configurable.
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
        for member in self.org_members:
            try:
                profile = frappe.get_doc(USER_PROFILE, member.org_member).as_dict()
            except frappe.DoesNotExistError:
                # Skip members with missing profiles
                continue

            members.append(
                {
                    "full_name": profile.full_name,
                    "role": member.org_role,
                    "profile_picture": (
                        profile.profile_photo
                        or "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.route,
                }
            )
        return members

    def get_context(self, context):
        context.members = self.get_members()
        context.social_links = self.get_social_links()
        # NOTE: Falling back to city images until organization graphics are made
        context.default_org_logo = "/assets/fossunited/images/chapter/city_profile.svg"
        context.default_org_banner = "/assets/fossunited/images/chapter/city_community_banner.png"
