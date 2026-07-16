# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import USER_PROFILE


class FOSSUnitedTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        designation: DF.Data | None
        foss_user_profile: DF.Link | None
        full_name: DF.Data
        headshot: DF.AttachImage | None
        is_active: DF.Check
        org_role: DF.Literal[
            "",
            "Founder",
            "Board",
            "Governing Board",
            "Full-Time",
            "Part-Time",
            "Intern",
            "Fellow",
            "Volunteer",
        ]
        portfolio_url: DF.Data | None
        user_bio: DF.SmallText | None
        username: DF.Data | None
    # end: auto-generated types

    def before_save(self):
        self.sync_from_user_profile()

    def sync_from_user_profile(self):
        if not self.foss_user_profile:
            return

        profile = frappe.get_cached_doc(USER_PROFILE, self.foss_user_profile)

        if not self.full_name and profile.full_name:
            self.full_name = profile.full_name
        if self.username != profile.username:
            self.username = profile.username
        if not self.headshot and profile.profile_photo:
            self.headshot = profile.profile_photo
        if not self.user_bio and profile.bio:
            self.user_bio = profile.bio
