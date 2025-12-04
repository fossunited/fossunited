# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import re
import textwrap

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.emailing import (
    handle_email_group_subscription,
)
from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    CORE_TEAM,
    EVENT,
    EVENT_CFP,
    EVENT_SCHEDULE,
    PROPOSAL,
)


class FOSSEventCFPSubmission(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.cfp_submission_reference.cfp_submission_reference import (  # noqa: E501
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

        approvability: DF.Data | None
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
        submitted_by: DF.Link
        subscribe_chapter_mailing: DF.Check
        talk_description: DF.TextEditor
        talk_license: DF.Data | None
        talk_title: DF.Data
        unsure_reviews: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        self.check_status()
        self.validate_linked_cfp_exists()
        self.validate_form_is_live()

    def before_save(self):
        if self.has_value_changed("is_withdrawn"):
            if self.is_withdrawn and self.status == "Approved":
                self.status = "Withdrawn"
                self.proposal_withdrawn_inform_chapter_member()
            elif self.is_withdrawn:
                self.status = "Withdrawn"
            else:
                self.status = "Review Pending"
        self.set_route()
        self.set_scores()
        self.handle_status_change()
        self.validate_session_type_permissions()
        if self.has_value_changed("subscribe_chapter_mailing"):
            self.handle_email_group("CFP Proposers")

    def after_insert(self):
        # Always handle initial subscription on insert
        self.handle_email_group("CFP Proposers")

    def set_route(self):
        event_route = frappe.db.get_value(EVENT, self.event, "route")
        self.route = f"{event_route}/cfp/{self.name}"

    def set_scores(self):
        statistics = self.get_review_statistics()
        self.positive_reviews = statistics[0]["percentage"]
        self.negative_reviews = statistics[1]["percentage"]
        self.unsure_reviews = statistics[2]["percentage"]
        self.approvability = statistics[3]["percentage"]

    def check_status(self) -> None:
        if self.status != "Review Pending":
            frappe.throw("Illegal status change", frappe.ValidationError)

    def validate_linked_cfp_exists(self) -> None:
        if not frappe.db.exists(EVENT_CFP, self.linked_cfp):
            frappe.throw("Invalid CFP", frappe.DoesNotExistError)

    def validate_form_is_live(self) -> None:
        linked_cfp = frappe.get_doc(EVENT_CFP, self.linked_cfp)
        if not linked_cfp.status == "Live":
            frappe.throw("The CFP Form for this event is not live", frappe.PermissionError)

    def validate_session_type_permissions(self) -> None:
        if self.session_type != "Invited Talk":
            return
        user = frappe.session.user
        # Block Website Users outright
        if frappe.db.get_value("User", user, "user_type") == "Website User":
            frappe.throw("You cannot set Session Type to 'Invited Talk'.", frappe.PermissionError)
        # Allow only specific desk roles to set this value
        allowed_roles = {"System Manager", "Chapter Team Member", "CFP Reviewer"}
        if not set(frappe.get_roles(user)).intersection(allowed_roles):
            frappe.throw("You cannot set Session Type to 'Invited Talk'.", frappe.PermissionError)

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
        context.session_categories = self.session_categories.splitlines()
        context.status_badge_theme = {
            "Review Pending": "orange",
            "Screening": "blue",
            "Approved": "green",
            "Withdrawn": "red",
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
        context.like = 1 if frappe.session.user in context.likes else 0
        context.like_count = len(context.likes)
        context.talk_video = self.cfp_get_talk_video()

    def get_meta(self, context):
        pagetitle = self.talk_title

        desc_short = textwrap.shorten(re.sub(r"<.*?>", "", self.talk_description), width=150)

        description = "{self.talk_title} is a {self.session_type} proposal for {self.event_name}. {desc_short}".format(  # noqa: E501
            self=self, desc_short=desc_short
        )

        speaker = self.speakers[0]
        if context.anonymous_cfps:
            speaker.full_name = ""
            speaker.designation = ""
            speaker.photo = ""

        chapter_name = frappe.db.get_value(CHAPTER, {"name": self.chapter}, "chapter_name")
        og_url = frappe.db.get_single_value("Ograph Settings", "ograph_url")

        image = "{og_url}/gen/submission?talk_title={talk_title_short}&session_type={self.session_type}&event_name={self.event_name}&speaker_designation={speaker.designation}&speaker_name={speaker.full_name}&speaker_image={speaker.photo}&event_chapter={chapter_name}".format(  # noqa: E501
            self=self,
            og_url=og_url,
            talk_title_short=textwrap.shorten(self.talk_title, width=50),
            chapter_name=chapter_name,
            speaker=speaker,
        )

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

        approvability = 0
        if positive + negative > 0:
            approvability = (positive / (positive + negative)) * 100

        return {
            "positive": positive,
            "negative": negative,
            "unsure": unsure,
            "approvability": int(approvability),
        }

    def get_likes(self) -> list:
        return frappe.db.get_all(
            "Comment",
            {
                "comment_type": "Like",
                "reference_doctype": self.doctype,
                "reference_name": self.name,
            },
            pluck="comment_email",
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

    def get_review_statistics(self):
        reviews = self.get_reviews()
        reviews_len = len(reviews) or 1

        score = {
            "Yes": 0,
            "No": 0,
            "Maybe": 0,
        }

        for review in reviews:
            score[review.to_approve] += 1

        score["approvability"] = (score["Yes"] / (reviews_len - score["Maybe"] or 1)) * 100

        statistics = [
            {
                "fieldname": "positive_reviews",
                "label": f"{score['Yes']} People Approved this Proposal",
                "value": score["Yes"],
                "percentage": int((score["Yes"] / reviews_len) * 100),
                "color": "var(--clr-foss-mint-500)",
                "background": "var(--clr-foss-mint-50)",
            },
            {
                "fieldname": "negative_reviews",
                "label": f"{score['No']} People Rejected this Proposal",
                "value": score["No"],
                "percentage": int((score["No"] / reviews_len) * 100),
                "color": "var(--clr-error-500)",
                "background": "var(--clr-error-50)",
            },
            {
                "fieldname": "unsure_reviews",
                "label": f"{score['Maybe']} People Marked Unsure",
                "value": score["Maybe"],
                "percentage": int((score["Maybe"] / reviews_len) * 100),
                "color": "var(--clr-warning-500)",
                "background": "var(--clr-warning-50)",
            },
            {
                "fieldname": "approvability",
                "label": "Approvability of proposal",
                "value": "",
                "percentage": int(score["approvability"]),
                "color": "216, 97%, 42%",
                "background": "206, 100%, 97%",
            },
        ]

        return statistics

    def get_reviews(self):
        reviews = []
        for review in self.reviews:
            reviews.append(review)

        return reviews

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

    def proposal_withdrawn_inform_chapter_member(self):
        members_email = frappe.db.get_all(
            CHAPTER_MEMBER,
            {
                "parent": self.chapter,
                "role": CORE_TEAM,
            },
            ["email"],
        )

        emails = [m["email"] for m in members_email if m.get("email")]
        to = frappe.db.get_value(CHAPTER, self.chapter, "email")
        message = f"""
        <p>Dear {self.chapter} team,</p>

        <p><b>{self.full_name}</b> has withdrawn their proposal from <b>{self.event_name}</b>,
        which was <b>approved</b> before for the event.</p>

        <p>You can find the proposal link below:</p>

        <p><a href="{frappe.utils.get_url(self.route)}" target="_blank">
            View CFP
        </a></p>

        <p>Regards,<br>
        FOSS United Team</p>
        """

        try:
            frappe.sendmail(
                recipients=to,
                cc=emails,
                subject=f"{self.full_name} has Withdrawn their proposal from {self.event_name}",
                message=message,
                reference_doctype=PROPOSAL,
                reference_name=self.name,
            )

        except Exception as exc:
            frappe.log_error(title="email_core_team:send_failed", message=frappe.get_traceback())
            frappe.throw(f"Failed to send email: {exc}")
