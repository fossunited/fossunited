import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.api.emailing import (
    add_to_email_group,
    create_email_group,
    create_newsletter_campaign,
    remove_from_email_group,
    send_campaign,
    send_test_email,
)
from fossunited.doctype_ids import EMAIL_GROUP
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
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

    def test_send_campaign(self):
        with self.set_user(self.core_team_user.name):
            send_campaign(campaign_id=self.newsletter.name)

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
