# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.website.website_generator import WebsiteGenerator


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
        discuss: DF.Data | None
        instagram: DF.Data | None
        linkedin: DF.Data | None
        logo: DF.AttachImage | None
        mastodon: DF.Data | None
        matrix: DF.Data | None
        org_about: DF.TextEditor
        org_email: DF.Data
        org_lead: DF.Data | None
        org_members: DF.Table[OrganizationTeamMember]
        org_name: DF.Data
        org_type: DF.Data | None
        org_website: DF.Data
        published: DF.Check
        route: DF.Data | None
        telegram: DF.Data | None
        twitter: DF.Data | None
        # end: auto-generated types
    pass

    def get_social_links(self):
        socials = {}
        # Get social fields from type annotations to stay in sync
        social_fields = [
            "bluesky",
            "discord",
            "discuss",
            "instagram",
            "linkedin",
            "mastodon",
            "matrix",
            "telegram",
            "twitter",
        ]

        for field in social_fields:
            value = getattr(self, field, None)
            if value:
                # Handle special naming cases
                display_name = "matrix-light" if field == "matrix" else field
                socials[display_name] = value

        return socials
