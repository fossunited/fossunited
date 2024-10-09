# Copyright (c) 2024, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests import UnitTestCase

from fossunited.api.checkins import checkin_attendee
from fossunited.doctype_ids import CHAPTER, CONFERENCE, EVENT, EVENT_TICKET, USER_PROFILE


class TestFOSSEventTicket(UnitTestCase):
    def setUp(self):
        fake = Faker()

        chapter_member = frappe.db.get_value(USER_PROFILE, {"user": "test1@example.com"}, ["name"])
        self.member_email = "test1@example.com"
        self.member_profile = chapter_member

        if not frappe.db.exists("Role", "Chapter Team Member"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Team Member"}).insert(
                ignore_permissions=True
            )
        if not frappe.db.exists("Role", "Chapter Lead"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Lead"}).insert(
                ignore_permissions=True
            )

        chapter = frappe.get_doc(
            {
                "doctype": CHAPTER,
                "chapter_type": CONFERENCE,
                "chapter_name": fake.name(),
                "email": fake.email(),
                "about_chapter": fake.text(),
                "chapter_members": [{"chapter_member": chapter_member}],
            }
        )
        chapter.insert(ignore_permissions=True)

        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": chapter.name,
                "event_name": fake.name(),
                "event_permalink": fake.slug().replace("-", "_"),
                "status": "Live",
                "event_type": CONFERENCE,
                "event_start_date": datetime.today(),
                "event_end_date": datetime.today() + timedelta(1),
                "event_description": fake.text(),
                "is_paid_event": 1,
                "tickets_status": "Live",
                "tiers": [
                    {
                        "enabled": 1,
                        "title": "General",
                        "price": 100,
                    }
                ],
            }
        )
        event.insert(ignore_permissions=True)

        self.event = event

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_checkin(self):
        fake = Faker()

        # Given that a ticket is created for an event
        ticket = frappe.get_doc(
            {
                "doctype": EVENT_TICKET,
                "event": self.event.name,
                "full_name": fake.name(),
                "email": fake.email(),
                "tier": "General",
            }
        )
        ticket.insert(ignore_permissions=True)
        ticket.reload()

        self.assertFalse(ticket.check_ins)
        # Set the user as a chapter member
        frappe.set_user(self.member_email)

        # When the user checks in the attendee
        checkin_attendee(self.event.name, ticket.as_dict(), self.member_email)

        # Then the check-in data should be saved
        ticket.reload()
        self.assertTrue(ticket.check_ins)

        # When the user tries to check-in the attendee again on the same day
        # Then the user should not be able to check-in the attendee again
        with self.assertRaises(frappe.ValidationError):
            checkin_attendee(self.event.name, ticket.as_dict(), self.member_email)

    def test_checkin_as_non_chapter_member(self):
        fake = Faker()

        # Given that a ticket is created for an event
        ticket = frappe.get_doc(
            {
                "doctype": EVENT_TICKET,
                "event": self.event.name,
                "full_name": fake.name(),
                "email": fake.email(),
                "tier": "General",
            }
        )
        ticket.insert(ignore_permissions=True)
        ticket.reload()

        self.assertFalse(ticket.check_ins)
        # Set the user as a random user
        frappe.set_user("test2@example.com")

        # When the user checks in the attendee
        # Then the user should not have permission to check-in the attendee
        with self.assertRaises(frappe.PermissionError):
            checkin_attendee(self.event.name, ticket.as_dict(), "test2@example.com")
