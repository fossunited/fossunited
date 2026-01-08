# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT


class EventVolunteer(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        affirmation_for_commitment: DF.Check
        bio: DF.Data | None
        chapter: DF.Link | None
        city: DF.Link | None
        email: DF.Data
        event_linked_field: DF.Link | None
        event_name: DF.Data | None
        identification: DF.Data | None
        other_volunteering_options: DF.Data | None
        past_experience: DF.LongText | None
        phone_number: DF.Data | None
        photo: DF.AttachImage | None
        volunteer_as: DF.Literal[
            "",
            "Marketing",
            "Design",
            "Community Outreach",
            "Speaker Management",
            "Diversity",
            "Video Editing",
            "Sponsorships",
            "Content",
            "Community Outreach",
            "Parallel Sessions Management",
            "Venue Management",
            "Open Spaces Management",
            "Travel Desk",
            "Host/Emcees",
            "Production and Livestream",
            "Adhoc Jobs Management",
            "Volunteer Manager",
            "Other",
        ]
        volunteer_name: DF.Data
        volunteer_status: DF.Literal["", "Accepted", "Waitlisted", "Rejected"]
    # end: auto-generated types

    def before_save(self):
        self.set_chapter_from_event()

    def set_chapter_from_event(self):
        if not self.chapter:
            event_chapter = frappe.db.get_value(EVENT, self.event_linked_field, "chapter")
            self.chapter = event_chapter
