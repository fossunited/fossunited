# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from fossunited.api.chapter import check_if_chapter_or_event_core_member


class EventFreeTicketCode(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Data | None
        event: DF.Link
        full_name: DF.Data | None
        is_used: DF.Check
        mapped_email: DF.Data
        max_count: DF.Int
        other_tier: DF.Data | None
        tier: DF.Literal[
            "Volunteer",
            "Speaker/Workshop Host",
            "Community Partner",
            "Sponsor",
            "Diversity Scholar",
            "Booth Manager",
            "Other",
        ]
        used_count: DF.Int
    # end: auto-generated types

    def on_trash(self):
        self.permit_only_team()

    def before_save(self):
        self.permit_only_team()

    def permit_only_team(self):
        """Allow only event/chapter team members to modify."""

        user = frappe.session.user
        roles = frappe.get_roles(user)

        if "System Manager" in roles or "Administrator" in roles:
            return True

        if check_if_chapter_or_event_core_member(self.event):
            return True

        frappe.log_error(
            title="Permission Denied: Free Ticket Code Modification",
            message=f"User {user} attempted to modify free ticket code for event {self.event}",
        )
        frappe.throw(
            _("You are not allowed to modify free ticket codes for this event."),
            frappe.PermissionError,
        )
