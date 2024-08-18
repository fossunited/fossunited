# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import (
    HACKATHON_LOCALHOST,
    LOCALHOST_ORGANIZER,
    USER_PROFILE,
)


class FOSSHackathonLocalHost(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hackathon_localhost_organizer.foss_hackathon_localhost_organizer import (
            FOSSHackathonLocalHostOrganizer,
        )

        city: DF.Link | None
        is_accepting_attendees: DF.Check
        localhost_name: DF.Data
        location: DF.Data | None
        map_link: DF.Data | None
        organizers: DF.Table[FOSSHackathonLocalHostOrganizer]
        parent_hackathon: DF.Link
        state: DF.Link | None
    # end: auto-generated types
    pass

    def before_insert(self):
        self.assign_localhost_organizer_role()

    def on_update(self):
        self.check_if_member_removed()

    def before_save(self):
        if self.has_value_changed("organizers") and (len(self.organizers) > len(self.get_doc_before_save().organizers)):
            self.assign_localhost_organizer_role()

    def assign_localhost_organizer_role(self):
        for member in self.organizers:
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, member.profile, "user"),
            )
            user.add_roles("Localhost Organizer")

    def check_if_member_removed(self):
        prev_doc = self.get_doc_before_save()
        if not (prev_doc and len(prev_doc.organizers) > len(self.organizers)):
            return

        current_organizers = {member.name for member in self.organizers}

        for member in prev_doc.organizers:
            if member.name not in current_organizers:
                self.remove_organizer_role(member)

    def remove_organizer_role(self, old_member):
        if self.other_localhost_member(old_member):
            return

        user = frappe.get_doc(
            "User",
            frappe.db.get_value(USER_PROFILE, old_member.profile, "user"),
        )
        user.remove_roles("Localhost Organizer")

    def other_localhost_member(self, old_member):
        is_member = frappe.db.exists(
            HACKATHON_LOCALHOST,
            [
                [
                    LOCALHOST_ORGANIZER,
                    "profile",
                    "=",
                    old_member.profile,
                ],
                ["name", "!=", self.name],
            ],
        )
        return bool(is_member)
