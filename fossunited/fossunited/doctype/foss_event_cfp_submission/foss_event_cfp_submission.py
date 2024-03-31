# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.fossunited.utils import (
    get_doc_likes,
    get_event_volunteers,
)


class FOSSEventCFPSubmission(WebsiteGenerator):
    def before_save(self):
        self.set_route()
        self.set_scores()

    def set_route(self):
        event_route = frappe.db.get_value(
            "FOSS Chapter Event", self.event, "route"
        )
        self.route = f"{event_route}/cfp/{self.name}"

    def set_scores(self):
        statistics = self.get_review_statistics()
        self.positive_reviews = statistics[0]["percentage"]
        self.negative_reviews = statistics[1]["percentage"]
        self.unsure_reviews = statistics[2]["percentage"]
        self.approvability = statistics[3]["percentage"]

    def get_context(self, context):
        context.cfp = frappe.get_doc(
            "FOSS Event CFP", self.linked_cfp
        )
        context.speaker = frappe.get_doc(
            "FOSS User Profile", {"user": self.submitted_by}
        )
        context.likes = get_doc_likes(self.doctype, self.name)
        context.liked_by_user = frappe.session.user in context.likes
        context.reviewers = self.get_reviewers(context.cfp)
        context.is_reviewer = frappe.session.user in [
            reviewer["email"] for reviewer in context.reviewers
        ]
        context.nav_items = self.get_navbar_items(context)
        context.submitter_foss_profile = frappe.get_doc(
            "FOSS User Profile", {"user": self.submitted_by}
        )
        context.review_statistics = self.get_review_statistics()
        context.reviews = self.get_reviews()
        context.already_reviewed = self.check_if_already_reviewed(
            context
        )
        context.no_cache = 1

    def get_navbar_items(self, context):
        nav_items = [
            "proposal_details",
            "about_speaker",
            "proposal_reviews",
        ]

        volunteers = get_event_volunteers(self.event)
        if (
            context.cfp.anonymise_proposals
            and not self.status == "Approved"
        ):
            nav_items.remove("about_speaker")

        if (
            not context.is_reviewer
            and frappe.session.user
            not in [volunteer.email for volunteer in volunteers]
            and not frappe.session.user == self.submitted_by
        ):
            nav_items.remove("proposal_reviews")

        return nav_items

    def get_reviewers(self, cfp):
        reviewers = []
        for reviewer in cfp.cfp_reviewers:
            reviewers.append(
                {
                    "full_name": reviewer.full_name,
                    "email": reviewer.email,
                    "profile": reviewer.reviewer,
                }
            )

        return reviewers

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

        score["approvability"] = (
            score["Yes"] / (reviews_len - score["Maybe"])
        ) * 100

        statistics = [
            {
                "fieldname": "positive_reviews",
                "label": f'{score["Yes"]} People Approved this Proposal',
                "value": score["Yes"],
                "percentage": int((score["Yes"] / reviews_len) * 100),
                "color": "var(--clr-foss-mint-500)",
                "background": "var(--clr-foss-mint-50)",
            },
            {
                "fieldname": "negative_reviews",
                "label": f'{score["No"]} People Rejected this Proposal',
                "value": score["No"],
                "percentage": int((score["No"] / reviews_len) * 100),
                "color": "var(--clr-error-500)",
                "background": "var(--clr-error-50)",
            },
            {
                "fieldname": "unsure_reviews",
                "label": f'{score["Maybe"]} People Marked Unsure',
                "value": score["Maybe"],
                "percentage": int(
                    (score["Maybe"] / reviews_len) * 100
                ),
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

    def get_review_templates(self):
        templates = frappe.get_doc("CFP Review Templates")
        templates_dict = {
            "Accepted": [],
            "Rejected": [],
            "Not Sure": [],
        }
        for template in templates.reviews_list:
            templates_dict[template.type].append(template.reason)

        return templates_dict

    def check_if_already_reviewed(self, context):
        for review in context.reviews:
            if review.email == frappe.session.user:
                return True

        return False
