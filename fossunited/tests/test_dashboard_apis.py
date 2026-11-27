"""
bench --site break.site run-tests --module fossunited.tests.test_dashboard_apis
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.chapter import get_my_chapter_dashboard
from fossunited.api.dashboard import get_event
from fossunited.doctype_ids import EVENT, EVENT_TICKET
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventTicketFactory,
    UserFactory,
    get_foss_profile_id,
)


class TestGetEvent(FrappeTestCase):
    """fossunited.api.dashboard.get_event"""

    def setUp(self):
        frappe.set_user("Administrator")
        self.member = UserFactory.create("with_foss_website_user_role")
        self.chapter = FOSSChapterFactory.create("with_members", members=[self.member.name])
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)  # status: Live
        self.draft_event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name, status="Draft"
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(EVENT, self.draft_event.name, force=True)
        frappe.delete_doc("FOSS Chapter", self.chapter.name, force=True)

    def test_draft_event_blocked_for_outsider(self):
        outsider = UserFactory.create("with_foss_website_user_role")
        frappe.set_user(outsider.name)
        with self.assertRaises(frappe.DoesNotExistError):
            get_event(self.draft_event.name)

    def test_draft_event_visible_to_chapter_member(self):
        frappe.set_user(self.member.name)
        data = get_event(self.draft_event.name)
        self.assertEqual(data["name"], self.draft_event.name)

    def test_draft_event_visible_to_system_manager(self):
        manager = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", manager.name).add_roles("System Manager")
        try:
            frappe.set_user(manager.name)
            data = get_event(self.draft_event.name)
            self.assertEqual(data["name"], self.draft_event.name)
        finally:
            frappe.set_user("Administrator")
            frappe.get_doc("User", manager.name).remove_roles("System Manager")

    def test_published_event_strips_internal_fields(self):
        frappe.set_user("Guest")
        data = get_event(self.event.name)
        for field in (
            "event_data",
            "_comments",
            "_assign",
            "_liked_by",
            "event_members",
            "owner",
            "modified_by",
        ):
            self.assertNotIn(field, data)

    def test_child_table_rows_strip_internal_fields(self):
        frappe.set_user("Administrator")
        event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            tiers=[{"enabled": 1, "title": "General", "price": 0, "maximum_tickets": 0}],
        )

        frappe.set_user("Guest")
        data = get_event(event.name)
        tier_row = data["tiers"][0]
        for field in ("_comments", "_assign", "_liked_by", "owner", "modified_by"):
            self.assertNotIn(field, tier_row)

        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_lookup_by_route(self):
        frappe.set_user("Guest")
        # Pass the stored route back verbatim: whatever prefix convention it
        # already has, this is a self-match regardless of "c/" handling.
        data = get_event(self.event.route, by_route=True)
        self.assertEqual(data.get("name"), self.event.name)

    def test_lookup_by_route_missing_returns_empty(self):
        frappe.set_user("Guest")
        self.assertEqual(get_event("does-not-exist", by_route=True), {})

    def test_tier_sold_count(self):
        frappe.set_user("Administrator")
        paid_event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)
        FOSSEventTicketFactory.create_list(3, event=paid_event.name, tier="General")

        frappe.set_user("Guest")
        data = get_event(paid_event.name)
        tiers = {t["title"]: t for t in data["tiers"]}
        self.assertEqual(tiers["General"]["sold_count"], 3)

        frappe.set_user("Administrator")
        frappe.db.delete(EVENT_TICKET, {"event": paid_event.name})
        frappe.delete_doc(EVENT, paid_event.name, force=True)

    def test_tier_sold_count_matches_case_insensitively(self):
        """A tier renamed to a different case ("general" -> "General") must still count
        tickets sold under the old-case title; DB collation treats them as equal."""
        frappe.set_user("Administrator")
        paid_event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)
        FOSSEventTicketFactory.create_list(2, event=paid_event.name, tier="general")

        frappe.set_user("Guest")
        data = get_event(paid_event.name)
        tiers = {t["title"]: t for t in data["tiers"]}
        self.assertEqual(tiers["General"]["sold_count"], 2)

        frappe.set_user("Administrator")
        frappe.db.delete(EVENT_TICKET, {"event": paid_event.name})
        frappe.delete_doc(EVENT, paid_event.name, force=True)

    def test_uncapped_tier_has_no_sold_count(self):
        frappe.set_user("Administrator")
        event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            tiers=[{"enabled": 1, "title": "Free", "price": 0, "maximum_tickets": 0}],
        )

        frappe.set_user("Guest")
        data = get_event(event.name)
        self.assertNotIn("sold_count", data["tiers"][0])

        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, event.name, force=True)


class TestGetMyChapterDashboard(FrappeTestCase):
    """fossunited.api.chapter.get_my_chapter_dashboard"""

    def setUp(self):
        frappe.set_user("Administrator")
        self.user = UserFactory.create("with_foss_website_user_role")
        self.profile = get_foss_profile_id(self.user.name)
        self.chapter = FOSSChapterFactory.create("with_members", members=[self.user.name])
        self.other_chapter = FOSSChapterFactory.create()  # user NOT a member

        self.own_event = FOSSChapterEventFactory.create(
            "with_ongoing_dates", chapter=self.chapter.name
        )
        self.other_event = FOSSChapterEventFactory.create(
            "with_ongoing_dates", chapter=self.other_chapter.name
        )
        self.created = []

    def tearDown(self):
        frappe.set_user("Administrator")
        for doctype, name in reversed(self.created):
            frappe.delete_doc(doctype, name, force=True)
        frappe.delete_doc(EVENT, self.own_event.name, force=True)
        frappe.delete_doc(EVENT, self.other_event.name, force=True)
        frappe.delete_doc("FOSS Chapter", self.chapter.name, force=True)
        frappe.delete_doc("FOSS Chapter", self.other_chapter.name, force=True)

    def test_only_shows_own_chapter_and_its_events(self):
        frappe.set_user(self.user.name)
        result = get_my_chapter_dashboard()

        self.assertIn(self.chapter.name, {c.name for c in result["chapters"]})
        self.assertNotIn(self.other_chapter.name, {c.name for c in result["chapters"]})

        scheduled_names = {e.name for e in result["scheduled"]}
        self.assertIn(self.own_event.name, scheduled_names)
        self.assertNotIn(self.other_event.name, scheduled_names)

    def test_includes_volunteer_only_event_outside_own_chapter(self):
        event_doc = frappe.get_doc(EVENT, self.other_event.name)
        event_doc.append("event_members", {"member": self.profile, "role": "Volunteer"})
        event_doc.save()

        frappe.set_user(self.user.name)
        result = get_my_chapter_dashboard()
        scheduled_names = {e.name for e in result["scheduled"]}
        self.assertIn(self.other_event.name, scheduled_names)

    def test_empty_for_user_with_no_chapters_or_events(self):
        outsider = UserFactory.create("with_foss_website_user_role")
        frappe.set_user(outsider.name)
        result = get_my_chapter_dashboard()

        self.assertEqual(result["chapters"], [])
        self.assertEqual(result["scheduled"], [])
        self.assertEqual(result["recent_concluded"], [])
