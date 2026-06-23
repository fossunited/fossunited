from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CAMPAIGN,
    CHAPTER,
    EMAIL_GROUP,
    EMAIL_MEMBER,
    EVENT,
    EVENT_VOLUNTEER,
)
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
)
from fossunited.utils.notifications import send_event_feedback_request

ENQUEUE_PATH = "fossunited.chapters.doctype.foss_chapter_event.foss_chapter_event.frappe.enqueue"
NEWSLETTER_SEND_PATH = "newsletter.newsletter.doctype.newsletter.newsletter.Newsletter.send_emails"


class TestFOSSChapterEvent(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create("with_members")
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)

    def tearDown(self):
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def test_members_are_added_to_event(self):
        for member in self.chapter.chapter_members:
            self.assertTrue(
                frappe.db.exists(
                    EVENT_VOLUNTEER,
                    {
                        "parent": self.event.name,
                        "member": member.chapter_member,
                    },
                )
            )

    def test_unique_event_slug(self):
        """Slugs must be unique within a chapter but reusable across chapters."""
        existing_permalink = self.event.event_permalink

        # Same chapter, same slug → should fail
        with self.assertRaises(frappe.exceptions.ValidationError):
            FOSSChapterEventFactory.create(
                chapter=self.chapter.name, event_permalink=existing_permalink
            )

        # Different chapter, same slug → should succeed
        other_chapter = FOSSChapterFactory.create()
        try:
            FOSSChapterEventFactory.create(
                chapter=other_chapter.name, event_permalink=existing_permalink
            )
            # Same chapter, different slug → should succeed
            FOSSChapterEventFactory.create(chapter=self.chapter.name)
        finally:
            frappe.delete_doc(CHAPTER, other_chapter.name, force=True)

    def test_email_groups_are_created_on_event_insert(self):
        expected_group_types = [
            "Event Participants",
            "CFP Proposers",
            "Accepted Proposers",
            "Rejected Proposers",
        ]

        for group_type in expected_group_types:
            self.assertTrue(
                frappe.db.exists(
                    "Email Group",
                    {
                        "group_type": group_type,
                        "reference_document": self.event.name,
                        "document_type": EVENT,
                    },
                ),
                msg=f"Email Group '{group_type}' not created for event {self.event.name}",
            )

        frappe.db.delete(
            "Email Group",
            {
                "reference_document": self.event.name,
                "document_type": EVENT,
            },
        )

    def test_map_link_extracts_coordinates(self):
        map_link = "https://maps.google.com/?q=12.9716,77.5946"
        event = FOSSChapterEventFactory.create(
            "with_map_link", chapter=self.chapter.name, map_link=map_link
        )

        self.assertIsNotNone(event.map_coordinate)
        self.assertEqual(event.map_coordinate, "12.9716,77.5946")
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_map_link_updates_coordinates(self):
        event = FOSSChapterEventFactory.create(
            "with_map_link",
            chapter=self.chapter.name,
            map_link="https://osmapp.org/node/abcdedfg/#69/12.9716/77.5946",
        )
        initial_coordinate = event.map_coordinate

        event = frappe.get_doc(EVENT, event.name)
        event.map_link = "https://maps.google.com/?q=69.007,420.911"
        event.save()

        self.assertEqual(initial_coordinate, "12.9716,77.5946")
        self.assertEqual(event.map_coordinate, "69.007,420.911")
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_event_without_map_link_has_no_coordinates(self):
        event = FOSSChapterEventFactory.create(chapter=self.chapter.name)
        self.assertIsNone(event.map_coordinate)
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_invalid_map_link_sets_none(self):
        event = FOSSChapterEventFactory.create(
            "with_map_link", chapter=self.chapter.name, map_link="https://invalid-url.com"
        )
        self.assertIsNone(event.map_coordinate)
        frappe.delete_doc(EVENT, event.name, force=True)


class TestFeedbackEmail(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_past_dates", chapter=self.chapter.name)

    def tearDown(self):
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def _add_to_email_group(self, group_type, email):
        group = frappe.db.get_value(
            EMAIL_GROUP,
            {"reference_document": self.event.name, "group_type": group_type},
            "name",
        )
        frappe.get_doc({"doctype": EMAIL_MEMBER, "email_group": group, "email": email}).insert(
            ignore_permissions=True
        )

    @patch(ENQUEUE_PATH)
    def test_concluding_past_event_enqueues_feedback(self, mock_enqueue):
        event = frappe.get_doc(EVENT, self.event.name)
        event.status = "Concluded"
        event.save()

        mock_enqueue.assert_called_once_with(
            "fossunited.utils.notifications.send_event_feedback_request",
            event_id=self.event.name,
            queue="long",
            enqueue_after_commit=True,
        )

    @patch(ENQUEUE_PATH)
    def test_conclude_events_scheduler_enqueues_feedback(self, mock_enqueue):
        from fossunited.scheduled_tasks import conclude_events

        conclude_events()

        matching = [
            c for c in mock_enqueue.call_args_list if c.kwargs.get("event_id") == self.event.name
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(
            matching[0].args[0],
            "fossunited.utils.notifications.send_event_feedback_request",
        )

    @patch(ENQUEUE_PATH)
    def test_no_enqueue_if_feedback_already_sent(self, mock_enqueue):
        frappe.db.set_value(EVENT, self.event.name, "feedback_sent", 1)
        event = frappe.get_doc(EVENT, self.event.name)
        event.status = "Concluded"
        event.save()

        mock_enqueue.assert_not_called()

    @patch(NEWSLETTER_SEND_PATH)
    def test_creates_campaign_when_participants_exist(self, mock_send):
        self._add_to_email_group("Event Participants", "participant@test.com")

        send_event_feedback_request(self.event.name)

        mock_send.assert_called_once()
        self.assertTrue(frappe.db.exists(CAMPAIGN, {"reference_document": self.event.name}))

    @patch(NEWSLETTER_SEND_PATH)
    def test_feedback_sent_flag_set_after_send(self, mock_send):
        self._add_to_email_group("Event Participants", "flag@test.com")

        send_event_feedback_request(self.event.name)

        self.assertEqual(frappe.db.get_value(EVENT, self.event.name, "feedback_sent"), 1)

    @patch(NEWSLETTER_SEND_PATH)
    def test_no_send_if_no_participants(self, mock_send):
        # Email groups exist but empty → total_subscribers = 0 → bail early
        send_event_feedback_request(self.event.name)

        mock_send.assert_not_called()
        self.assertFalse(frappe.db.exists(CAMPAIGN, {"reference_document": self.event.name}))
