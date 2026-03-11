# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.api.checkins import (
    add_checkin,
    has_checked_in_today,
    remove_today_checkin,
)
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

        from fossunited.fossunited.doctype.event_check_in.event_check_in import EventCheckIn

        check_ins: DF.Table[EventCheckIn]
        disqualified: DF.Check
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

    def before_insert(self):
        hackathon = frappe.db.get_value(
            HACKATHON,
            {"name": self.hackathon},
            ["is_registration_live", "start_date", "end_date"],
            as_dict=True,
        )

        if not hackathon:
            frappe.throw("Invalid Hackathon selected")

        today = frappe.utils.now_datetime()

        # Registration closed manually
        if not hackathon.is_registration_live:
            frappe.throw(
                "Registrations have been closed for this hackathon!",
                frappe.PermissionError,
            )

        if hackathon.end_date and hackathon.end_date < today:
            frappe.throw(
                "This event has already ended. Registration is no longer allowed.",
                frappe.PermissionError,
            )

    def after_insert(self):
        self.handle_add_to_email_group()
        # Add to status-based localhost group if applicable
        if self.wants_to_attend_locally and self.localhost:
            self.sync_localhost_status_groups(new_status=self.localhost_request_status)

    def before_save(self):
        if self.has_value_changed("wants_to_attend_locally"):
            self.handle_localhost_request()

        self.handle_localhost_rejection()

        if self.has_value_changed("localhost"):
            # Remove from old localhost groups before changing
            old_localhost = (
                self.get_doc_before_save().localhost if self.get_doc_before_save() else None
            )
            if old_localhost:
                self.remove_from_all_localhost_groups(old_localhost)
            self.update_request_status()

        if self.has_value_changed("subscribe_chapter_mailing"):
            self.handle_add_to_email_group()

        if self.has_value_changed("localhost") and self.localhost:
            # Localhost changed — just add to new group
            self.sync_localhost_status_groups(new_status=self.localhost_request_status)
        elif self.has_value_changed("localhost_request_status") and self.localhost:
            # Only status changed within the same localhost
            self.sync_localhost_status_groups(
                new_status=self.localhost_request_status,
                old_status=self._get_old_status(),
            )

    def validate(self):
        if self.wants_to_attend_locally and not self.localhost:
            frappe.throw("No LocalHost value provided", frappe.ValidationError)

    def on_trash(self):
        try:
            # Remove from all email groups
            self.subscribe_chapter_mailing = 0
            self.handle_add_to_email_group()

            # Remove from status-based localhost groups
            if self.localhost:
                self.remove_from_all_localhost_groups()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                "Error in on_trash: Unsubscribing from email groups",
            )

    def handle_add_to_email_group(self):
        """Handle chapter and hackathon event subscription"""
        event_doc = frappe.get_doc(HACKATHON, self.hackathon)

        handle_email_group_subscription(
            emails=[self.email],
            chapter=event_doc.chapter,
            event=self.hackathon,
            subscribe_to_chapter=self.subscribe_chapter_mailing,
            subscribe_to_event=self.subscribe_chapter_mailing,
            document_type_event=HACKATHON,
        )

    def sync_localhost_status_groups(self, old_status=None, new_status=None):
        if not self.localhost:
            return

        event_doc = frappe.get_doc(HACKATHON, self.hackathon)

        # REMOVE from old group
        if old_status:
            # frappe.throw("for old")
            handle_email_group_subscription(
                emails=[self.email],
                chapter=event_doc.chapter,
                event=self.localhost,
                event_type="Event Participants",
                custom_group_title=f"{old_status}-{self.localhost}-Localhost",
                subscribe_to_chapter=self.subscribe_chapter_mailing,
                subscribe_to_event=False,
                document_type_event=HACKATHON_LOCALHOST,
            )

        # ADD to new group
        if new_status:
            handle_email_group_subscription(
                emails=[self.email],
                chapter=event_doc.chapter,
                event=self.localhost,
                event_type="Event Participants",
                custom_group_title=f"{new_status}-{self.localhost}-Localhost",
                subscribe_to_chapter=self.subscribe_chapter_mailing,
                subscribe_to_event=True,
                document_type_event=HACKATHON_LOCALHOST,
            )

    def remove_from_all_localhost_groups(self, localhost_id=None):
        """Remove participant from all localhost status groups

        Args:
            localhost_id: Specific localhost to remove from. If None, uses self.localhost
        """
        target_localhost = localhost_id or self.localhost

        if not target_localhost:
            return

        event_doc = frappe.get_doc(HACKATHON, self.hackathon)
        all_statuses = ["Pending", "Pending Confirmation", "Accepted", "Rejected"]

        for status in all_statuses:
            try:
                handle_email_group_subscription(
                    emails=[self.email],
                    chapter=event_doc.chapter,
                    event=target_localhost,
                    event_type="Event Participants",
                    custom_group_title=f"{status}-{target_localhost}-Localhost",
                    subscribe_to_chapter=self.subscribe_chapter_mailing,
                    subscribe_to_event=False,
                    document_type_event=HACKATHON_LOCALHOST,
                )
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Error removing from {status} group of localhost {target_localhost}",
                )

    def update_request_status(self):
        """Reset status to Pending when localhost changes"""
        self.localhost_request_status = "Pending"

    def handle_localhost_rejection(self):
        """Handle rejection by adding comment and resetting wants_to_attend_locally"""
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
        """Validate localhost request changes"""
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

    def _get_old_status(self):
        """Get previous status value"""
        prev_doc = self.get_doc_before_save()
        return prev_doc.localhost_request_status if prev_doc else None

    def has_permission(self, ptype="read", user=None):
        """Participants can only edit their own record"""
        user = user or frappe.session.user

        if user == "Administrator":
            return True
        if {"System Manager", "Localhost Organizer"} & set(frappe.get_roles(user)):
            return True
        if ptype == "read":
            return True
        if user == "Guest":
            return False
        if ptype == "create":
            return True
        return user in {self.user, self.email}

    @frappe.whitelist()
    def has_checked_in_today(self):
        return has_checked_in_today(self)

    @frappe.whitelist()
    def add_check_in(self):
        # Add to email group and checkin
        result = add_checkin(self)
        if self.localhost:
            checkin_date = frappe.utils.nowdate()
            self.sync_localhost_status_groups(new_status=f"Checkin-{checkin_date}")
        return result

    @frappe.whitelist()
    def remove_today_check_in(self):
        # Remove from email group
        result = remove_today_checkin(self)
        if self.localhost:
            checkin_date = frappe.utils.nowdate()
            self.sync_localhost_status_groups(old_status=f"Checkin-{checkin_date}")
        return result
