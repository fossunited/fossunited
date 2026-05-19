# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import re
import textwrap
from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.chapter import check_if_chapter_or_event_core_member
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
from fossunited.fossunited.utils import get_event_sponsors, get_youtube_id


class FOSSChapterEvent(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.chapters.doctype.foss_chapter_event_member.foss_chapter_event_member import (
            FOSSChapterEventMember,
        )
        from fossunited.chapters.doctype.foss_event_community_partner.foss_event_community_partner import (
            FOSSEventCommunityPartner,
        )
        from fossunited.fossunited.doctype.event_project_showcase.event_project_showcase import (
            EventProjectShowcase,
        )
        from fossunited.fossunited.doctype.foss_event_field.foss_event_field import FOSSEventField
        from fossunited.fossunited.doctype.foss_event_schedule.foss_event_schedule import (
            FOSSEventSchedule,
        )
        from fossunited.fossunited.doctype.foss_event_sponsor.foss_event_sponsor import (
            FOSSEventSponsor,
        )
        from fossunited.ticketing.doctype.foss_ticket_tier.foss_ticket_tier import FOSSTicketTier

        banner_image: DF.AttachImage | None
        chapter: DF.Link | None
        chapter_name: DF.Data | None
        community_partners: DF.Table[FOSSEventCommunityPartner]
        custom_fields: DF.Table[FOSSEventField]
        deck_link: DF.Data | None
        event_bio: DF.Data | None
        event_data: DF.JSON | None
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
            "Meet Up",
            "Conference",
            "Workshop",
            "Birds Of Feathers",
            "Hackathon",
            "Online",
            "Linux Installation Party",
        ]
        external_event_url: DF.Data | None
        feedback_sent: DF.Check
        hall_options: DF.SmallText | None
        has_external_webpage: DF.Check
        is_external_event: DF.Check
        is_paid_event: DF.Check
        is_published: DF.Check
        livestream_embed_link: DF.Data | None
        livestream_link: DF.Data | None
        map_coordinate: DF.Data | None
        map_link: DF.Data | None
        must_attend: DF.Check
        paid_tshirts_available: DF.Check
        project_showcase: DF.Table[EventProjectShowcase]
        proposal_page_description: DF.Text | None
        route: DF.Data | None
        schedule_page_description: DF.LongText | None
        show_cfp: DF.Check
        show_photos: DF.Check
        show_rsvp: DF.Check
        show_schedule: DF.Check
        show_speakers: DF.Check
        sponsor_list: DF.Table[FOSSEventSponsor]
        status: DF.Literal["Draft", "Live", "Concluded", "Cancelled"]
        t_shirt_price: DF.Currency
        ticket_form_description: DF.MarkdownEditor | None
        tickets_status: DF.Literal["Live", "Closed"]
        tiers: DF.Table[FOSSTicketTier]
    # end: auto-generated types

    def after_insert(self):
        if not self.is_external_event:
            self.create_email_groups()

    def before_insert(self):
        self.copy_team_members()

    def on_update(self):
        self.sync_event_member_shares()
        if (
            self.has_value_changed("status")
            and self.status == "Concluded"
            and not self.feedback_sent
            and self.event_end_date
        ):
            frappe.enqueue(
                "fossunited.utils.notifications.send_event_feedback_request",
                event_id=self.name,
                queue="long",
                enqueue_after_commit=True,
            )

    def validate(self):
        self.validate_permalink()

    def before_save(self):
        if self.is_external_event:
            self.has_external_webpage = True

        if self.has_value_changed("status"):
            self.update_published_status()
        self.set_route()

        if self.has_value_changed("map_link"):
            if self.map_link:
                lat, lng = extract_map_coordinates(self.map_link)
                self.map_coordinate = f"{lat},{lng}" if (lat and lng) else None
            else:
                self.map_coordinate = None

    def sync_event_member_shares(self):
        prev = self.get_doc_before_save()
        prev_emails = {m.email for m in prev.event_members if m.email} if prev else set()
        curr_emails = {m.email for m in self.event_members if m.email}

        for email in curr_emails - prev_emails:
            frappe.share.add_docshare(
                self.doctype,
                self.name,
                user=email,
                read=1,
                write=0,
                flags={"ignore_share_permission": True},
            )

        for email in prev_emails - curr_emails:
            frappe.db.delete(
                "DocShare",
                {"share_doctype": self.doctype, "share_name": self.name, "user": email},
            )

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
            frappe.throw(_("Event Permalink cannot have spaces!"), frappe.ValidationError)

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

        description = "{self.event_name} is being organized on {start_date} by {self.chapter_name} Community. {desc_short}".format(
            self=self,
            desc_short=desc_short,
            start_date=self.event_start_date.strftime("%A, %-d %B %Y"),
        )

        og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        og_image = "{og_url}/gen/events?event_name={self.event_name}&event_date={start_date}&event_type={self.event_type}&event_chapter={self.chapter_name}&event_location={self.event_location}".format(
            self=self,
            og_url=og_url,
            start_date=self.event_start_date.strftime("%-d %B %Y"),
        )
        image = frappe.utils.get_url(self.banner_image) or og_image

        return pagetitle, description, image

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
        if not submissions:
            return [], []

        speakers = frappe.db.get_all(
            SPEAKER,
            filters={"parent": ["in", [s.name for s in submissions]]},
            fields=[
                "photo",
                "full_name",
                "designation",
                "organization",
                "linked_user",
                "parent",
            ],
        )
        return speakers, submissions

    def get_rsvp_status_block(self):
        rsvp = frappe.db.get_value(
            EVENT_RSVP,
            {"event": self.name},
            ["route", "is_published"],
            as_dict=1,
        )
        if not rsvp:
            return {"has_doc": False, "is_published": False, "form_route": None}
        return {
            "has_doc": True,
            "is_published": bool(rsvp.is_published),
            "form_route": rsvp.route,
        }

    def get_cfp_status_block(self):
        cfp = frappe.db.get_value(
            EVENT_CFP,
            {"event": self.name},
            ["status", "deadline"],
            as_dict=1,
        )
        if not cfp:
            return {"has_doc": False}

        now = datetime.now()
        closing_soon = cfp.deadline is not None and now <= cfp.deadline <= now + timedelta(days=3)
        return {
            "has_doc": True,
            "form_route": f"{self.route}/cfp",
            "is_published": cfp.status == "Live",
            "closing_soon": closing_soon,
            "deadline": cfp.deadline.strftime("%d %b %Y") if cfp.deadline else None,
        }

    def get_user_registration_status(self):
        """Return the current user's registration status for this event"""

        user = frappe.session.user
        if user == "Guest":
            return None

        # Check RSVP first
        rsvp = frappe.db.get_value(
            RSVP_RESPONSE,
            {
                "event": self.name,
                "submitted_by": user,
            },
            "status",
        )

        if rsvp:
            return rsvp.lower()  # "accepted", "pending", "rejected"

        # Check ticket purchase if paid event
        if self.is_paid_event and frappe.db.exists(
            EVENT_TICKET,
            {"event": self.name, "email": user},
        ):
            return "ticket"

        return None

    def get_event_stats(self):
        """Get attendance and proposal statistics for the event"""
        stats = {"attending": 0, "proposals": 0}

        # Count RSVP responses
        rsvp_count = frappe.db.count(RSVP_RESPONSE, {"event": self.name, "status": "Accepted"})
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

    @staticmethod
    def format_schedule_for_template(schedule_dict):
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
                hall_items = []
                for item in items:
                    item.start_time_display = fmt(getattr(item, "start_time", None))
                    hall_items.append(item)
                formatted[date_str][hall] = hall_items
        return formatted

    def get_breadcrumb(self):
        crumbs = [
            {"route": "/", "label": "Home"},
            {"route": "/events/timeline", "label": "Events"},
            {"label": self.event_name},
        ]

        return crumbs

    def get_context(self, context):
        context.chapter = frappe.get_doc(CHAPTER, self.chapter)
        context.sponsors_dict = get_event_sponsors(self.sponsor_list)
        context.volunteers = self.get_volunteers()
        context.speakers, context.submissions = self.get_speakers()
        context.rsvp_status_block = self.get_rsvp_status_block()
        context.cfp_status_block = self.get_cfp_status_block()
        context.all_cfp_link = f"/dashboard/cfp/all/{self.route.split('c/')[1]}"

        # Add user registration status
        context.registration_status = self.get_user_registration_status()

        # Add event statistics
        context.event_stats = self.get_event_stats()

        # Add schedule data using existing API - keep nested structure for proper ordering
        from fossunited.api.schedule import get_event_schedule

        schedule_dict = get_event_schedule(self.name)
        context.schedule_data = self.format_schedule_for_template(schedule_dict)

        context.pagetitle, context.description, context.image = self.get_meta()
        context.social_links = context.chapter.get_social_links()
        context.status_concluded = self.status == "Concluded"
        context.status_live = self.status == "Live"

        # Add permission check for managing event
        context.can_manage_event = check_if_chapter_or_event_core_member(self.name)
        context.event_dashboard_url = f"/dashboard/event/{self.name}"

        context.map_lat = None
        context.map_lng = None

        if self.map_coordinate and self.map_coordinate not in ["None,None", ",", ""]:
            try:
                lat_str, lng_str = self.map_coordinate.split(",")
                context.map_lat = float(lat_str) if lat_str and lat_str != "None" else None
                context.map_lng = float(lng_str) if lng_str and lng_str != "None" else None
            except (ValueError, AttributeError):
                pass

        context.breadcrumbs = self.get_breadcrumb()

        context.livestream_youtube_id = get_youtube_id(self.livestream_embed_link)

        context.no_cache = 1


@frappe.whitelist()
def get_event_connection_counts(events: str | list):
    import json

    if isinstance(events, str):
        events = json.loads(events)

    if not events:
        return {}

    def get_counts(doctype):
        rows = frappe.db.get_all(
            doctype,
            filters={"event": ["in", events]},
            fields=["event", "count(*) as count"],
            group_by="event",
        )
        return {r.event: r.count for r in rows}

    cfp = get_counts(PROPOSAL)
    rsvp = get_counts(RSVP_RESPONSE)

    return {
        event: {
            "cfp_count": cfp.get(event, 0),
            "rsvp_count": rsvp.get(event, 0),
        }
        for event in events
    }


def extract_map_coordinates(map_url):
    """
    Extract latitude and longitude from map URLs.
    Returns tuple: (lat, lng) or (None, None) if not found
    """
    import re

    import requests

    if not map_url:
        return None, None

    # Follow redirects for shortened URLs (goo.gl, maps.app.goo.gl)
    if "goo.gl" in map_url:
        try:
            response = requests.head(map_url, allow_redirects=True, timeout=5)
            map_url = response.url
        except requests.RequestException:
            return None, None

    # domain.com/lat,lng or domain.com/path/lat,lng
    match = re.search(r"/(-?\d+\.?\d*),(-?\d+\.?\d*)(?:[/#?]|$)", map_url)
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        # valid lat/lng ranges
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return lat, lng

    # OSM format: #zoom/lat/lng
    match = re.search(r"#[\d.]+/([-\d.]+)/([-\d.]+)", map_url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Google Maps @ format: @lat,lng,zoom
    match = re.search(r"@([-\d.]+),([-\d.]+)", map_url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Google Maps !3d and !4d format
    lat_match = re.search(r"!3d([-\d.]+)", map_url)
    lng_match = re.search(r"!4d([-\d.]+)", map_url)
    if lat_match and lng_match:
        return float(lat_match.group(1)), float(lng_match.group(1))

    # OSMand pin format: pin=lat,lng
    match = re.search(r"[?&]pin=([-\d.]+),([-\d.]+)", map_url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # OpenStreetMap directions with to= parameter: to=lat%2Clng
    match = re.search(r"[?&]to=([-\d.]+)%2C([-\d.]+)", map_url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Direct lat/lng query parameters
    match = re.search(r"[?&]lat=([-\d.]+).*[?&]lng=([-\d.]+)", map_url, re.IGNORECASE)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Reverse pattern: lng, lat
    match = re.search(r"[?&]lng=([-\d.]+).*[?&]lat=([-\d.]+)", map_url, re.IGNORECASE)
    if match:
        return float(match.group(2)), float(match.group(1))

    # Google q param: q=lat,lng
    match = re.search(r"[?&]q=([-\d.]+),([-\d.]+)", map_url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # OSM shortlink with way/node/relation parameter: osm.org/go/xxxxx?way=123
    match = re.search(r"osm\.org/go/[^?]+\?(node|way|relation)=([\d]+)", map_url)
    if match:
        obj_type, obj_id = match.groups()
        # Rewrite URL to standard format and continue to API fetch below
        map_url = f"https://www.openstreetmap.org/{obj_type}/{obj_id}"

    # OSM node/way/relation - fetch from API
    match = re.search(r"/(node|way|relation)/([\d]+)", map_url)
    if match:
        obj_type, obj_id = match.groups()
        try:
            # Fetch object from OSM API
            response = requests.get(
                f"https://www.openstreetmap.org/api/0.6/{obj_type}/{obj_id}.json",
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])

                if not elements:
                    return None, None

                element = elements[0]

                # Direct coordinates (for nodes)
                if element.get("lat") is not None and element.get("lon") is not None:
                    return float(element["lat"]), float(element["lon"])

                # Center coordinates (for some ways/relations)
                center = element.get("center")
                if center and center.get("lat") is not None and center.get("lon") is not None:
                    return float(center["lat"]), float(center["lon"])

                # For ways without center: fetch nodes and calculate centroid
                nodes_list = element.get("nodes", [])
                if nodes_list:
                    # Remove duplicate nodes (closing polygons)
                    unique_nodes = list(dict.fromkeys(nodes_list))
                    node_ids = ",".join(
                        map(str, unique_nodes)  # nosemgrep: frappe-no-functional-code
                    )

                    nodes_response = requests.get(
                        f"https://www.openstreetmap.org/api/0.6/nodes.json?nodes={node_ids}",
                        timeout=5,
                    )

                    if nodes_response.status_code == 200:
                        nodes_data = nodes_response.json()
                        nodes = [
                            n
                            for n in nodes_data.get("elements", [])
                            if n.get("lat") is not None and n.get("lon") is not None
                        ]

                        if nodes:
                            avg_lat = sum(n["lat"] for n in nodes) / len(nodes)
                            avg_lon = sum(n["lon"] for n in nodes) / len(nodes)
                            return float(avg_lat), float(avg_lon)

        except (requests.RequestException, ValueError, KeyError):
            pass

    return None, None
