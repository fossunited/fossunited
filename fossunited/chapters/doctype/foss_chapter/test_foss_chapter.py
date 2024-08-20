# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase


class TestFOSSChapter(FrappeTestCase):
    def setUp(self):
        fake = Faker()

        chapter = frappe.get_doc(
            {
                "doctype": "FOSS Chapter",
                "chapter_name": "Pune",
                "chapter_type": "City Community",
                "city": "Pune",
                "country": "India",
                "email": fake.email(),
                "facebook": fake.url(),
                "instagram": fake.url(),
                "linkedin": fake.url(),
                "mastodon": fake.url(),
                "public_chat_group_url": fake.url(),
                "state": "Maharashtra",
                "x": fake.url(),
            }
        )
        chapter.insert()

        lead_profile = frappe.get_doc("FOSS User Profile", {"user": "test@example.com"})
        chapter.append("chapter_members", {"chapter_member": lead_profile.name, "role": "Lead"})
        chapter.save()

        self.chapter = chapter

    def tearDown(self):
        frappe.delete_doc("FOSS Chapter", self.chapter.name)

    def test_role_assignment_on_create(self):
        # Given a chapter
        chapter = self.chapter

        # When the chapter was created, a lead was assigned to it.
        # Then the lead should have the role of 'Chapter Lead' and 'Chapter Team Member'
        user = frappe.db.get_value("FOSS User Profile", chapter.chapter_members[0].chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)

    def test_role_assignment_on_member_addition(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc("FOSS Chapter", self.chapter.name)

        # When a new member is added to the chapter
        new_member = frappe.get_doc("FOSS User Profile", {"user": "test1@example.com"})

        chapter.append("chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"})
        chapter.save()

        # Then the new member should have the role of 'Chapter Team Member'
        user = frappe.db.get_value("FOSS User Profile", new_member.name, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)
