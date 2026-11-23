import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.api.emailing import (
    add_to_email_group,
    create_email_group,
    create_newsletter_campaign,
    get_email_groups,
    remove_from_email_group,
    send_campaign,
    send_test_email,
    update_campaign,
)
from fossunited.doctype_ids import CAMPAIGN, CHAPTER, EMAIL_GROUP
from fossunited.tests.factories.foss_chapter_event_factory import (
    FOSSChapterEventFactory,
)
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.user_factory import UserFactory

fake = Faker()


class TestEmailing(FrappeTestCase):
    def setUp(self):
        self.core_team_user = UserFactory.create("with_foss_website_user_role")
        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.core_team_user.name]
        )
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)

        self.setup_campaign()

    def setup_campaign(self):
        with self.set_user(self.core_team_user.name):
            email_group = frappe.get_doc(
                EMAIL_GROUP,
                {
                    "reference_document": self.event.name,
                    "document_type": self.event.doctype,
                    "group_type": "Event Participants",
                },
            )

            for _ in range(3):
                add_to_email_group(email_group.name, fake.unique.email())

            recipient_groups = [
                {
                    "label": email_group.group_type,
                    "value": email_group.name,
                    "description": "",
                }
            ]
            newsletter_data = {
                "subject": fake.sentence(),
                "content_type": "Rich Text",
                "message": fake.paragraph(),
                "email_group": recipient_groups,
                "attachments": [],
            }
            self.newsletter = create_newsletter_campaign(
                data=newsletter_data,
                reference_document=self.event.name,
                document_type=self.event.doctype,
                chapter=self.chapter.name,
            )

    def test_send_test_email(self):
        with self.set_user(self.core_team_user.name):
            send_test_email(campaign_id=self.newsletter.name, email=fake.email())

    def test_send_campaign_persists_email_sent_for_chapter_member(self):
        with self.set_user(self.core_team_user.name):
            send_campaign(campaign_id=self.newsletter.name)

        self.newsletter.reload()
        self.assertTrue(self.newsletter.email_sent)

    def test_create_email_group_creates_group(self):
        group = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )

        self.assertTrue(frappe.db.exists("Email Group", group.name))
        self.assertEqual(group.reference_document, self.event.name)
        self.assertEqual(group.document_type, self.event.doctype)
        self.assertEqual(group.chapter, self.chapter.name)

    def test_create_email_group_returns_existing(self):
        group1 = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )

        group2 = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )

        self.assertEqual(group1.name, group2.name)

        count = frappe.db.count("Email Group", {"name": group1.name})
        self.assertEqual(count, 1)

    def test_add_to_email_group_adds_member(self):
        group = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )
        email = fake.unique.email()
        add_to_email_group(group.name, email)

        self.assertTrue(
            frappe.db.exists("Email Group Member", {"email": email, "email_group": group.name})
        )

    def test_remove_from_email_group_removes_member(self):
        group = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )
        email = fake.unique.email()
        add_to_email_group(group.name, email)

        self.assertTrue(
            frappe.db.exists("Email Group Member", {"email": email, "email_group": group.name})
        )

        remove_from_email_group(group.name, email)

        self.assertFalse(
            frappe.db.exists("Email Group Member", {"email": email, "email_group": group.name})
        )

    def test_add_to_nonexistent_email_group_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            add_to_email_group("non-existent-group", fake.email())

    def _create_foreign_email_group(self):
        """An email group belonging to a different chapter/event than self.chapter/self.event."""
        other_user = UserFactory.create("with_foss_website_user_role")
        other_chapter = FOSSChapterFactory.create("with_members", members=[other_user.name])
        other_event = FOSSChapterEventFactory.create(chapter=other_chapter.name)
        with self.set_user(other_user.name):
            return create_email_group(
                type="Event Participants",
                reference_document=other_event.name,
                document_type=other_event.doctype,
            )

    def test_get_email_groups_requires_chapter_membership(self):
        outsider = UserFactory.create("with_foss_website_user_role")
        with self.set_user(outsider.name):
            with self.assertRaises(frappe.PermissionError):
                get_email_groups(
                    reference_document=self.event.name,
                    document_type=self.event.doctype,
                    chapter=self.chapter.name,
                )

    def test_get_email_groups_requires_chapter_param(self):
        with self.set_user(self.core_team_user.name):
            with self.assertRaises(frappe.PermissionError):
                get_email_groups(
                    reference_document=self.event.name, document_type=self.event.doctype
                )

    def test_get_email_groups_returns_for_chapter_member(self):
        with self.set_user(self.core_team_user.name):
            groups = get_email_groups(
                reference_document=self.event.name,
                document_type=self.event.doctype,
                chapter=self.chapter.name,
            )

        self.assertTrue(any(g.name for g in groups))

    def test_create_newsletter_campaign_rejects_foreign_email_group(self):
        foreign_group = self._create_foreign_email_group()
        newsletter_data = {
            "subject": fake.sentence(),
            "content_type": "Rich Text",
            "message": fake.paragraph(),
            "email_group": [
                {"label": foreign_group.group_type, "value": foreign_group.name, "description": ""}
            ],
            "attachments": [],
        }

        with self.set_user(self.core_team_user.name):
            with self.assertRaises(frappe.PermissionError):
                create_newsletter_campaign(
                    data=newsletter_data,
                    reference_document=self.event.name,
                    document_type=self.event.doctype,
                    chapter=self.chapter.name,
                )

    def test_update_campaign_rejects_foreign_email_group(self):
        foreign_group = self._create_foreign_email_group()

        with self.set_user(self.core_team_user.name):
            with self.assertRaises(frappe.PermissionError):
                update_campaign(
                    campaign_id=self.newsletter.name,
                    data={
                        "email_group": [
                            {
                                "label": foreign_group.group_type,
                                "value": foreign_group.name,
                                "description": "",
                            }
                        ]
                    },
                )

    def test_create_newsletter_campaign_accepts_chapter_own_group(self):
        """A chapter-only campaign (no reference_document) must still accept the
        chapter's own email group, created with reference_document=chapter.name,
        document_type=CHAPTER."""
        chapter_group = frappe.get_doc(
            EMAIL_GROUP,
            {
                "reference_document": self.chapter.name,
                "document_type": CHAPTER,
                "group_type": "Chapter Event Participants",
            },
        )
        newsletter_data = {
            "subject": fake.sentence(),
            "content_type": "Rich Text",
            "message": fake.paragraph(),
            "email_group": [
                {
                    "label": chapter_group.group_type,
                    "value": chapter_group.name,
                    "description": "",
                }
            ],
            "attachments": [],
        }

        with self.set_user(self.core_team_user.name):
            newsletter = create_newsletter_campaign(
                data=newsletter_data,
                document_type=CHAPTER,
                chapter=self.chapter.name,
            )

        self.assertTrue(frappe.db.exists(CAMPAIGN, newsletter.name))

    def test_update_campaign_ignores_sender_fields(self):
        original_sender_name = self.newsletter.sender_name
        original_sender_email = self.newsletter.sender_email

        with self.set_user(self.core_team_user.name):
            update_campaign(
                campaign_id=self.newsletter.name,
                data={
                    "sender_name": "Spoofed Sender",
                    "sender_email": "spoofed@example.com",
                    "subject": "Updated subject",
                },
            )

        self.newsletter.reload()
        self.assertEqual(self.newsletter.sender_name, original_sender_name)
        self.assertEqual(self.newsletter.sender_email, original_sender_email)
        self.assertEqual(self.newsletter.subject, "Updated subject")
