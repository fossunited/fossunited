# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, STUDENT_CLUB, USER_PROFILE


class TestFOSSChapter(FrappeTestCase):
    def setUp(self):
        fake = Faker()

        chapter = frappe.get_doc(
            {
                "doctype": CHAPTER,
                "chapter_name": fake.text(max_nb_chars=40),
                "chapter_type": STUDENT_CLUB,
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

        if not frappe.db.exists("Role", "Chapter Team Member"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Team Member"}).insert(
                ignore_permissions=True
            )
        if not frappe.db.exists("Role", "Chapter Lead"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Lead"}).insert(
                ignore_permissions=True
            )

        lead_profile = frappe.get_doc(USER_PROFILE, {"user": "test@example.com"})
        chapter.append("chapter_members", {"chapter_member": lead_profile.name, "role": "Lead"})
        chapter.save()

        self.chapter = chapter

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name)

    def test_role_assignment_on_create(self):
        # Given a chapter
        chapter = self.chapter

        # When the chapter was created, a lead was assigned to it.
        # Then the lead should have the role of 'Chapter Lead' and 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, chapter.chapter_members[0].chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)

    def test_role_assignment_on_member_addition(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc(CHAPTER, self.chapter.name)

        # When a new member is added to the chapter
        new_member = frappe.get_doc(USER_PROFILE, {"user": "test1@example.com"})

        chapter.append(
            "chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"}
        )
        chapter.save()

        # Then the new member should have the role of 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, new_member.name, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)

    def test_role_deassignment_on_member_removal(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc(CHAPTER, self.chapter.name)

        new_members = frappe.get_all(
            USER_PROFILE,
            filters=[
                ["user", "like", "%test%"],
                ["name", "not in", [m.chapter_member for m in chapter.chapter_members]],
            ],
        )
        for new_member in new_members:
            chapter.append(
                "chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"}
            )
        chapter.save()

        # When a member is removed from the chapter
        removed_member = chapter.chapter_members[0]
        chapter.chapter_members = [
            m for m in chapter.chapter_members if m.chapter_member != removed_member.chapter_member
        ]
        chapter.save()

        # Then the removed member should not have the role of 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, removed_member.chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})

        # check other members retain the role
        for member in chapter.chapter_members:
            user = frappe.db.get_value(USER_PROFILE, member.chapter_member, "user")
            if not bool(
                frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
            ):
                self.fail(f"Role not retained for {member}")

        self.assertFalse(has_role)
