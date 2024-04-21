# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.fossunited.forms import create_submission


class FOSSEventCFP(WebsiteGenerator):
    def before_insert(self):
        self.assign_reviewers()

    def assign_reviewers(self):
        reviewers = frappe.get_single(
            "FOSS Global CFP Review Settings"
        ).members
        print(reviewers)

        for reviewer in reviewers:
            self.append(
                "cfp_reviewers",
                {
                    "reviewer": reviewer.profile,
                    "email": reviewer.email,
                    "full_name": reviewer.full_name,
                },
            )

    def before_save(self):
        self.set_route()
        self.enable_cfp_tab()

    def set_route(self):
        event_route = frappe.db.get_value(
            "FOSS Chapter Event", self.event, "route"
        )
        self.route = f"{event_route}/cfp"

    def enable_cfp_tab(self):
        frappe.db.set_value(
            "FOSS Chapter Event", self.event, "show_cfp", 1
        )

    def get_context(self, context):
        context.submissions = get_cfp_submissions(self.name)
        context.event = frappe.get_doc(
            "FOSS Chapter Event", self.event
        )
        context.event_name = self.event_name
        context.event_date = frappe.db.get_value(
            "FOSS Chapter Event", self.event, "event_start_date"
        ).strftime("%B %d, %Y")
        context.submission_doctype = "FOSS Event CFP Submission"
        context.already_submitted = (
            True if self.check_if_already_submitted() else False
        )

        context.form_fields = self.get_form_fields()
        context.no_cache = 1

    def get_form_fields(self):
        try:
            last_doc = frappe.get_last_doc(
                "FOSS Event CFP Submission",
                filters={"submitted_by": frappe.session.user},
            )
        except frappe.exceptions.DoesNotExistError:
            last_doc = {}

        meta = frappe.get_meta("FOSS Event CFP Submission").as_dict()
        current_section = None

        form_fields = [
            {
                "fieldname": "full_name",
                "fieldtype": "Data",
                "label": "Full Name",
                "reqd": 1,
                "value": frappe.get_value(
                    "User", frappe.session.user, "full_name"
                ),
            },
            {
                "fieldname": "email",
                "fieldtype": "Data",
                "label": "Email",
                "reqd": 1,
                "value": frappe.get_value(
                    "User", frappe.session.user, "email"
                ),
            },
            {
                "fieldname": "picture_url",
                "fieldtype": "Data",
                "label": "Picture (URL)",
                "value": last_doc.get("picture_url") or "",
                "description": "Paste a URL for your publicly hosted photo. Keep it in a 1:1 ratio.",
                "reqd": 1,
            },
            {
                "fieldname": "designation",
                "fieldtype": "Data",
                "label": "Designation",
                "reqd": 1,
                "value": last_doc.get("designation") or "",
            },
            {
                "fieldname": "organization",
                "fieldtype": "Data",
                "label": "Organization",
                "value": last_doc.get("organization") or "",
            },
            {
                "fieldname": "bio",
                "fieldtype": "Text Editor",
                "label": "Speaker Bio",
                "reqd": 1,
                "value": last_doc.get("bio") or "",
            },
        ]
        for field in meta["fields"]:
            if field["fieldtype"] == "Column Break":
                continue
            if field["fieldtype"] == "Section Break":
                current_section = field["label"]
                continue
            if current_section in [
                "Meta Info",
                "Personal Information",
                "Custom Answers",
                "CFP Reviews",
                "Review Scores",
            ]:
                continue
            form_fields.append({k: v for k, v in field.items()})

        form_fields.extend(self.get_custom_questions())

        return form_fields

    def get_custom_questions(self):
        custom_questions = []
        for index, question in enumerate(
            self.cfp_custom_questions, start=1
        ):
            custom_questions.append(
                {
                    "fieldname": "custom_question_" + str(index),
                    "fieldtype": question.type,
                    "label": question.question,
                    "options": question.options,
                    "reqd": question.is_mandatory or 0,
                    "description": question.description,
                }
            )
        return custom_questions

    def check_if_already_submitted(self):
        return frappe.db.exists(
            "FOSS Event CFP Submission",
            {
                "linked_cfp": self.name,
                "submitted_by": frappe.session.user,
            },
        )


@frappe.whitelist()
def create_cfp_submission(fields):
    fields_dict = {
        "doctype": "FOSS Event CFP Submission",
        "submitted_by": frappe.session.user,
    }
    fields_dict.update(frappe.parse_json(fields))
    return create_submission(fields_dict)


@frappe.whitelist()
def get_cfp_submissions(linked_cfp):
    submissions = frappe.get_all(
        "FOSS Event CFP Submission",
        fields=["*"],
        filters={
            "submitted_by": frappe.session.user,
            "linked_cfp": linked_cfp,
        },
    )
    frappe.form_dict["submissions"] = submissions
    return submissions
