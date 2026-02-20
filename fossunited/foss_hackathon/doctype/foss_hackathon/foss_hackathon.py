# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
from datetime import datetime

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.emailing import create_email_group
from fossunited.api.schedule import get_event_schedule
from fossunited.chapters.doctype.foss_chapter_event.foss_chapter_event import (
    FOSSChapterEvent,
)
from fossunited.doctype_ids import (
    CHAPTER,
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    HACKATHON_PARTNER_PROJECT,
    USER_PROFILE,
)
from fossunited.fossunited.utils import get_event_sponsors

BASE_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


class FOSSHackathon(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.chapters.doctype.foss_chapter_event_member.foss_chapter_event_member import (  # noqa: E501
            FOSSChapterEventMember,
        )
        from fossunited.chapters.doctype.foss_event_community_partner.foss_event_community_partner import (  # noqa: E501
            FOSSEventCommunityPartner,
        )
        from fossunited.fossunited.doctype.foss_event_schedule.foss_event_schedule import (
            FOSSEventSchedule,
        )
        from fossunited.fossunited.doctype.foss_event_sponsor.foss_event_sponsor import (
            FOSSEventSponsor,
        )

        chapter: DF.Link
        community_partners: DF.Table[FOSSEventCommunityPartner]
        contribution_coming_soon_description: DF.SmallText | None
        contribution_project_guidelines: DF.MarkdownEditor | None
        enable_oss_contributon_projects: DF.Check
        end_date: DF.Datetime
        external_website_url: DF.Data | None
        hackathon_banner: DF.AttachImage | None
        hackathon_description: DF.TextEditor
        hackathon_logo: DF.AttachImage | None
        hackathon_name: DF.Data
        hackathon_rules: DF.TextEditor | None
        hackathon_type: DF.Literal["", "Remote", "In-person", "Hybrid"]
        has_external_website: DF.Check
        has_localhosts: DF.Check
        has_partner_projects: DF.Check
        is_contribution_project_coming_soon: DF.Check
        is_published: DF.Check
        is_registration_live: DF.Check
        is_team_mandatory: DF.Check
        max_team_members: DF.Int
        only_show_logo: DF.Check
        partner_project_guidelines: DF.MarkdownEditor | None
        permalink: DF.Data | None
        registration_description: DF.TextEditor | None
        route: DF.Data | None
        schedule: DF.Table[FOSSEventSchedule]
        show_schedule_tab: DF.Check
        sponsor_list: DF.Table[FOSSEventSponsor]
        start_date: DF.Datetime
        volunteers: DF.Table[FOSSChapterEventMember]
    # end: auto-generated types

    def before_save(self):
        self.set_route()

    def after_insert(self):
        create_email_group(
            type="Event Participants",
            reference_document=self.name,
            document_type=HACKATHON,
        )

    def set_route(self):
        if self.permalink:
            self.route = f"hack/{self.permalink}"
        else:
            self.route = f"hack/{self.hackathon_name.lower().replace(' ', '-')}"

    def get_context(self, context):
        if self.chapter:
            context.chapter = frappe.get_doc(CHAPTER, self.chapter)

        context.sponsors_dict = get_event_sponsors(self.sponsor_list)

        schedule_dict = get_event_schedule(self.name, self.doctype)
        context.schedule_data = FOSSChapterEvent.format_schedule_for_template(schedule_dict)

        context.event_stats = frappe.db.count(HACKATHON_PARTICIPANT, {"hackathon": self.name})

        cities_dict = self.get_localhosts()
        context.localhosts_by_city = [
            {"city": city, "localhosts": hosts} for city, hosts in sorted(cities_dict.items())
        ]

        context.volunteers = self.get_volunteers()
        context.mentors = self.get_mentors()
        context.partner_projects = frappe.get_all(
            HACKATHON_PARTNER_PROJECT,
            {"hackathon": self.name},
            ["repo_link as link", "project_name as sponsor_name", "logo as image"],
        )
        context.status_live = self.end_date > frappe.utils.now_datetime()
        context.registration_status = frappe.db.exists(
            HACKATHON_PARTICIPANT, {"user": frappe.session.user, "hackathon": self.name}
        )
        context.event_year = str(self.start_date.year)
        context.pagetitle, context.description, context.image = self.get_meta()
        context.no_cache = 1

    def get_volunteers(self):
        members = []
        for member in self.volunteers:
            profile = frappe.db.get_value(
                USER_PROFILE,
                member.member,
                [
                    "profile_photo",
                    "route",
                ],
                as_dict=1,
            )
            members.append(
                {
                    "full_name": member.full_name,
                    "role": member.role or "Volunteer",
                    "profile_picture": (
                        profile.profile_photo
                        or "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.route,
                }
            )
        return members

    def get_meta(self):
        import re
        import textwrap

        pagetitle = self.hackathon_name

        desc_short = textwrap.shorten(re.sub(r"<.*?>", "", self.hackathon_description), width=150)

        start_date = self.start_date.strftime("%A, %-d %B %Y")
        end_date = self.end_date.strftime("%-d %B %Y")

        chapter_name = frappe.db.get_value(CHAPTER, self.chapter, "chapter_name")

        hackathon_type_text = ""
        if self.hackathon_type:
            hackathon_type_text = f"This is a {self.hackathon_type.lower()} hackathon. "

        description = "{hackathon_name} is a hackathon organized by {chapter_name} Community from {start_date} to {end_date}. {type_text}{desc_short}".format(  # noqa: E501
            hackathon_name=self.hackathon_name,
            chapter_name=chapter_name,
            start_date=start_date,
            end_date=end_date,
            type_text=hackathon_type_text,
            desc_short=desc_short,
        )

        og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        image = "{og_url}/gen/hackathons?hackathon_name={hackathon_name}&start_date={start_date}&end_date={end_date}&hackathon_type={hackathon_type}&chapter={chapter_name}".format(  # noqa: E501
            og_url=og_url,
            hackathon_name=self.hackathon_name,
            start_date=self.start_date.strftime("%-d %B %Y"),
            end_date=self.end_date.strftime("%-d %B %Y"),
            hackathon_type=self.hackathon_type or "",
            chapter_name=chapter_name,
        )

        return pagetitle, description, image

    def get_localhosts(self):
        localhosts = frappe.db.get_all(
            HACKATHON_LOCALHOST,
            filters={"parent_hackathon": self.name},
            fields=["name", "localhost_name", "route", "city", "state", "location"],
            order_by="city, localhost_name",
            page_length=99,
        )

        # Bulk Fetch Counts
        attending_counts = frappe.db.get_all(
            HACKATHON_PARTICIPANT,
            filters={"localhost_request_status": "Accepted", "hackathon": self.name},
            fields=["localhost", "count(name) as count"],
            group_by="localhost",
        )
        applied_counts = frappe.db.get_all(
            HACKATHON_PARTICIPANT,
            filters={"hackathon": self.name},
            fields=["localhost", "count(name) as count"],
            group_by="localhost",
        )
        localhost_names = [h["name"] for h in localhosts]
        likes_counts = frappe.db.get_all(
            "Comment",
            filters={
                "comment_type": "Like",
                "reference_doctype": HACKATHON_LOCALHOST,
                "reference_name": ("in", localhost_names),
            },
            fields=["reference_name as localhost", "count(name) as count"],
            group_by="reference_name",
        )

        # Convert to dicts
        attending_dict = {item["localhost"]: item["count"] for item in attending_counts}
        applied_dict = {item["localhost"]: item["count"] for item in applied_counts}
        likes_dict = {item["localhost"]: item["count"] for item in likes_counts}

        # Process LocalHosts and group by city
        cities_dict = {}
        for host in localhosts:
            host["route"] = f"/{host.route}"
            host["attending"] = attending_dict.get(host.name, 0)
            host["interested"] = applied_dict.get(host.name, 0) + likes_dict.get(host.name, 0)

            city = host.get("city", "Other")
            if city not in cities_dict:
                cities_dict[city] = []

            cities_dict[city].append(host)

        return cities_dict

    def get_mentors(self):
        mentors = frappe.get_all(
            "FOSS Hackathon Mentor",
            filters={"hackathon": self.name},
            fields=[
                "name",
                "mentor",
                "full_name",
                "mentor.user_image as profile_picture",
                "mentor.username as username",
            ],
        )

        for m in mentors:
            if m.get("username"):
                m["route"] = f"u/{m['username']}"

        return mentors
