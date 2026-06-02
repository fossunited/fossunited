# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import re
import textwrap

import frappe
from frappe import _
from frappe.exceptions import PermissionError
from frappe.query_builder import DocType
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.profile import is_valid_username
from fossunited.api.sidebar import user_is_chapter_member
from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_TICKET,
    EVENT_VOLUNTEER,
    HACKATHON,
    HACKATHON_ISSUE_PR,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    HACKATHON_PROJECT,
    HACKATHON_RESULT,
    HACKATHON_TEAM_MEMBER,
    LOCALHOST_ORGANIZER,
    PROPOSAL,
    RSVP_RESPONSE,
)
from fossunited.fossunited.utils import sanitize_text_content


class PrivateProfileError(PermissionError):
    """Exception raised when trying to access a private profile."""

    pass


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
        cfp_visibility: DF.Literal["Everyone", "Chapter Volunteers", "Only Me"]
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
        bluesky: DF.Data | None
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
        self.about = sanitize_text_content(self.about)
        self.bio = sanitize_text_content(self.bio)

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
            frappe.log_error(f"Error updating user details: {e!s}")
            frappe.throw(_("Error updating user details"))

    def validate_username(self):
        if not (3 <= len(self.username) <= 30):
            frappe.throw(_("Username must be between 3 and 30 characters"))

        if not re.match(r"^[a-z0-9_\.]+$", self.username):
            frappe.throw(
                _("Username can only contain lowercase letters, numbers, underscores and dots.")
            )

        if re.search(
            r"\.(txt|html|php|js|json|xml|css|htm)$",
            self.username,
            re.IGNORECASE,
        ):
            frappe.throw(_("Username cannot end with extensions like .txt, .html, etc."))

        if not is_valid_username(self.username, self.name):
            frappe.throw(_("Username is already taken or restricted."))

    def set_route(self):
        self.route = f"u/{self.username}"

    def get_user_activity(self, participants):
        # Events the user has attended (concluded only)
        paid_event_ids = frappe.db.get_all(
            EVENT_TICKET, pluck="event", filters={"email": self.email}, page_length=9999
        )
        rsvpd_event_ids = frappe.db.get_all(
            RSVP_RESPONSE,
            pluck="event",
            filters={"email": self.email},
            page_length=9999,
        )
        event_volunteer_ids = frappe.get_all(
            EVENT_VOLUNTEER,  # populated from chap volunteers by default
            filters={"member": self.name},
            pluck="parent",
        )
        attended_event_ids = list(set(rsvpd_event_ids + paid_event_ids + event_volunteer_ids))
        attended = (
            frappe.db.get_all(
                EVENT,
                fields=[
                    "name",
                    "route",
                    "external_event_url",
                    "chapter",
                    "event_start_date",
                    "event_end_date",
                    "event_name",
                    "banner_image",
                    "must_attend",
                    "event_location",
                ],
                filters={
                    "name": ["in", attended_event_ids],
                    "is_published": 1,
                    "status": "Concluded",
                },
            )
            if attended_event_ids
            else []
        )

        # Hackathons the user has attended (participants passed from get_context — no re-query)
        hackathon_participants = participants

        hack_ids = [v.hackathon for v in hackathon_participants]
        hackathon_map = (
            {
                h.name: h
                for h in frappe.db.get_all(
                    HACKATHON,
                    fields=[
                        "name",
                        "route",
                        "chapter",
                        "start_date",
                        "hackathon_type",
                        "hackathon_logo",
                        "only_show_logo",
                        "hackathon_name",
                    ],
                    filters={"name": ["in", hack_ids], "is_published": 1},
                )
            }
            if hack_ids
            else {}
        )

        localhost_ids = [v.localhost for v in hackathon_participants if v.localhost]
        localhost_map = (
            {
                host.name: host
                for host in frappe.db.get_all(
                    HACKATHON_LOCALHOST,
                    fields=["name", "localhost_name", "location"],
                    filters={"name": ["in", localhost_ids], "is_published": 1},
                )
            }
            if localhost_ids
            else {}
        )

        attended_hack = []
        for val in hackathon_participants:
            hack_data = hackathon_map.get(val.hackathon, {})
            local_data = localhost_map.get(val.localhost, {"localhost_name": "", "location": ""})
            attended_hack.append({**hack_data, **local_data})

        # CFP Proposals submitted, and how many of those were approved
        proposals = frappe.db.get_all(
            PROPOSAL,
            fields=["event", "status", "talk_title", "route", "session_type"],
            filters={"email": self.email},
            page_length=9999,
        )

        proposal_event_ids = list({p.event for p in proposals})
        cfp_event_map = (
            {
                e.name: e
                for e in frappe.db.get_all(
                    EVENT,
                    fields=[
                        "name",
                        "chapter",
                        "event_start_date",
                        "event_name",
                        "banner_image",
                        "must_attend",
                        "event_location",
                    ],
                    filters={
                        "name": ["in", proposal_event_ids],
                        "is_published": 1,
                        "status": ["in", ["Live", "Concluded"]],
                    },
                )
            }
            if proposal_event_ids
            else {}
        )

        show_cfps = self.cfp_visibility == "Everyone" or (
            self.cfp_visibility == "Chapter Volunteers"
            and user_is_chapter_member(frappe.session.user)
        )

        cfps = []
        talked = []
        for val in proposals:
            event_data = cfp_event_map.get(val.event)
            if not event_data:
                continue
            if show_cfps:
                cfps.append(event_data | val)
            if val.status == "Approved":
                talked.append(event_data | val)

        ChapterMember = DocType(CHAPTER_MEMBER)
        Chapter = DocType(CHAPTER)

        chapters = (
            frappe.qb.from_(ChapterMember)
            .join(Chapter)
            .on(Chapter.name == ChapterMember.parent)
            .select(
                ChapterMember.parent,
                ChapterMember.role,
                Chapter.name,
                Chapter.route,
                Chapter.chapter_name.as_("title"),
                Chapter.chapter_type,
                Chapter.chapter_status,
            )
            .where((ChapterMember.chapter_member == self.name) & (Chapter.is_published == 1))
        ).run(as_dict=True)
        volunteered = []
        chapter_ids = [c["parent"] for c in chapters]

        for c in chapters:
            volunteered.append(
                {
                    "type": "chapter",
                    "name": c.name,
                    "route": c.route,
                    "title": c.title,
                    "role": c.role,
                    "meta": f"{c.chapter_type} | {c.chapter_status}",
                    "chapter_type": c.chapter_type,
                }
            )

        EventMember = DocType(EVENT_VOLUNTEER)
        Event = DocType(EVENT)

        events = (
            frappe.qb.from_(EventMember)
            .join(Event)
            .on(Event.name == EventMember.parent)
            .select(
                EventMember.parent,
                EventMember.role,
                Event.name,
                Event.route,
                Event.event_name.as_("title"),
                Event.chapter,
                Event.event_start_date,
                Event.event_location,
            )
            .where((EventMember.member == self.name) & (Event.is_published == 1))
        ).run(as_dict=True)
        for e in events:
            if e.chapter in chapter_ids:
                continue
            volunteered.append(
                {
                    "type": "event",
                    "name": e.name,
                    "route": e.route,
                    "title": e.title,
                    "role": e.role,
                    "meta": f"Event | {frappe.utils.formatdate(e.event_start_date, 'd MMM yyyy')}",
                    "event_date": e.event_start_date,
                }
            )

        return attended, attended_hack, talked, cfps, volunteered

    def get_context(self, context):
        if self.is_private and frappe.session.user not in (
            "Administrator",
            self.user,
        ):
            frappe.throw(_("Profile is Private"), PrivateProfileError)

        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(experience.as_dict())
        context.experiences_dict = experiences_dict

        # Fetch participants once; reused by both activity and badges
        participants = frappe.get_all(
            HACKATHON_PARTICIPANT,
            filters={"user_profile": self.name},
            fields=["name", "hackathon", "team", "localhost"],
        )

        if self.show_activity:
            (
                context.attended,
                context.attended_hack,
                context.talked,
                context.cfps,
                context.volunteered,
            ) = self.get_user_activity(participants)

        context.hackathon_badges = self.get_hackathon_badges(participants)
        context.pagetitle, context.description, context.image = self.get_meta()

        context.no_cache = 1

    def get_hackathon_badges(self, participants):
        badges = []

        # 1. Batch-resolve missing team via child table (one query)
        missing_team_names = [p.name for p in participants if not p.team]
        if missing_team_names:
            team_rows = frappe.get_all(
                HACKATHON_TEAM_MEMBER,
                filters={"member": ["in", missing_team_names]},
                fields=["member", "parent"],
            )
            member_to_team = {r.member: r.parent for r in team_rows}
            for p in participants:
                if not p.team:
                    p.team = member_to_team.get(p.name)

        participants_with_team = [p for p in participants if p.team]

        #  2. Bulk-fetch hackathon metadata (name + route)
        hackathon_ids = list({p.hackathon for p in participants})
        hackathon_map = {}  # name → {hackathon_name, route}
        if hackathon_ids:
            hackathon_map = {
                h.name: h
                for h in frappe.get_all(
                    HACKATHON,
                    filters={"name": ["in", hackathon_ids]},
                    fields=["name", "hackathon_name", "route"],
                )
            }

        #  3. Bulk-fetch results for all teams (one query)
        team_ids = list({p.team for p in participants_with_team})
        result_map = {}  # (hackathon, team) → result row
        winning_project_ids = []
        if team_ids:
            result_rows = frappe.get_all(
                HACKATHON_RESULT,
                filters={"parent": ["in", hackathon_ids], "team": ["in", team_ids]},
                fields=["parent", "team", "status", "project"],
            )
            result_map = {(r.parent, r.team): r for r in result_rows}
            winning_project_ids = [r.project for r in result_rows if r.project]

        #  4. Bulk-fetch project routes for winners
        winner_project_route_map = {}
        if winning_project_ids:
            winner_project_route_map = {
                p.name: p.route
                for p in frappe.get_all(
                    HACKATHON_PROJECT,
                    filters={"name": ["in", winning_project_ids]},
                    fields=["name", "route"],
                )
            }

        #  5. Winner badges
        winning_hackathon_ids = set()
        for p in participants_with_team:
            result = result_map.get((p.hackathon, p.team))
            if not result:
                continue
            hack = hackathon_map.get(p.hackathon, frappe._dict())
            project_route = winner_project_route_map.get(result.project)
            badges.append(
                {
                    "type": "winner",
                    "href": f"/{project_route}" if project_route else None,
                    "title": f"{result.status} at {hack.hackathon_name}",
                }
            )
            winning_hackathon_ids.add(p.hackathon)

        #  6. Participant badges
        candidate_teams = [
            p.team for p in participants_with_team if p.hackathon not in winning_hackathon_ids
        ]
        if candidate_teams:
            candidate_projects = frappe.get_all(
                HACKATHON_PROJECT,
                filters={"team": ["in", candidate_teams]},
                fields=[
                    "name",
                    "hackathon",
                    "team",
                    "description",
                    "demo_link",
                    "is_contribution_project",
                    "route",
                ],
            )
            project_by_team = {proj.team: proj for proj in candidate_projects}

            contrib_ids = [
                proj.name
                for proj in candidate_projects
                if proj.is_contribution_project and not proj.demo_link
            ]
            issue_count_map = {}
            if contrib_ids:
                IssuePR = DocType(HACKATHON_ISSUE_PR)
                rows = (
                    frappe.qb.from_(IssuePR)
                    .select(IssuePR.parent, frappe.qb.fn.Count("*").as_("cnt"))
                    .where(IssuePR.parent.isin(contrib_ids))
                    .groupby(IssuePR.parent)
                ).run(as_dict=True)
                issue_count_map = {r.parent: r.cnt for r in rows}

            for p in participants_with_team:
                if p.hackathon in winning_hackathon_ids:
                    continue
                proj = project_by_team.get(p.team)
                if not (proj and proj.description):
                    continue
                issue_count = issue_count_map.get(proj.name, 0)
                qualifies = proj.demo_link or (proj.is_contribution_project and issue_count > 1)
                if not qualifies:
                    continue
                hack = hackathon_map.get(p.hackathon, frappe._dict())
                badges.append(
                    {
                        "type": "participant",
                        "href": f"/{proj.route}" if proj.route else f"/{hack.route}",
                        "title": f"Participant of {hack.hackathon_name}, qualified first round",
                    }
                )

        #  7. Localhost organizer badge (two bulk queries)
        organizer_rows = frappe.get_all(
            LOCALHOST_ORGANIZER,
            filters={"profile": self.name},
            fields=["parent"],
        )
        if organizer_rows:
            localhost_ids = [r.parent for r in organizer_rows]
            localhosts = frappe.get_all(
                HACKATHON_LOCALHOST,
                filters={"name": ["in", localhost_ids]},
                fields=["name", "route", "localhost_name", "parent_hackathon"],
            )
            # Fetch any hackathon not already in hackathon_map
            extra_hack_ids = [
                lh.parent_hackathon
                for lh in localhosts
                if lh.parent_hackathon and lh.parent_hackathon not in hackathon_map
            ]
            if extra_hack_ids:
                for h in frappe.get_all(
                    HACKATHON,
                    filters={"name": ["in", extra_hack_ids]},
                    fields=["name", "hackathon_name", "route"],
                ):
                    hackathon_map[h.name] = h
            for lh in localhosts:
                hack = hackathon_map.get(lh.parent_hackathon, frappe._dict())
                badges.append(
                    {
                        "type": "localhost",
                        "href": f"/{lh.route}",
                        "title": f"LocalHost Organizer for {lh.localhost_name}, {hack.hackathon_name}",
                    }
                )

        #  8. Judge badge (keyed by name; TODO: move to hackathon child table)
        _HACKATHON_JUDGES = {
            "FOSS Hack 2026": [
                "Shree Kumar",
                "Rajandran R",
                "Agriya Khetarpal",
                "Ayushmaan Bora",
                "Manas Kamal",
                "Liyas Thomas",
                "Natarajan Kannan",
                "Arjun Ashok",
            ],
        }
        for hack_name, judges in _HACKATHON_JUDGES.items():
            if self.full_name not in judges:
                continue
            hack = next(
                (h for h in hackathon_map.values() if h.hackathon_name == hack_name),
                None,
            )
            if not hack:
                hack = frappe.db.get_value(
                    HACKATHON,
                    {"hackathon_name": hack_name},
                    ["name", "hackathon_name", "route"],
                    as_dict=True,
                )
            badges.append(
                {
                    "type": "judge",
                    "href": f"/{hack.route}" if hack and hack.route else None,
                    "title": f"Judge for {hack_name}",
                }
            )

        return badges

    def get_meta(self):
        if self.is_private:
            return self.username, "Private Profile", ""

        # eg. Arya | arya_k
        pagetitle = self.full_name + " | " + self.username

        desc_short = ""
        if self.about:
            desc_short = textwrap.shorten(re.sub(r"<.*?>", "", self.about), width=150)

        description = f"{self.full_name} is a Community Member. {desc_short}"

        og_url = None
        if frappe.db.exists("DocType", "Ograph Settings"):
            og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        if og_url:
            image = (
                "{og_url}/gen/profile?"
                "username={username}&"
                "full_name={full_name}&"
                "designation={designation}&"
                "image={image}"
            ).format(
                og_url=og_url,
                username=self.username,
                full_name=self.full_name,
                designation=self.bio or "FOSS United User",
                image=self.profile_photo
                or "/assets/fossunited/images/defaults/user_profile_image.png",
            )
        else:
            image = (
                self.profile_photo or "/assets/fossunited/images/defaults/user_profile_image.png"
            )

        return pagetitle, description, image

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
