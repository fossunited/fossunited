# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSChapter(WebsiteGenerator):
    def before_save(self):
        for member in self.chapter_members:
            if member.role == "Lead":
                self.chapter_lead = member.chapter_member
                break

    def get_context(self, context):
        if self.chapter_type == "City Community":
            context.profile_img_src = (
                "/assets/fossunited/images/chapter/city_profile.svg"
            )
            context.default_banner = "/assets/fossunited/images/chapter/city_community_banner.png"
        else:
            context.profile_img_src = "/assets/fossunited/images/chapter/foss_club_profile.svg"
            context.default_banner = "/assets/fossunited/images/chapter/foss_club_banner.png"

        context.upcoming_events = self.get_upcoming_events()
        context.past_events = self.get_past_events()
        context.members = self.get_members()
        context.social_links = self.get_social_links()

    def get_upcoming_events(self):
        return frappe.get_all(
            "FOSS Chapter Events",
            filters={
                "chapter": self.name,
                "event_end_date": (">=", frappe.utils.now()),
                "status": ["in", ["Approved", "In Progress"]],
            },
            fields=[
                "name",
                "route",
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
            "FOSS Chapter Events",
            filters={
                "chapter": self.name,
                "event_end_date": ("<", frappe.utils.now()),
                "status": "Concluded",
            },
            fields=[
                "name",
                "route",
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
