import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.stats import get_event_stats, get_user_stats, get_platform_stats
from fossunited.doctype_ids import USER_PROFILE


class TestFossUserProfile(FrappeTestCase):
    def test_get_event_stats(self):
        """Test event statistics API"""
        stats = get_event_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_events", stats)
        self.assertIn("published_events", stats)
        self.assertIn("upcoming_events", stats)
        self.assertIn("past_events", stats)

    def test_get_user_stats(self):
        """Test user statistics API"""
        stats = get_user_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_users", stats)
        self.assertIn("active_users", stats)

    def test_get_platform_stats(self):
        """Test platform statistics API"""
        stats = get_platform_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("events", stats)
        self.assertIn("users", stats)
        self.assertIn("last_updated", stats)