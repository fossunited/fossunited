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

        from fossunited.foss_profiles.doctype.organization_team_member.organization_team_member import (  # noqa: E501
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
        org_about: DF.TextEditor
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
    pass

    def get_social_links(self):
        socials = {}
        # Get social fields from type annotations to stay in sync
        social_fields = [
            "github",
            "gitlab",
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
                # Handle special naming cases
                display_name = "matrix-light" if field == "matrix" else field
                socials[display_name] = value

        return socials

    def get_members(self):
        members = []
        for member in self.org_members:
            profile = frappe.get_doc(USER_PROFILE, member.org_member).as_dict()
            members.append(
                {
                    "full_name": profile.full_name,
                    "role": member.org_role,
                    "profile_picture": (
                        profile.profile_photo
                        if profile.profile_photo
                        else "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.route,
                }
            )
        return members

    def get_context(self, context):
        context.members = self.get_members()
        context.social_links = self.get_social_links()
