import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, EMAIL_GROUP
from fossunited.id.roles import CHAPTER_MEMBER
from fossunited.tests.factories import FOSSChapterFactory, UserFactory, get_foss_profile_id


class TestFOSSChapter(FrappeTestCase):
    def setUp(self):
        self.team_member_user = UserFactory.create("with_foss_website_user_role")
        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.team_member_user.name]
        )

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def test_role_assignment_on_create(self):
        self.assertTrue(self.has_team_member_role(self.team_member_user.name))

    def test_role_assignment_on_member_addition(self):
        new_user = UserFactory.create("with_foss_website_user_role")
        profile_name = get_foss_profile_id(new_user.name)
        self.assertFalse(self.has_team_member_role(new_user.name))

        # Add user as chapter member
        with self.set_user(self.team_member_user.name):
            self.chapter.append(
                "chapter_members",
                {"chapter_member": profile_name, "role": "Core Team Member"},
            )
            self.chapter.save()

        self.assertTrue(self.has_team_member_role(new_user.name))

    def test_role_deassignment_on_member_removal(self):
        # Add two new members
        new_members = UserFactory.create_list(2, "with_foss_website_user_role")
        self.chapter.chapter_members = []
        for user in new_members:
            self.chapter.append(
                "chapter_members",
                {"chapter_member": get_foss_profile_id(user.name), "role": "Core Team Member"},
            )
        self.chapter.save()

        # Check that all members have the team member role
        self.assertTrue(all(self.has_team_member_role(user.name) for user in new_members))

        # Remove first member
        removed_member_profile = get_foss_profile_id(new_members[0].name)
        self.chapter.chapter_members = [
            m for m in self.chapter.chapter_members if m.chapter_member != removed_member_profile
        ]
        self.chapter.save()

        # Check that the first member no longer has the team member role
        self.assertFalse(self.has_team_member_role(new_members[0].name))

    def has_team_member_role(self, user: str) -> bool:
        return bool(frappe.db.exists("Has Role", {"role": CHAPTER_MEMBER, "parent": user}))

    def test_unique_chapter_slug(self):
        with self.assertRaises(frappe.UniqueValidationError):
            FOSSChapterFactory.create(slug=self.chapter.slug)

    def test_email_groups_are_created_on_chapter_insert(self):
        expected_group_types = [
            "Chapter Event Participants",
            "Chapter CFP Proposers",
        ]

        for group_type in expected_group_types:
            self.assertTrue(
                frappe.db.exists(
                    EMAIL_GROUP,
                    {
                        "group_type": group_type,
                        "reference_document": self.chapter.name,
                        "document_type": CHAPTER,
                    },
                ),
                msg=f"Email Group '{group_type}' not created for chapter {self.chapter.name}",
            )

        frappe.db.delete(
            EMAIL_GROUP,
            {"reference_document": self.chapter.name, "document_type": CHAPTER},
        )
