import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_VOLUNTEER,
)
from fossunited.tests.utils import insert_test_chapter, insert_test_event


class TestFOSSChapterEvent(FrappeTestCase):
    def setUp(self):
        self.core_team_email = "test1@example.com"
        self.chapter = insert_test_chapter(members=[self.core_team_email])
        self.event = insert_test_event(
            chapter=self.chapter,
        )

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_members_are_added_to_event(self):
        # Given a chapter
        chapter = self.chapter

        # When an event is created for the chapter
        event = self.event

        # Then the existing members of the chapter should be added to the event
        for member in chapter.chapter_members:
            self.assertTrue(
                frappe.db.exists(
                    EVENT_VOLUNTEER,
                    {
                        "parent": event.name,
                        "member": member.chapter_member,
                    },
                )
            )

    def test_unique_event_slug(self):
        """Test that event slugs must be unique within a chapter
        but can be reused across chapters."""

        original_chapter = self.chapter
        original_event = self.event
        existing_permalink = original_event.event_permalink

        # Test 1: Same chapter, same slug (should fail)
        with self.assertRaises(frappe.exceptions.ValidationError):
            insert_test_event(chapter=original_chapter, event_permalink=existing_permalink)

        # Test 2: Different chapter, same slug (should succeed)
        new_chapter = insert_test_chapter(city="Kochi", state="Kerala")

        insert_test_event(
            chapter=new_chapter,
            event_permalink=existing_permalink,
        )

        # Test 3: Same chapter, different slug (should succeed)
        insert_test_event(chapter=original_chapter)

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
        """Test that a new event with map_link extracts and stores coordinates."""
        map_coord = "12.9716,77.5946"
        map_link = "https://maps.google.com/?q=12.9716,77.5946"

        event = insert_test_event(
            chapter=self.chapter,
            map_link=map_link,
        )
        self.assertIsNotNone(event.map_coordinate)
        self.assertEqual(event.map_coordinate, map_coord)

        frappe.delete_doc(EVENT, event.name, force=True)

    def test_map_link_updates_coordinates(self):
        """Test that changing map_link triggers coordinate re-extraction."""
        event = insert_test_event(
            chapter=self.chapter,
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
        """Test that events created without map_link have no coordinates."""
        event = insert_test_event(chapter=self.chapter)
        self.assertIsNone(event.map_coordinate)
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_invalid_map_link_sets_none(self):
        """Test that invalid map links result in None coordinates."""
        event = insert_test_event(
            chapter=self.chapter,
            map_link="https://invalid-url.com",
        )

        self.assertIsNone(event.map_coordinate)
        frappe.delete_doc(EVENT, event.name, force=True)
