# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSUserProfile(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_profiles.doctype.foss_user_profile_education.foss_user_profile_education import (
            FOSSUserProfileEducation,
        )
        from fossunited.foss_profiles.doctype.foss_user_profile_work_experience.foss_user_profile_work_experience import (
            FOSSUserProfileWorkExperience,
        )
        from fossunited.foss_profiles.doctype.foss_user_projects.foss_user_projects import (
            FOSSUserProjects,
        )
        from fossunited.foss_profiles.doctype.foss_user_skill_multiselect.foss_user_skill_multiselect import (
            FOSSUserSkillMultiselect,
        )

        about: DF.TextEditor | None
        bio: DF.SmallText | None
        cover_image: DF.AttachImage | None
        current_city: DF.Link | None
        devto: DF.Data | None
        education: DF.Table[FOSSUserProfileEducation]
        email: DF.Data | None
        experience: DF.Table[FOSSUserProfileWorkExperience]
        full_name: DF.Data | None
        gender: DF.Data | None
        github: DF.Data | None
        gitlab: DF.Data | None
        instagram: DF.Data | None
        is_private: DF.Check
        is_published: DF.Check
        linkedin: DF.Data | None
        mastodon: DF.Data | None
        medium: DF.Data | None
        profile_photo: DF.AttachImage | None
        projects: DF.Table[FOSSUserProjects]
        route: DF.Data | None
        skills: DF.TableMultiSelect[FOSSUserSkillMultiselect]
        user: DF.Link
        username: DF.Data
        website: DF.Data | None
        x: DF.Data | None
        youtube: DF.Data | None

    # end: auto-generated types
    def validate(self):
        self.validate_username()
        self.set_route()

    def validate_username(self):
        self.username = self.username.lower().replace("-", "_")

    def set_route(self):
        self.route = self.username.lower().replace("-", "_")

    def get_context(self, context):
        if self.is_private and frappe.session.user not in (
            "Administrator",
            self.user,
        ):
            frappe.throw(
                _("Profile Not Found"), frappe.DoesNotExistError
            )

        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(
                experience.as_dict()
            )
        context.experiences_dict = experiences_dict
        context.no_cache = 1

    def on_trash(self):
        frappe.delete_doc("User", self.user, force=True)
