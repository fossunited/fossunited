# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import re
import textwrap
from datetime import datetime

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.emailing import create_email_group
from fossunited.doctype_ids import (
    CAMPAIGN,
    CHAPTER,
    EMAIL_GROUP,
    EVENT,
    EVENT_CFP,
    EVENT_RSVP,
    EVENT_TICKET,
    PROPOSAL,
    RSVP_RESPONSE,
    SPEAKER,
    USER_PROFILE,
)
from fossunited.fossunited.utils import is_user_team_member

BASE_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


class FOSSChapterEvent(WebsiteGenerator):
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
        from fossunited.fossunited.doctype.event_project_showcase.event_project_showcase import (
            EventProjectShowcase,
        )
        from fossunited.fossunited.doctype.foss_event_field.foss_event_field import (
            FOSSEventField,
        )
        from fossunited.fossunited.doctype.foss_event_schedule.foss_event_schedule import (
            FOSSEventSchedule,
        )
        from fossunited.fossunited.doctype.foss_event_sponsor.foss_event_sponsor import (
            FOSSEventSponsor,
        )
        from fossunited.ticketing.doctype.foss_ticket_tier.foss_ticket_tier import (
            FOSSTicketTier,
        )

        banner_image: DF.AttachImage | None
        chapter: DF.Link | None
        chapter_name: DF.Data | None
        community_partners: DF.Table[FOSSEventCommunityPartner]
        custom_fields: DF.Table[FOSSEventField]
        deck_link: DF.Data | None
        event_bio: DF.Data | None
        event_description: DF.TextEditor | None
        event_end_date: DF.Datetime
        event_location: DF.Data | None
        event_logo: DF.AttachImage | None
        event_members: DF.Table[FOSSChapterEventMember]
        event_name: DF.Data
        event_permalink: DF.Data | None
        event_schedule: DF.Table[FOSSEventSchedule]
        event_start_date: DF.Datetime
        event_type: DF.Literal[
            "Meet Up",  # noqa: F722, F821
            "Conference",  # noqa: F722, F821
            "Workshop",  # noqa: F722, F821
            "Birds Of Feathers",  # noqa: F722, F821
            "Hackathon",  # noqa: F722, F821
            "Linux Installation Party",  # noqa: F722, F821
        ]
        external_event_url: DF.Data | None
        hall_options: DF.SmallText | None
        has_external_webpage: DF.Check
        is_external_event: DF.Check
        is_paid_event: DF.Check
        is_published: DF.Check
        livestream_embed_link: DF.Data | None
        livestream_link: DF.Data | None
        map_link: DF.Data | None
        must_attend: DF.Check
        paid_tshirts_available: DF.Check
        primary_button_label: DF.Data | None
        primary_button_url: DF.Data | None
        project_showcase: DF.Table[EventProjectShowcase]
        proposal_page_description: DF.Text | None
        route: DF.Data | None
        schedule_page_description: DF.LongText | None
        secondary_button_label: DF.Data | None
        secondary_button_url: DF.Data | None
        show_cfp: DF.Check
        show_photos: DF.Check
        show_rsvp: DF.Check
        show_schedule: DF.Check
        show_speakers: DF.Check
        sponsor_list: DF.Table[FOSSEventSponsor]
        status: DF.Literal["Draft", "Live", "Concluded", "Cancelled"]  # noqa: F722, F821
        t_shirt_price: DF.Currency
        ticket_form_description: DF.MarkdownEditor | None
        tickets_status: DF.Literal["Live", "Closed"]  # noqa: F722, F821
        tiers: DF.Table[FOSSTicketTier]
    # end: auto-generated types

    def after_insert(self):
        if not self.is_external_event:
            self.create_email_groups()

    def before_insert(self):
        self.copy_team_members()

    def validate(self):
        self.validate_permalink()

    def before_save(self):
        if self.is_external_event:
            self.has_external_webpage = True

        if self.has_value_changed("status"):
            self.update_published_status()
        self.set_route()

    def on_trash(self):
        self.delete_campaigns()
        self.delete_email_groups()

    def create_email_groups(self):
        for group in [
            "Event Participants",
            "CFP Proposers",
            "Accepted Proposers",
            "Rejected Proposers",
        ]:
            create_email_group(type=group, reference_document=self.name, document_type=EVENT)

    def delete_campaigns(self):
        campaigns = frappe.db.get_all(
            CAMPAIGN,
            {"reference_document": self.name, "document_type": EVENT},
            pluck="name",
        )
        for campaign in campaigns:
            frappe.delete_doc(
                CAMPAIGN,
                campaign,
            )

    def delete_email_groups(self):
        groups = frappe.db.get_all(
            EMAIL_GROUP,
            {"reference_document": self.name, "document_type": EVENT},
            pluck="name",
        )
        for group in groups:
            frappe.delete_doc(
                EMAIL_GROUP,
                group,
            )

    def copy_team_members(self):
        if not self.chapter:
            return

        chapter_team_members = frappe.get_doc(CHAPTER, self.chapter).chapter_members

        for member in chapter_team_members:
            self.append(
                "event_members",
                {
                    "member": member.chapter_member,
                    "full_name": member.full_name,
                    "role": member.role,
                    "email": member.email,
                },
            )

    def validate_permalink(self):
        if self.has_external_webpage:
            return

        if frappe.db.exists(
            self.doctype,
            {
                "event_permalink": self.event_permalink,
                "name": ("!=", self.name),
                "chapter": self.chapter,
            },
        ):
            frappe.throw(
                f"Event Permalink {self.event_permalink} already exists!",
                frappe.ValidationError,
            )

        if " " in self.event_permalink:
            frappe.throw("Event Permalink cannot have spaces!", frappe.ValidationError)

    def update_published_status(self):
        if self.status == "Draft" or self.status == "Cancelled":
            self.is_published = 0
            return

        self.is_published = 1
        return

    def set_route(self):
        if self.has_external_webpage:
            return

        event_route = frappe.db.get_value(CHAPTER, self.chapter, "route")
        self.route = f"{event_route}/{self.event_permalink}"

    def get_meta(self):
        pagetitle = self.event_name

        desc_short = textwrap.shorten(re.sub(r"<.*?>", "", self.event_description), width=150)

        description = "{self.event_name} is being organized on {start_date} by {self.chapter_name} Community. {desc_short}".format(  # noqa: E501
            self=self,
            desc_short=desc_short,
            start_date=self.event_start_date.strftime("%A, %-d %B %Y"),
        )

        og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        image = "{og_url}/gen/events?event_name={self.event_name}&event_date={start_date}&event_type={self.event_type}&event_chapter={self.chapter_name}&event_location={self.event_location}".format(  # noqa: E501
            self=self,
            og_url=og_url,
            start_date=self.event_start_date.strftime("%-d %B %Y"),
        )

        return pagetitle, description, image

    def get_navbar_items(self, speakers=None):
        navbar_items = [
            "event_information",
            "speakers",
            "rsvp",
            "talk_proposal",
            "livestreaming",
        ]

        if is_user_team_member(self.chapter, frappe.session.user):
            return navbar_items

        if speakers is None:
            speakers, _ = self.get_speakers()
        if not self.show_speakers or not speakers:
            navbar_items.remove("speakers")
        if not self.show_rsvp or self.is_paid_event:
            navbar_items.remove("rsvp")
        if not self.show_cfp:
            navbar_items.remove("talk_proposal")
        if self.livestream_embed_link is None:
            navbar_items.remove("livestreaming")

        return navbar_items

    def get_sponsors(self):
        # Get industry partners with joining_date (normalize company names, normalize dates)
        ip_records = frappe.db.get_all("Industry Partners", fields=["company", "joining_date"])
        ip_lookup = {
            (ip.get("company") or "").strip().lower(): frappe.utils.getdate(ip.get("joining_date"))
            if ip.get("joining_date")
            else None
            for ip in ip_records
        }
        # Define tier sort order (include Venue Partner per spec)
        sort_order = {
            "Platinum": 0,
            "Gold": 1,
            "Silver": 2,
            "Bronze": 3,
            "Venue Partner": 4,
        }

        # Group sponsors by tier (do not mutate persisted fields like `tier`)
        sponsors_by_tier = {}
        for s in self.sponsor_list:
            tier_key = (s.custom_tier or "Custom").strip() if s.tier == "Custom" else s.tier
            sponsor_key = (s.sponsor_name or "").strip().lower()
            s.is_ip = sponsor_key in ip_lookup
            s.sort_date = (
                ip_lookup.get(sponsor_key)
                if s.is_ip
                else (frappe.utils.getdate(s.date_of_confirm) if s.date_of_confirm else None)
            )
            sponsors_by_tier.setdefault(tier_key, []).append(s)

        # Sort sponsors within each tier
        fallback_date = frappe.utils.getdate(frappe.utils.today())
        for sponsor_group in sponsors_by_tier.values():
            sponsor_group.sort(
                key=lambda s: (
                    not s.is_ip,
                    s.sort_date is None,
                    s.sort_date or fallback_date,
                    (s.sponsor_name or "").lower(),
                )
            )

        # Return sponsors_by_tier dict in sorted tier order
        return dict(
            sorted(
                sponsors_by_tier.items(),
                key=lambda x: sort_order.get(x[0], float("inf")),
            )
        )

    def get_volunteers(self):
        """Get volunteers with profile information. Batch fetch profiles for performance."""
        if not self.event_members:
            return []

        # Batch fetch all profiles
        member_ids = [member.member for member in self.event_members]
        profiles = {
            p.name: p
            for p in frappe.get_all(
                USER_PROFILE,
                filters={"name": ("in", member_ids)},
                fields=["name", "profile_photo", "route"],
            )
        }

        members = []
        for member in self.event_members:
            profile = profiles.get(member.member, {})
            members.append(
                {
                    "full_name": member.full_name,
                    "role": member.role or "Volunteer",
                    "profile_picture": (
                        profile.get("profile_photo")
                        if profile.get("profile_photo")
                        else "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.get("route", ""),
                }
            )
        return members

    def get_speakers(self):
        submissions = frappe.db.get_all(
            PROPOSAL,
            {"event": self.name, "status": "Approved"},
            ["name", "talk_title", "route"],
        )

        speakers = []

        for submission in submissions:
            _submission_speakers = frappe.db.get_all(
                SPEAKER,
                {"parent": submission.name},
                [
                    "photo",
                    "full_name",
                    "designation",
                    "organization",
                    "linked_user",
                    "parent",
                ],
            )
            speakers.extend(_submission_speakers)

        return speakers, submissions

    def get_rsvp_status_block(self):
        rsvp_status_block = {}
        rsvp_status_block["doctype"] = EVENT_RSVP
        rsvp_status_block["block_for"] = "rsvp"

        if frappe.db.exists(EVENT_RSVP, {"event": self.name}):
            rsvp_form = frappe.get_doc(EVENT_RSVP, {"event": self.name})
            rsvp_status_block |= {
                "form_route": rsvp_form.route,
                "has_doc": True,
                "block_heading": "RSVP Form is Live!",
                "docname": rsvp_form.name,
                "is_published": rsvp_form.is_published,
                "is_unpublished": not rsvp_form.is_published,
            }
            rsvp_status_block["is_team_member"] = False
            if frappe.db.exists(
                RSVP_RESPONSE,
                {
                    "linked_rsvp": rsvp_form.name,
                    "submitted_by": frappe.session.user,
                },
            ):
                submission = frappe.get_doc(
                    RSVP_RESPONSE,
                    {
                        "linked_rsvp": rsvp_form.name,
                        "submitted_by": frappe.session.user,
                    },
                )
                rsvp_status_block |= {
                    "has_submitted": True,
                    "block_heading": "You have RSVP'd",
                    "submission": submission.name,
                    "edit_submission": True,
                }
            else:
                rsvp_status_block["show_primary_cta"] = True
                rsvp_status_block["primary_cta"] = "RSVP for the event"

            if not rsvp_form.is_published:
                rsvp_status_block["block_heading"] = "RSVP form is closed!"
        else:
            rsvp_status_block["has_doc"] = False
            rsvp_status_block["block_heading"] = "RSVP form is not live yet!"
            rsvp_status_block["is_team_member"] = False
            rsvp_status_block["show_primary_cta"] = False
        return rsvp_status_block

    def get_cfp_status_block(self):
        cfp_status_block = {}
        cfp_status_block["doctype"] = EVENT_CFP
        cfp_status_block["block_for"] = "cfp"

        if frappe.db.exists(EVENT_CFP, {"event": self.name}):
            cfp_form = frappe.get_doc(EVENT_CFP, {"event": self.name})
            cfp_status_block |= {
                "form_route": cfp_form.get("route") or f"{self.route}/cfp",
                "has_doc": True,
                "block_heading": "Call for Proposal (CFP) Form is Live!",
                "docname": cfp_form.name,
                "deadline": (
                    cfp_form.deadline.strftime("%d %B, %Y  %I:%M %p")
                    if cfp_form.deadline
                    else None
                ),
                "is_published": cfp_form.status == "Live",
                "is_unpublished": cfp_form.status == "Closed",
            }
            cfp_status_block["is_team_member"] = False
            if frappe.db.exists(
                PROPOSAL,
                {
                    "linked_cfp": cfp_form.name,
                    "submitted_by": frappe.session.user,
                },
            ):
                submission = frappe.get_doc(
                    PROPOSAL,
                    {
                        "linked_cfp": cfp_form.name,
                        "submitted_by": frappe.session.user,
                    },
                )
                cfp_status_block |= {
                    "has_submitted": True,
                    "block_heading": "You have submitted a talk",
                    "submission": submission.name,
                }

            cfp_status_block["show_primary_cta"] = True
            cfp_status_block["primary_cta"] = "Submit a talk proposal"

            if cfp_form.status == "Closed":
                cfp_status_block["block_heading"] = "Talk Proposal Form is Unpublished!"
        else:
            cfp_status_block["has_doc"] = False
            cfp_status_block["block_heading"] = "Talk Proposal Form is not live yet!"
            cfp_status_block["is_team_member"] = False
            cfp_status_block["show_primary_cta"] = False
        return cfp_status_block

    def check_user_registration(self):
        """Check if the current user has registered for this event via RSVP or ticket purchase"""
        if frappe.session.user == "Guest":
            return False

        # Check for RSVP
        rsvp_exists = frappe.db.exists(
            RSVP_RESPONSE,
            {
                "event": self.name,
                "submitted_by": frappe.session.user,
            },
        )

        if rsvp_exists:
            return True

        # Check for ticket purchase (if ticketing is enabled)
        if self.is_paid_event:
            ticket_exists = frappe.db.exists(
                EVENT_TICKET,
                {
                    "event": self.name,
                    "email": frappe.session.user,
                },
            )
            if ticket_exists:
                return True

        return False

    def get_event_stats(self):
        """Get attendance and proposal statistics for the event"""
        stats = {"attending": 0, "proposals": 0}

        # Count RSVP responses
        rsvp_count = frappe.db.count(RSVP_RESPONSE, {"event": self.name})
        stats["attending"] = rsvp_count

        # Add ticket holders if paid event
        if self.is_paid_event:
            ticket_count = frappe.db.count(
                EVENT_TICKET,
                {"event": self.name},
            )
            stats["attending"] += ticket_count

        # Count proposals
        proposal_count = frappe.db.count(PROPOSAL, {"event": self.name})
        stats["proposals"] = proposal_count

        return stats

    def format_schedule_for_template(self, schedule_dict):
        """Format schedule dict with time display for template rendering.
        Returns nested structure: {date: {hall: [items]}} with start_time_display added.
        """
        if not schedule_dict:
            return {}

        def fmt(td):
            if not td:
                return ""
            s = int(td.total_seconds())
            h, m = (s // 3600) % 24, (s % 3600) // 60
            return f"{(h % 12) or 12:02d}:{m:02d} {'AM' if h < 12 else 'PM'}"

        formatted = {}
        for date_str, halls in schedule_dict.items():
            formatted[date_str] = {}
            for hall, items in halls.items():
                formatted[date_str][hall] = [
                    (
                        setattr(
                            item,
                            "start_time_display",
                            fmt(getattr(item, "start_time", None)),
                        )
                        or item
                    )
                    for item in items
                ]
        return formatted

    def get_context(self, context):
        context.chapter = frappe.get_doc(CHAPTER, self.chapter)
        context.sponsors_dict = self.get_sponsors()
        context.volunteers = self.get_volunteers()
        context.speakers, context.submissions = self.get_speakers()
        context.rsvp_status_block = self.get_rsvp_status_block()
        context.cfp_status_block = self.get_cfp_status_block()
        context.all_cfp_link = f"/dashboard/cfp/all/{self.route.split('c/')[1]}"

        # Add user registration status
        context.user_has_registered = self.check_user_registration()

        # Add event statistics
        context.event_stats = self.get_event_stats()

        # Add schedule data using existing API - keep nested structure for proper ordering
        from fossunited.api.schedule import get_event_schedule

        schedule_dict = get_event_schedule(self.name)
        context.schedule_data = self.format_schedule_for_template(schedule_dict)

        # Format CFP deadline for short display (already formatted in get_cfp_status_block)
        if context.cfp_status_block.get("has_doc") and context.cfp_status_block.get("deadline"):
            # Convert from long format to short format for display
            try:
                from datetime import datetime

                deadline_dt = datetime.strptime(
                    context.cfp_status_block["deadline"], "%d %B, %Y  %I:%M %p"
                )
                context.cfp_status_block["deadline"] = deadline_dt.strftime("%d %b %Y")
            except (ValueError, AttributeError):
                # If already in short format or invalid, keep as is
                pass

        context.pagetitle, context.description, context.image = self.get_meta()
        context.social_links = frappe.get_doc(CHAPTER, self.chapter).get_social_links()
