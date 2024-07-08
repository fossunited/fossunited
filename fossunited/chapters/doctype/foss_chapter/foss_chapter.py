# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSChapter(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.chapters.doctype.foss_chapter_lead_team_member.foss_chapter_lead_team_member import (
            FOSSChapterLeadTeamMember,
        )

        about_chapter: DF.TextEditor | None
        banner_image: DF.AttachImage | None
        chapter_lead: DF.Link | None
        chapter_members: DF.Table[FOSSChapterLeadTeamMember]
        chapter_name: DF.Data
        chapter_type: DF.Literal[
            "City Community", "FOSS Club", "Conference"
        ]
        city: DF.Link | None
        country: DF.Link | None
        email: DF.Data
        facebook: DF.Data | None
        google_map_link: DF.Data | None
        instagram: DF.Data | None
        institution_name: DF.Link | None
        is_published: DF.Check
        linkedin: DF.Data | None
        mastodon: DF.Data | None
        public_chat_group_url: DF.Data | None
        represent_image: DF.AttachImage | None
        route: DF.Data | None
        state: DF.Link | None
        x: DF.Data | None

    # end: auto-generated types
    def validate(self):
        self.make_city_name_upper()

    def before_save(self):
        self.set_chapter_lead()
        self.set_route()

    def set_chapter_lead(self):
        for member in self.chapter_members:
            if member.role == "Lead":
                self.chapter_lead = member.chapter_member
                break

    def set_route(self):
        if self.chapter_type == "FOSS Club":
            self.route = (
                f"clubs/{self.chapter_name.lower().replace(' ', '-')}"
            )
        else:
            self.route = (
                f"{self.chapter_name.lower().replace(' ', '-')}"
            )

    def get_context(self, context):
        if self.chapter_type == "City Community":
            context.profile_img_src = (
                "/assets/fossunited/images/chapter/city_profile.svg"
            )
            context.default_banner = "/assets/fossunited/images/chapter/city_community_banner.png"
        elif self.chapter_type == "FOSS Club":
            context.profile_img_src = "/assets/fossunited/images/chapter/foss_club_profile.svg"
            context.default_banner = "/assets/fossunited/images/chapter/foss_club_banner.png"
        else:
            context.profile_img_src = None

        context.upcoming_events = self.get_upcoming_events()
        context.past_events = self.get_past_events()
        context.members = self.get_members()
        context.social_links = self.get_social_links()

    # make the chapter name upper case if it is a city community
    def make_city_name_upper(self):
        if self.chapter_type == "City Community":
            self.chapter_name = self.city.upper()

    def get_upcoming_events(self):
        return frappe.get_all(
            "FOSS Chapter Event",
            filters={
                "chapter": self.name,
                "event_end_date": (">=", frappe.utils.now()),
                "status": ["in", ["Approved", "Live"]],
            },
            fields=[
                "name",
                "route",
                "chapter",
                "event_start_date",
                "event_name",
                "banner_image",
                "must_attend",
                "event_location",
            ],
            order_by="event_start_date asc",
            page_length=6,
        )

    def get_past_events(self):
        return frappe.get_all(
            "FOSS Chapter Event",
            filters={
                "chapter": self.name,
                "event_end_date": ("<", frappe.utils.now()),
                "status": "Concluded",
            },
            fields=[
                "name",
                "route",
                "chapter",
                "event_start_date",
                "event_name",
                "banner_image",
                "must_attend",
                "event_location",
            ],
            order_by="event_end_date desc",
            page_length=6,
        )

    def get_members(self):
        members = []
        for member in self.chapter_members:
            profile = frappe.get_doc(
                "FOSS User Profile", member.chapter_member
            ).as_dict()
            members.append(
                {
                    "full_name": member.full_name,
                    "role": member.role,
                    "profile_picture": profile.profile_photo
                    if profile.profile_photo
                    else "/assets/fossunited/images/defaults/user_profile_image.png",
                    "route": profile.route,
                }
            )
        return members

    def get_social_links(self):
        socials = {}
        SOCIAL_LINK_FIELDNAMES = [
            "github",
            "gitlab",
            "x",
            "linkedin",
            "instagram",
            "mastodon",
            "youtube",
            "medium",
            "facebook",
        ]
        for k, v in self.as_dict().items():
            if k in SOCIAL_LINK_FIELDNAMES:
                if v:
                    socials[k] = v
            else:
                continue

        return socials
