# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import re
import textwrap

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.chapter import get_chapter_members_email
from fossunited.api.emailing import (
    handle_email_group_subscription,
)
from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_CFP,
    EVENT_SCHEDULE,
    PROPOSAL,
    USER_PROFILE,
)
from fossunited.fossunited.utils import get_youtube_id, sanitize_text_content


class FOSSEventCFPSubmission(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.cfp_submission_reference.cfp_submission_reference import (
            CFPSubmissionReference,
        )
        from fossunited.fossunited.doctype.cfp_submission_speaker.cfp_submission_speaker import (
            CFPSubmissionSpeaker,
        )
        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )
        from fossunited.fossunited.doctype.foss_event_cfp_review.foss_event_cfp_review import (
            FOSSEventCFPReview,
        )

        accept_coc: DF.Check
        attendance_confirmed: DF.Check
        bio: DF.TextEditor | None
        chapter: DF.Data | None
        custom_answers: DF.Table[FOSSCustomAnswer]
        designation: DF.Data | None
        email: DF.Data | None
        event: DF.Data | None
        event_name: DF.Data | None
        first_name: DF.Data | None
        full_name: DF.Data | None
        intended_audience: DF.Literal["Beginner", "Intermediate", "Advanced"]
        is_first_talk: DF.Literal["Yes", "No"]
        is_published: DF.Check
        is_withdrawn: DF.Check
        key_takeaways: DF.TextEditor | None
        last_name: DF.Data | None
        linked_cfp: DF.Link
        negative_reviews: DF.Data | None
        organization: DF.Data | None
        picture_url: DF.Data | None
        positive_reviews: DF.Data | None
        references: DF.Table[CFPSubmissionReference]
        reviews: DF.Table[FOSSEventCFPReview]
        route: DF.Data | None
        session_categories: DF.Text | None
        session_type: DF.Literal[
            "Talk",
            "Lightning Talk",
            "Panel Discussion",
            "Birds of Feather(BoF)",
            "Workshop",
            "Invited Talk",
        ]
        speakers: DF.Table[CFPSubmissionSpeaker]
        status: DF.Literal["Review Pending", "Screening", "Approved", "Rejected", "Withdrawn"]
        submitted_by: DF.Link | None
        subscribe_chapter_mailing: DF.Check
        talk_description: DF.TextEditor
        talk_license: DF.Data | None
        talk_title: DF.Data
        unsure_reviews: DF.Data | None
    # end: auto-generated types

    def has_permission(self, permtype="read", user=None):
        """Grant access to the submitter and all speakers on the proposal."""
        _user = user or frappe.session.user
        if _user == "Guest":
            return super().has_permission(permtype)

        speaker_emails = [s.email for s in self.speakers if s.email]
        if _user == self.submitted_by or _user in speaker_emails:
            return True

        roles = set(frappe.get_roles(_user))
        if "System Manager" in roles or "CFP Reviewer" in roles:
            return super().has_permission(permtype)

        if "Chapter Team Member" in roles:
            from fossunited.fossunited.permissions import _ctm_chapters

            return bool(self.chapter and self.chapter in _ctm_chapters(_user))

        return super().has_permission(permtype)

    def validate(self):
        self.bio = sanitize_text_content(self.bio)
        self.talk_description = sanitize_text_content(self.talk_description)
        self.key_takeaways = sanitize_text_content(self.key_takeaways)

    def before_insert(self):
        self.check_status()
        self.validate_linked_cfp_exists()
        self.validate_form_is_live()
        self._set_name_from_first_speaker()

    def _set_name_from_first_speaker(self):
        if not self.speakers:
            return
        parts = (self.speakers[0].full_name or "").strip().split(" ", 1)
        self.first_name = parts[0]
        self.last_name = parts[1] if len(parts) > 1 else ""
        self.full_name = self.speakers[0].full_name

    def before_save(self):
        if self.has_value_changed("is_withdrawn"):
            if self.is_withdrawn and self.status == "Approved":
                self.status = "Withdrawn"
                self.notify_team_approved_proposal_withdrawn()
            elif self.is_withdrawn:
                self.status = "Withdrawn"
            else:
                self.status = "Review Pending"
        self.set_route()
        self.set_scores()
        self.handle_status_change()
        self.validate_session_type_permissions()
        self.validate_review_ownership()
        if self.has_value_changed("subscribe_chapter_mailing"):
            self.handle_email_group("CFP Proposers")
        self.notify_proposer_on_review()

    def after_insert(self):
        # Always handle initial subscription on insert
        self.handle_email_group("CFP Proposers")
        self._link_speaker_users()

    def _link_speaker_users(self):
        """Set linked_user (FOSS User Profile) on speaker rows whose email has a profile."""
        emails = [s.email for s in self.speakers if s.email and not s.linked_user]
        if not emails:
            return
        profile_map = {
            p.user: p.name
            for p in frappe.db.get_all(USER_PROFILE, {"user": ("in", emails)}, ["name", "user"])
        }
        for speaker in self.speakers:
            profile_name = profile_map.get(speaker.email)
            if profile_name:
                frappe.db.set_value(
                    "CFP Submission Speaker",
                    speaker.name,
                    "linked_user",
                    profile_name,
                    update_modified=False,
                )

    def set_route(self):
        event_route = frappe.db.get_value(EVENT, self.event, "route")
        self.route = f"{event_route}/cfp/{self.name}"

    def set_scores(self):
        total = len(self.reviews) or 1
        yes = sum(1 for r in self.reviews if r.to_approve == "Yes")
        no = sum(1 for r in self.reviews if r.to_approve == "No")
        maybe = sum(1 for r in self.reviews if r.to_approve == "Maybe")
        self.positive_reviews = int((yes / total) * 100)
        self.negative_reviews = int((no / total) * 100)
        self.unsure_reviews = int((maybe / total) * 100)

    def check_status(self) -> None:
        if self.status != "Review Pending":
            frappe.throw(
                _("New CFP submissions must start with status 'Review Pending'"),
                frappe.ValidationError,
            )

    def validate_linked_cfp_exists(self) -> None:
        if not frappe.db.exists(EVENT_CFP, self.linked_cfp):
            frappe.throw(_("Invalid CFP"), frappe.DoesNotExistError)

    def validate_form_is_live(self) -> None:
        linked_cfp = frappe.get_doc(EVENT_CFP, self.linked_cfp)
        if not linked_cfp.status == "Live":
            frappe.throw(_("The CFP Form for this event is not live"), frappe.PermissionError)

    def validate_session_type_permissions(self) -> None:
        if self.session_type != "Invited Talk":
            return
        if not self.has_value_changed("session_type"):
            return
        allowed_roles = {"System Manager", "Chapter Team Member", "CFP Reviewer"}
        if not allowed_roles.intersection(frappe.get_roles()):
            frappe.throw(
                _("You cannot set Session Type to 'Invited Talk'."),
                frappe.PermissionError,
            )

    def get_context(self, context):
        event = frappe.get_doc(EVENT, self.event)
        cfp = frappe.db.get_value(
            EVENT_CFP,
            self.linked_cfp,
            ["anonymise_proposals", "has_public_custom_responses"],
            as_dict=True,
        )
        context.anonymous_cfps = cfp.anonymise_proposals
        context.has_public_custom_responses = cfp.has_public_custom_responses
        context.breadcrumbs = self.get_breadcrumb(event)
        context.session_categories = (
            self.session_categories.splitlines() if self.session_categories else []
        )
        context.status_badge_theme = {
            "Review Pending": "orange",
            "Screening": "blue",
            "Approved": "green",
            "Withdrawn": "gray",
            "Rejected": "red",
        }
        context.tabs = [
            {
                "label": "Details",
                "name": "proposal_details",
            },
            {
                "label": "Reviews",
                "name": "proposal_reviews",
            },
        ]

        context.review_badge = {
            "Yes": {
                "label": "Approved",
                "theme": "green",
            },
            "No": {
                "label": "Rejected",
                "theme": "red",
            },
            "Maybe": {
                "label": "Not Sure",
                "theme": "orange",
            },
        }

        context.review_scores = self.get_review_scores()
        context.total_reviews = len(self.reviews)

        context.pagetitle, context.description, context.image = self.get_meta(context)

        # For Like
        context.reference_doctype = self.doctype
        context.reference_name = self.name
        context.likes = self.get_likes()
        context.like_count = len(context.likes)
        user = frappe.session.user
        if user == "Guest":
            # Check by IP address for guests
            current_ip = frappe.local.request_ip
            context.like = (
                1 if any(lik.get("ip_address") == current_ip for lik in context.likes) else 0
            )
        else:
            # Check by email for logged-in users
            context.like = (
                1 if any(lik.get("comment_email") == user for lik in context.likes) else 0
            )

        context.talk_video = self.cfp_get_talk_video()
        context.youtube_embed_id = get_youtube_id(context.talk_video)

        user = frappe.session.user
        speaker_emails = [s.email for s in self.speakers if s.email]
        context.is_owner = user != "Guest" and (
            user == self.submitted_by or user == self.email or user in speaker_emails
        )

        _visible_filters = {"is_published": 1, "cfp_visibility": "Everyone"}

        # Speaker profile URLs keyed by email (suppressed when CFP is anonymous)
        context.speaker_profile_map = {}
        if speaker_emails and not context.anonymous_cfps:
            rows = frappe.db.get_all(
                USER_PROFILE,
                filters={"user": ["in", speaker_emails], **_visible_filters},
                fields=["user", "username"],
            )
            context.speaker_profile_map = {p.user: f"/u/{p.username}" for p in rows if p.username}

        # Submitter profile (suppressed when CFP is anonymous)
        context.submitter_profile = None
        if self.submitted_by and not context.anonymous_cfps:
            profile = frappe.db.get_value(
                USER_PROFILE,
                {"user": self.submitted_by, **_visible_filters},
                ["username", "full_name", "profile_photo"],
                as_dict=True,
            )
            if profile and profile.username:
                context.submitter_profile = {
                    "url": f"/u/{profile.username}",
                    "full_name": profile.full_name or self.full_name or self.submitted_by,
                    "photo": profile.profile_photo,
                }

        context.no_cache = 1
        if context.is_owner:
            context.cfp_data_json = frappe.as_json(self.as_dict()).replace("</", "<\\/")
            meta = frappe.get_meta(PROPOSAL)
            context.cfp_field_desc_json = frappe.as_json(
                {f.fieldname: f.description for f in meta.fields if f.description}
            ).replace("</", "<\\/")

    def get_meta(self, context):
        pagetitle = self.talk_title

        desc_short = textwrap.shorten(re.sub(r"<.*?>", "", self.talk_description), width=150)

        description = f"{self.talk_title} is a {self.session_type} proposal for {self.event_name}. {desc_short}"

        speaker = self.speakers[0]
        if context.anonymous_cfps:
            speaker.full_name = ""
            speaker.designation = ""
            speaker.photo = ""

        chapter_name = frappe.db.get_value(CHAPTER, {"name": self.chapter}, "chapter_name")
        og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        image = f"{og_url}/gen/submission?talk_title={textwrap.shorten(self.talk_title, width=50)}&session_type={self.session_type}&event_name={self.event_name}&speaker_designation={speaker.designation}&speaker_name={speaker.full_name}&speaker_image={speaker.photo}&event_chapter={chapter_name}"

        return pagetitle, description, image

    def get_review_scores(self) -> dict[str, int]:
        positive = 0
        negative = 0
        unsure = 0

        for review in self.reviews:
            if review.to_approve == "Yes":
                positive += 1
            elif review.to_approve == "No":
                negative += 1
            elif review.to_approve == "Maybe":
                unsure += 1

        return {
            "positive": positive,
            "negative": negative,
            "unsure": unsure,
        }

    def get_likes(self) -> list:
        """Returns list of dicts with comment_email and ip_address for proper guest handling"""
        return frappe.db.get_all(
            "Comment",
            filters={
                "comment_type": "Like",
                "reference_doctype": self.doctype,
                "reference_name": self.name,
            },
            fields=["comment_email", "ip_address"],
            page_length=9999,
        )

    def get_breadcrumb(self, event) -> list[dict[str, str]]:
        crumbs = [
            {
                "route": f"/{event.route}",
                "label": event.event_name,
            },
            {
                "route": f"/{event.route}/cfp/all",
                "label": "All Proposals",
            },
            {
                "label": self.talk_title,
            },
        ]

        return crumbs

    def handle_status_change(self) -> None:
        if not self.has_value_changed("status"):
            return

        if self.status == "Approved":
            self.handle_email_group("Accepted Proposers")

        if self.status == "Rejected":
            self.handle_email_group("Rejected Proposers")

    def handle_email_group(self, email_group_type) -> None:
        emails = [s.email for s in self.speakers if s.email]

        handle_email_group_subscription(
            emails=emails,
            chapter=self.chapter,
            event=self.event,
            event_type=email_group_type,
            chapter_type="Chapter CFP Proposers",
            # NOTE: We mandate subscribe to event mailing cause,
            # ideally CFPs would require some communication to occur by team
            # Again, event is temporary for event_duration. Hope logic sounds intentional?
            # if not, please do raise an issue!
            subscribe_to_event=True,
            subscribe_to_chapter=self.subscribe_chapter_mailing,
            document_type_event=EVENT,
        )

    def cfp_get_talk_video(self) -> str | None:
        """Return the talk video link if CFP is linked in schedule and has a video."""

        talk_scheduled = frappe.db.get_value(
            EVENT_SCHEDULE,
            {"linked_cfp": self.name},
            ["talk_video"],
        )

        return talk_scheduled

    def notify_team_approved_proposal_withdrawn(self):
        """Notify chapter members that an approved proposal has been withdrawn by proposer."""
        team_emails = get_chapter_members_email(self.chapter)
        to = frappe.db.get_value(CHAPTER, self.chapter, "email")
        message = f"""
        <p>Dear {self.chapter} team,</p>

        <p><b>{self.full_name}</b> has withdrawn their proposal from <b>{self.event_name}</b>,
        which was <b>approved</b> before for the event.</p>

        Proposal title: {self.talk_title}
        <p>You can find the proposal link below:</p>

        <p><a href="{frappe.utils.get_url(self.route)}" target="_blank">
            View CFP
        </a></p>

        <p>Regards,<br>
        FOSS United Team</p>
        """

        if not to:
            return

        try:
            frappe.sendmail(
                recipients=[to],
                cc=team_emails,
                subject=f"{self.full_name} has Withdrawn their proposal from {self.event_name}",
                message=message,
                reference_doctype=PROPOSAL,
                reference_name=self.name,
            )

        except Exception as exc:
            frappe.log_error(title="email_core_team:send_failed", message=frappe.get_traceback())
            frappe.throw(f"Failed to send email: {exc}")

    def validate_review_ownership(self):
        """CFP Reviewers can only add/edit their own review row, and only one."""
        roles = set(frappe.get_roles())
        if "System Manager" in roles:
            return
        if not roles & {"CFP Reviewer", "Chapter Team Member", "IndiaFOSS Chairs"}:
            return

        user = frappe.session.user
        old_doc = self.get_doc_before_save()
        old_reviews = {r.name: r for r in old_doc.reviews if r.name} if old_doc else {}

        own_rows = 0
        reverted = False
        for review in self.reviews:
            is_new = not review.name or review.name not in old_reviews
            if is_new:
                if review.email and review.email != user:
                    frappe.throw(
                        _("You can only add reviews under your own account."),
                        frappe.PermissionError,
                    )
                own_rows += 1
            else:
                old = old_reviews[review.name]
                if old.email != user:
                    dirty = (
                        review.reviewer != old.reviewer
                        or review.email != old.email
                        or review.reviewer_profile != old.reviewer_profile
                        or review.to_approve != old.to_approve
                        or review.remarks != old.remarks
                    )
                    if dirty:
                        review.reviewer = old.reviewer
                        review.email = old.email
                        review.reviewer_profile = old.reviewer_profile
                        review.to_approve = old.to_approve
                        review.remarks = old.remarks
                        reverted = True
                else:
                    own_rows += 1

        if reverted:
            frappe.msgprint(
                _("Your edits to other reviewers' rows were discarded."),
                alert=True,
                indicator="red",
            )

        if own_rows > 1:
            frappe.throw(
                _("You can only submit one review per proposal."),
                frappe.PermissionError,
            )

    def notify_proposer_on_review(self):
        """Notify proposer on new or updated review."""
        old_doc = self.get_doc_before_save()
        if self.is_new() or not old_doc:
            return

        old_reviews = {r.name: r for r in old_doc.reviews if r.name}
        for review in self.reviews:
            old_review = old_reviews.get(review.name)

            if not old_review:
                change_type = "new"
            elif review.remarks != old_review.remarks:
                change_type = "remarks_changed"
            else:
                continue

            self._send_review_email(review, change_type, old_review)

    def _send_review_email(self, review, change_type, old_review=None):
        """Helper to send review notification emails."""
        if not self.email:
            return

        speaker_emails = [s.email for s in self.speakers if s.email]
        sub_prefix = "New review" if change_type == "new" else "Review remarks updated"

        try:
            frappe.sendmail(
                recipients=[self.email],
                cc=speaker_emails,
                subject=f"{sub_prefix} on your proposal for {self.event_name}",
                message=self._build_review_message(review, change_type, old_review),
                reference_doctype=PROPOSAL,
                reference_name=self.name,
            )
        except Exception:
            frappe.log_error(
                title="review_notification:send_failed",
                message=frappe.get_traceback(),
            )

    def _build_review_message(self, review, change_type, old_review=None):
        """Build review notification message."""
        base_intro = (
            f"Dear {self.full_name},<br><br>"
            f"Your proposal for <b>{self.event_name}</b>, "
            f"titled <b>{self.talk_title}</b>, has an update.<br><br>"
        )

        if change_type == "new":
            remarks_section = (
                f"Remarks: <pre><code>{review.remarks}</code></pre><br>" if review.remarks else ""
            )
            body = f"<b>A new review has been submitted.</b><br>{remarks_section}"
        else:  # remarks_changed
            body = (
                f"<b>A reviewer has updated their remarks.</b><br>"
                f"Old Remarks: <pre><code>{old_review.remarks}</code></pre><br>"
                f"New Remarks: <pre><code>{review.remarks}</code></pre><br>"
            )

        closing = (
            f"You can access your proposal here: {frappe.utils.get_url(self.route)}<br><br>"
            "Regards,<br>FOSS United Team"
        )

        return base_intro + body + closing
