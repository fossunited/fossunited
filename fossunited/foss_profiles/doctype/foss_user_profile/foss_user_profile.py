# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.exceptions import PermissionError
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.profile import is_valid_username
from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_TICKET,
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    PROPOSAL,
    RSVP_RESPONSE,
)


class PrivateProfileError(PermissionError):
    """Exception raised when trying to access a private profile."""

    pass


class FOSSUserProfile(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_profiles.doctype.foss_user_profile_education.foss_user_profile_education import (  # noqa: E501
            FOSSUserProfileEducation,
        )
        from fossunited.foss_profiles.doctype.foss_user_profile_work_experience.foss_user_profile_work_experience import (  # noqa: E501
            FOSSUserProfileWorkExperience,
        )
        from fossunited.foss_profiles.doctype.foss_user_projects.foss_user_projects import (  # noqa: E501
            FOSSUserProjects,
        )
        from fossunited.foss_profiles.doctype.foss_user_skill_multiselect.foss_user_skill_multiselect import (  # noqa: E501
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
        show_activity: DF.Check
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

    def after_insert(self):
        self.share_user_with_self()

    def on_update(self):
        prev_user_doc = self.get_doc_before_save()
        if prev_user_doc is None:
            return
        try:
            if self.full_name is not self.get_doc_before_save().full_name:
                frappe.db.set_value(
                    "User",
                    {"email": self.email},
                    "full_name",
                    self.full_name,
                )
            if self.username is not self.get_doc_before_save().username:
                frappe.db.set_value(
                    "User",
                    {"email": self.email},
                    "username",
                    self.username,
                )
        except Exception as e:
            frappe.log_error(f"Error updating user details: {str(e)}")
            frappe.throw("Error updating user details")

    def validate_username(self):
        if not (3 <= len(self.username) <= 30):
            frappe.throw("Username must be between 3 and 30 characters")

        if not re.match(r"^[a-z0-9_\.]+$", self.username):
            frappe.throw(
                "Username can only contain lowercase letters, numbers, underscores and dots."
            )

        if re.search(
            r"\.(txt|html|php|js|json|xml|css|htm)$",
            self.username,
            re.IGNORECASE,
        ):
            frappe.throw("Username cannot end with extensions like .txt, .html, etc.")

        if not is_valid_username(self.username, self.name):
            frappe.throw("Username is already taken or restricted.")

    def set_route(self):
        self.route = f"u/{self.username}"

    def get_user_activity(self):
        attended = []

        paid_event_ids = frappe.db.get_all(
            EVENT_TICKET,
            pluck="event",
            filters={"email": self.email},
            page_length=9999,
        )

        rsvpd_event_ids = frappe.db.get_all(
            RSVP_RESPONSE,
            pluck="event",
            filters={"email": self.email},
            page_length=9999,
        )
        for val in rsvpd_event_ids + paid_event_ids:
            attended.append(
                frappe.db.get_value(
                    EVENT,
                    fieldname=[
                        "name",
                        "route",
                        "chapter",
                        "event_start_date",
                        "event_name",
                        "banner_image",
                        "must_attend",
                        "event_location",
                    ],
                    filters={"name": val},
                    as_dict=1,
                )
            )

        attended_hack = []

        hackathon_ids = frappe.db.get_all(
            HACKATHON_PARTICIPANT,
            fields=["hackathon", "localhost"],
            filters={"email": self.email},
            page_length=9999,
        )
        for val in hackathon_ids:
            attended_hack.append(
                frappe.db.get_value(
                    HACKATHON,
                    fieldname=[
                        "name",
                        "route",
                        "chapter",
                        "start_date",
                        "hackathon_type",
                        "hackathon_logo",
                        "only_show_logo",
                        "hackathon_name",
                    ],
                    filters={"name": val.hackathon},
                    as_dict=1,
                )
                | frappe.db.get_value(
                    HACKATHON_LOCALHOST,
                    fieldname=[
                        "localhost_name",
                        "location",
                    ],
                    filters={"name": val.localhost},
                    as_dict=1,
                )
            )
        talked = []

        approved_cfp_event_ids = frappe.db.get_all(
            PROPOSAL,
            fields=["event", "talk_title", "route", "session_type"],
            filters={"email": self.email, "status": "Approved"},
            page_length=9999,
        )

        for val in approved_cfp_event_ids:
            talked.append(
                frappe.db.get_value(
                    EVENT,
                    fieldname=[
                        "name",
                        "chapter",
                        "event_start_date",
                        "event_name",
                        "banner_image",
                        "must_attend",
                        "event_location",
                    ],
                    filters={"name": val.event},
                    as_dict=1,
                )
                | val
            )

        volunteered = []

        volunteer_chapters = frappe.db.get_all(
            CHAPTER_MEMBER,
            fields=["parent", "role"],
            filters={"chapter_member": self.name},
            page_length=9999,
        )

        for val in volunteer_chapters:
            volunteered.append(
                frappe.db.get_value(
                    CHAPTER,
                    fieldname=[
                        "name",
                        "route",
                        "chapter_type",
                        "chapter_name",
                        "chapter_status",
                    ],
                    filters={"name": val.parent},
                    as_dict=1,
                )
                | val
            )

        return attended, attended_hack, talked, volunteered

    def get_context(self, context):
        if self.is_private and frappe.session.user not in (
            "Administrator",
            self.user,
        ):
            frappe.throw("Profile is Private", PrivateProfileError)

        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(experience.as_dict())
        context.experiences_dict = experiences_dict

        context.attended, context.attended_hack, context.talked, context.volunteered = (
            self.get_user_activity()
        )

        context.no_cache = 1

    def on_trash(self):
        frappe.delete_doc("User", self.user, force=True)

    def share_user_with_self(self):
        """
        Share the profile document with it's user.
        Give user Read and Write permissions.
        """
        share_doc = frappe.get_doc(
            {
                "doctype": "DocShare",
                "user": self.user,
                "share_doctype": self.doctype,
                "share_name": self.name,
                "read": 1,
                "write": 1,
                "share": 1,
            }
        )
        share_doc.flags.ignore_share_permission = 1
        share_doc.insert(ignore_permissions=True)
