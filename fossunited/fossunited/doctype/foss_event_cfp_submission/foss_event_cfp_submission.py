# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.emailing import add_to_email_group, create_email_group
from fossunited.doctype_ids import EVENT, EVENT_CFP


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
        intended_audience: DF.Literal["Beginner", "Intermediate", "Advanced"]  # noqa: F821
        is_first_talk: DF.Literal["Yes", "No"]  # noqa: F821
        is_published: DF.Check
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
            "Talk", "Lightning Talk", "Panel Discussion", "Birds of Feather(BoF)", "Workshop"  # noqa: F722, F821
        ]
        speakers: DF.Table[CFPSubmissionSpeaker]
        status: DF.Literal["Review Pending", "Screening", "Approved", "Rejected"]  # noqa: F722, F821
        submitted_by: DF.Link | None
        talk_description: DF.TextEditor
        talk_reference: DF.Data | None
        talk_title: DF.Data
        unsure_reviews: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        self.check_status()
        self.validate_linked_cfp_exists()

    def before_save(self):
        self.set_route()
        self.set_scores()
        self.handle_status_change()

    def after_insert(self):
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

    def get_context(self, context):
        event = frappe.get_doc(EVENT, self.event)
        context.anonymous_cfps = frappe.db.get_value(
            EVENT_CFP, self.linked_cfp, "anonymise_proposals"
        )
        context.breadcrumbs = self.get_breadcrumb(event)
        context.session_categories = self.session_categories.splitlines()
        context.status_badge_theme = {
            "Review Pending": "orange",
            "Screening": "blue",
            "Approved": "green",
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

        # For Like
        context.reference_doctype = self.doctype
        context.reference_name = self.name
        context.likes = self.get_likes()
        context.like = 1 if frappe.session.user in context.likes else 0
        context.like_count = len(context.likes)

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
            approvability = (positive + (unsure / 2) / (positive + negative + unsure)) * 100

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

    def handle_email_group(self, type) -> None:
        if not frappe.db.exists(
            "Email Group",
            {
                "reference_document": self.event,
                "document_type": EVENT,
                "group_type": type,
            },
        ):
            create_email_group(
                type=type,
                reference_document=self.event,
                document_type=EVENT,
            )

        email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.event,
                "document_type": EVENT,
                "group_type": type,
            },
            ["name"],
        )

        for speaker in self.speakers:
            if not speaker.email:
                continue

            try:
                add_to_email_group(email_group, speaker.email)
            except frappe.DuplicateEntryError:
                continue
