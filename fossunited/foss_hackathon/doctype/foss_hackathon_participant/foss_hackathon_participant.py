# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.api.emailing import handle_email_group_subscription
from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_LOCALHOST,
)


class FOSSHackathonParticipant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data
        full_name: DF.Data
        git_profile: DF.Data | None
        hackathon: DF.Link
        is_student: DF.Check
        localhost: DF.Link | None
        localhost_request_status: DF.Literal[
            "Pending", "Pending Confirmation", "Accepted", "Rejected"
        ]
        organization: DF.Data | None
        subscribe_chapter_mailing: DF.Check
        user: DF.Link | None
        user_profile: DF.Link | None
        wants_to_attend_locally: DF.Check
    # end: auto-generated types

    def after_insert(self):
        self.handle_add_to_email_group()

    def before_save(self):
        if self.has_value_changed("wants_to_attend_locally"):
            self.handle_localhost_request()
        self.handle_localhost_rejection()
        if self.has_value_changed("localhost"):
            self.update_request_status()
        if self.has_value_changed("subscribe_chapter_mailing"):
            self.handle_add_to_email_group()
        if (
            self.has_value_changed("localhost_request_status")
            and self.localhost_request_status == "Accepted"
            and self.localhost
        ):
            self.subscribe_to_localhost_email_group()

    def validate(self):
        if self.wants_to_attend_locally and not self.localhost:
            frappe.throw("No LocalHost value provided", frappe.ValidationError)

    def on_trash(self):
        try:
            # remove from mailing group as well
            self.subscribe_chapter_mailing = 0
            self.handle_add_to_email_group()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Error in on_trash: Unsubscribing from email groups",
            )

    def handle_add_to_email_group(self):
        # Check if user should be subscribed
        event_doc = frappe.get_doc(HACKATHON, self.hackathon)

        handle_email_group_subscription(
            emails=[self.email],
            chapter=event_doc.chapter,
            event=self.hackathon,
            subscribe_to_chapter=self.subscribe_chapter_mailing,
            subscribe_to_event=self.subscribe_chapter_mailing,
            document_type_event=HACKATHON,
        )

    def subscribe_to_localhost_email_group(self):
        event_doc = frappe.get_doc(HACKATHON, self.hackathon)

        handle_email_group_subscription(
            emails=[self.email],
            chapter=event_doc.chapter,
            event=self.localhost,
            subscribe_to_chapter=self.subscribe_chapter_mailing,
            subscribe_to_event=True,
            document_type_event=HACKATHON_LOCALHOST,
        )

    def update_request_status(self):
        self.localhost_request_status = "Pending"

    def handle_localhost_rejection(self):
        if not self.has_value_changed("localhost") and self.localhost_request_status == "Rejected":
            localhost_name = frappe.db.get_value(
                HACKATHON_LOCALHOST, self.localhost, "localhost_name"
            )
            self.add_comment(
                "Comment",
                f"Rejected by localhost: {localhost_name}",
            )
            self.wants_to_attend_locally = False

    def handle_localhost_request(self):
        prev_doc = self.get_doc_before_save()
        if not prev_doc:
            return

        if frappe.db.get_value("User", frappe.session.user, "user_type") == "System User":
            return

        if not self.wants_to_attend_locally:
            return

        if (self.localhost == prev_doc.localhost) and self.localhost_request_status == "Rejected":
            frappe.throw(
                "You have already been rejected from this localhost.",
                frappe.PermissionError,
            )

        self.localhost_request_status = "Pending"
