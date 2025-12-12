import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, nowdate

from fossunited.doctype_ids import CHAPTER, EVENT, USER_PROFILE
from fossunited.fossunited.utils import (
    get_volunteers_data,
    get_volunteers_stats,
)
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_event,
    insert_user_profile,
)


class TestVolunteersPage(FrappeTestCase):
    """Test cases for volunteers page data functions."""

    def setUp(self):
        frappe.db.delete("FOSS Chapter Lead Team Member", {"email": "test1@example.com"})
        frappe.db.delete("FOSS Chapter Lead Team Member", {"email": "core1@example.com"})

        self.member1_email = "luffy@example.com"
        self.member2_email = "zoro@example.com"
        self.member3_email = "xebec@example.com"

        # Create test user profiles using existing helper
        self.profile1_name = insert_user_profile(
            self.member1_email, first_name="Monkey", last_name="Luffy"
        )
        self.profile2_name = insert_user_profile(self.member2_email, full_name="Zoro")
        self.profile3_name = insert_user_profile(self.member3_email, full_name="Xebec")

        self.profile1 = frappe.get_doc(USER_PROFILE, self.profile1_name)
        self.profile1.current_city = "Bangalore"
        self.profile1.show_activity = 1
        self.profile1.save()

        self.profile2 = frappe.get_doc(USER_PROFILE, self.profile2_name)
        self.profile2.route = "u/zoro"
        self.profile2.current_city = "Mumbai"
        self.profile2.show_activity = 0
        self.profile2.save()

        self.profile3 = frappe.get_doc(USER_PROFILE, self.profile3_name)
        self.profile3.route = "u/xebec"
        self.profile3.current_city = "Delhi"
        self.profile3.show_activity = 1
        self.profile3.save()

        self.chapter1 = insert_test_chapter(
            city="Bangalore",
            state="Karnataka",
            members=[self.member1_email, self.member2_email],
        )
        self.chapter2 = insert_test_chapter(
            city="Mumbai",
            state="Maharashtra",
            members=[self.member1_email, self.member3_email],  # luffy in both chapters
        )

        self._events = []

    def tearDown(self):
        frappe.set_user("Administrator")
        for event in self._events:
            frappe.delete_doc(EVENT, event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter1.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter2.name, force=True)
        frappe.delete_doc(USER_PROFILE, self.profile1.name, force=True)
        frappe.delete_doc(USER_PROFILE, self.profile2.name, force=True)
        frappe.delete_doc(USER_PROFILE, self.profile3.name, force=True)
        # Delete associated Frappe Users
        for email in [self.member1_email, self.member2_email, self.member3_email]:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True)

    def test_get_volunteers_data_returns_correct_structure(self):
        """Test that volunteers data returns expected fields and structure."""
        # Create a recent event
        event = insert_test_event(chapter=self.chapter1)
        self._events.append(event)

        result = get_volunteers_data()

        # Should have volunteers from both chapters
        self.assertEqual(len(result), 4)

        # Check structure of first result
        first = result[0]
        expected_fields = {
            "chapter_member",
            "route",
            "full_name",
            "profile_photo",
            "show_activity",
            "current_city",
            "chapter_name",
            "chapter_logo",
            "chapter_route",
            "latest_event",
        }
        self.assertEqual(set(first.keys()), expected_fields)

        # Verify data types
        self.assertIsInstance(first["route"], str)
        self.assertIsInstance(first["full_name"], str)
        self.assertIsInstance(first["show_activity"], int)
        self.assertIsInstance(first["chapter_name"], str)
        self.assertIsInstance(first["chapter_route"], str)

        # latest_event should be ISO string or None
        if first["latest_event"]:
            self.assertIsInstance(first["latest_event"], str)
            self.assertIn("T", first["latest_event"])  # ISO format check

    def test_get_volunteers_data_includes_all_members(self):
        """Test that all chapter members are included in results."""
        # Create events for both chapters
        event1 = insert_test_event(chapter=self.chapter1)
        event2 = insert_test_event(chapter=self.chapter2)
        self._events.extend([event1, event2])

        result = get_volunteers_data()

        # Get all unique member profile names from results
        member_profiles = {row["chapter_member"] for row in result}

        # Should include all three members (by their profile names)
        self.assertIn(self.profile1.name, member_profiles)
        self.assertIn(self.profile2.name, member_profiles)
        self.assertIn(self.profile3.name, member_profiles)

    def test_get_volunteers_data_member_in_multiple_chapters(self):
        """Test that a member in multiple chapters appears multiple times."""
        # Create events for both chapters
        event1 = insert_test_event(chapter=self.chapter1)
        event2 = insert_test_event(chapter=self.chapter2)
        self._events.extend([event1, event2])

        result = get_volunteers_data()

        # luffy (profile1) is in both chapters
        luffy_entries = [r for r in result if r["chapter_member"] == self.profile1.name]

        # Should have 2 entries (one per chapter)
        self.assertEqual(len(luffy_entries), 2)

        # Should have different chapter names
        chapter_names = {entry["chapter_name"] for entry in luffy_entries}
        self.assertEqual(len(chapter_names), 2)

    def test_get_volunteers_data_respects_profile_fields(self):
        """Test that profile fields are correctly populated."""
        event = insert_test_event(chapter=self.chapter1)
        self._events.append(event)

        result = get_volunteers_data()

        # Find luffy's entry
        luffy_entry = next((r for r in result if r["chapter_member"] == self.profile1.name), None)
        self.assertIsNotNone(luffy_entry)

        # Verify profile data
        self.assertEqual(luffy_entry["full_name"], "Monkey Luffy")
        self.assertEqual(luffy_entry["route"], "u/monkey_luffy")
        self.assertEqual(luffy_entry["current_city"], "Bangalore")
        self.assertEqual(luffy_entry["show_activity"], 1)

        # Find Zoro (is he lost again?)
        zoro_entry = next((r for r in result if r["chapter_member"] == self.profile2.name), None)
        self.assertIsNotNone(zoro_entry)
        self.assertEqual(zoro_entry["show_activity"], 0)

    def test_get_volunteers_stats_counts_unique_volunteers(self):
        """Test that stats count unique volunteers even if in multiple chapters."""
        # Create recent events (within last year)
        event1 = insert_test_event(chapter=self.chapter1)
        event2 = insert_test_event(chapter=self.chapter2)
        self._events.extend([event1, event2])

        result = get_volunteers_stats()
        # Should count unique volunteers (Luffy in 2 chapters = 1 unique)
        # Total unique: Luffy, Zoro, Xebec = 3
        self.assertEqual(result["active_count"], 3)

        # Should count both chapters
        self.assertEqual(result["communities_count"], 2)

    def test_get_volunteers_stats_excludes_inactive_chapters(self):
        """Test that stats only include chapters with events in last year."""
        # Create old event (more than 1 year ago) for chapter1
        old_date = add_to_date(nowdate(), years=-2)
        old_event = insert_test_event(
            chapter=self.chapter1,
            event_start_date=old_date,
        )

        # Create recent event for chapter2
        recent_event = insert_test_event(chapter=self.chapter2)
        self._events.extend([old_event, recent_event])

        result = get_volunteers_stats()

        # Should only count chapter2 (with recent event)
        self.assertEqual(result["communities_count"], 1)

        # Should only count volunteers from chapter2 (Luffy and Xebec)
        self.assertEqual(result["active_count"], 2)

    def test_get_volunteers_data_includes_latest_event_timestamp(self):
        """Test that latest_event shows the most recent event date."""
        # Create multiple events for chapter1
        old_event = insert_test_event(
            chapter=self.chapter1,
            event_start_date=add_to_date(nowdate(), days=-30),
        )
        recent_event = insert_test_event(
            chapter=self.chapter1,
            event_start_date=add_to_date(nowdate(), days=-5),
        )
        self._events.extend([old_event, recent_event])

        result = get_volunteers_data()

        chapter1_entries = [r for r in result if r["chapter_name"] == self.chapter1.chapter_name]

        # All should have the same latest_event (the most recent one)
        latest_dates = {entry["latest_event"] for entry in chapter1_entries}
        self.assertEqual(len(latest_dates), 1)

        # Verify it's the recent event's date (ISO format comparison)
        latest_date = list(latest_dates)[0]
        self.assertIn(recent_event.event_start_date.strftime("%Y-%m-%d"), latest_date)
