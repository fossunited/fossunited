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
                "chapter_name": fake.text(max_nb_chars=40),
                "chapter_type": "FOSS Club",
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

    def test_role_deassignment_on_member_removal(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc("FOSS Chapter", self.chapter.name)

        new_members = frappe.get_all("FOSS User Profile", filters=[["user", "like", "%test%"], ["name", "not in", [m.chapter_member for m in chapter.chapter_members]]])
        for new_member in new_members:
            chapter.append("chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"})
        chapter.save()

        # When a member is removed from the chapter
        removed_member = chapter.chapter_members[0]
        chapter.chapter_members = [m for m in chapter.chapter_members if m.chapter_member != removed_member.chapter_member]
        chapter.save()

        # Then the removed member should not have the role of 'Chapter Team Member'
        user = frappe.db.get_value("FOSS User Profile", removed_member.chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})

        # check other members retain the role
        for member in chapter.chapter_members:
            user = frappe.db.get_value("FOSS User Profile", member.chapter_member, "user")
            if not bool(frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})):
                self.fail(f"Role not retained for {member}")

        self.assertFalse(has_role)
