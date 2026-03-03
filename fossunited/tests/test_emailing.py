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
from fossunited.doctype_ids import CHAPTER, EMAIL_GROUP, EVENT

from .utils import insert_test_chapter, insert_test_event

fake = Faker()


class TestEmailing(FrappeTestCase):
    def setUp(self):
        self.core_team_email = "test1@example.com"
        self.chapter = insert_test_chapter(members=[self.core_team_email])
        self.event = insert_test_event(chapter=self.chapter)

        self.setup_campaign()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        # Delete all email groups for the event
        groups = frappe.get_all(
            "Email Group",
            filters={"reference_document": self.event.name},
            pluck="name",
        )
        for group_name in groups:
            frappe.delete_doc("Email Group", group_name, force=True)

    def setup_campaign(self):
        email_group = frappe.get_doc(
            EMAIL_GROUP,
            {
                "reference_document": self.event.name,
                "document_type": self.event.doctype,
                "group_type": "Event Participants",
            },
        )

        recipient_emails = [
            "test2@example.com",
            "test3@example.com",
            "test5@example.com",
        ]
        for email in recipient_emails:
            add_to_email_group(email_group.name, email)

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
        frappe.set_user(self.core_team_email)

        test_email = fake.email()

        send_test_email(campaign_id=self.newsletter.name, email=test_email)

    def test_send_campaign(self):
        frappe.set_user(self.core_team_email)

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
        # First call creates it
        group1 = create_email_group(
            type="Event Participants",
            reference_document=self.event.name,
            document_type=self.event.doctype,
        )

        # Second call should not create a new one
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
        email = "added@example.com"
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
        email = "remove@example.com"
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
            add_to_email_group("non-existent-group", "test@example.com")
