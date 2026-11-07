from collections import Counter
from datetime import datetime, timedelta
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.chapter import get_my_chapter_dashboard, get_my_chapters
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_VOLUNTEER
from fossunited.tests.factories import FOSSChapterFactory, UserFactory, get_foss_profile_id
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory

NOW = datetime(2035, 6, 15, 12, 0, 0)


class TestChapterDashboard(FrappeTestCase):
    def setUp(self):
        self.user = UserFactory.create("with_foss_website_user_role")
        self.chapters = []
        self.events = []

    def tearDown(self):
        frappe.set_user("Administrator")
        for event in reversed(self.events):
            frappe.delete_doc(EVENT, event.name, force=True)
        for chapter in reversed(self.chapters):
            frappe.delete_doc(CHAPTER, chapter.name, force=True)

    def chapter(self, member=True):
        chapter = (
            FOSSChapterFactory.create("with_members", members=[self.user.name])
            if member
            else FOSSChapterFactory.create()
        )
        self.chapters.append(chapter)
        return chapter

    def event(self, chapter, status="Live", end=None, start=None, volunteer=False):
        event = FOSSChapterEventFactory.create(
            "with_chapter",
            chapter=chapter.name,
            event_start_date=start or NOW - timedelta(days=1),
            event_end_date=end or NOW + timedelta(days=1),
        )
        # before_insert copies chapter members into event volunteers. Remove those
        # inherited rows so each test explicitly controls membership vs volunteering.
        frappe.db.delete(EVENT_VOLUNTEER, {"parent": event.name, "parenttype": EVENT})
        # Write fixture status without Document lifecycle hooks so the test controls
        # all status/date combinations independently of the real clock.
        frappe.db.set_value(EVENT, event.name, "status", status, update_modified=False)
        if volunteer:
            frappe.get_doc(
                {
                    "doctype": EVENT_VOLUNTEER,
                    "parent": event.name,
                    "parenttype": EVENT,
                    "parentfield": "event_members",
                    "member": get_foss_profile_id(self.user.name),
                    "email": self.user.name,
                    "role": "Volunteer",
                }
            ).db_insert()
        self.events.append(event)
        return event

    def legacy(self):
        chapter_names = get_my_chapters(self.user.name)
        chapters = (
            frappe.get_all(CHAPTER, filters={"name": ["in", chapter_names]}, fields=["*"])
            if chapter_names
            else []
        )
        scheduled, recent = [], []
        for chapter in chapters:
            doc = frappe.get_doc(CHAPTER, chapter.name)
            scheduled.extend(doc.get_upcoming_events())
            recent.extend(
                e
                for e in doc.get_past_events()
                if e.event_end_date and e.event_end_date >= NOW - timedelta(days=21)
            )
        names = {e.name for e in scheduled + recent}
        volunteer_names = frappe.get_all(
            EVENT_VOLUNTEER,
            filters={"email": self.user.name, "parenttype": EVENT},
            pluck="parent",
        )
        only_volunteer = [name for name in volunteer_names if name not in names]
        if only_volunteer:
            scheduled.extend(
                frappe.get_all(
                    EVENT,
                    filters={"name": ["in", only_volunteer], "status": ["in", ["Live", "Draft"]]},
                    fields=["*"],
                )
            )
            recent.extend(
                frappe.get_all(
                    EVENT,
                    filters={
                        "name": ["in", only_volunteer],
                        "status": ["not in", ["Live", "Draft"]],
                        "event_end_date": [">=", NOW - timedelta(days=21)],
                    },
                    fields=["*"],
                )
            )
        return {"chapters": chapters, "scheduled": scheduled, "recent_concluded": recent}

    def dashboard(self):
        with (
            self.set_user(self.user.name),
            patch("fossunited.api.chapter.now_datetime", return_value=NOW),
            patch("frappe.utils.now", return_value=NOW.strftime("%Y-%m-%d %H:%M:%S")),
        ):
            return get_my_chapter_dashboard()

    def assert_parity(self):
        with (
            self.set_user(self.user.name),
            patch("fossunited.api.chapter.now_datetime", return_value=NOW),
            patch("frappe.utils.now", return_value=NOW.strftime("%Y-%m-%d %H:%M:%S")),
        ):
            expected = self.legacy()
            result = get_my_chapter_dashboard()
        self.assertEqual(result, expected)
        return result

    def test_empty_memberships(self):
        self.assertEqual(
            self.assert_parity(), {"chapters": [], "scheduled": [], "recent_concluded": []}
        )

    def test_multichapter_status_boundaries_and_order(self):
        for _ in range(2):
            chapter = self.chapter()
            for status in ("Live", "Draft", "Concluded", "Cancelled"):
                for offset in (-22, -21, -1, 0, 1):
                    self.event(
                        chapter,
                        status=status,
                        end=NOW + timedelta(days=offset),
                        start=NOW + timedelta(hours=offset),
                    )
        result = self.assert_parity()
        self.assertEqual(len(result["scheduled"]), 4)
        self.assertEqual(len(result["recent_concluded"]), 4)

    def test_unrelated_chapter_events_not_exposed(self):
        chapter = self.chapter(member=False)
        self.event(chapter)
        self.event(chapter, status="Concluded", end=NOW - timedelta(days=1))
        result = self.assert_parity()
        self.assertFalse(result["chapters"])
        self.assertFalse(result["scheduled"])
        self.assertFalse(result["recent_concluded"])

    def test_no_chapter_document_hydration(self):
        chapter = self.chapter()
        self.event(chapter)
        with patch("frappe.get_doc", wraps=frappe.get_doc) as get_doc:
            self.dashboard()
        chapter_loads = [
            call for call in get_doc.call_args_list if call.args and call.args[0] == CHAPTER
        ]
        self.assertEqual(chapter_loads, [])

    def test_event_query_count_does_not_grow_with_chapters(self):
        def measure():
            with patch.object(frappe.db, "sql", wraps=frappe.db.sql) as sql:
                self.dashboard()
            statements = [str(call.args[0]) for call in sql.call_args_list if call.args]
            return Counter(
                "event"
                for query in statements
                if "tabFOSS Chapter Event`" in query
                and query.lstrip().lower().startswith("select")
            )

        first = self.chapter()
        self.event(first)
        one = measure()
        for _ in range(3):
            self.event(self.chapter())
        four = measure()
        self.assertEqual(one["event"], 2)
        self.assertEqual(four["event"], 2)

    def test_volunteer_only_status_date_semantics(self):
        chapter = self.chapter(member=False)
        for status in ("Live", "Draft", "Concluded", "Cancelled"):
            for offset in (-22, -21, -1, 0, 1):
                self.event(
                    chapter, status=status, end=NOW + timedelta(days=offset), volunteer=True
                )
        result = self.assert_parity()
        self.assertFalse(result["chapters"])
        self.assertEqual(len(result["scheduled"]), 10)
        self.assertEqual(len(result["recent_concluded"]), 8)

    def test_member_volunteer_overlap_deduplicated(self):
        chapter = self.chapter()
        self.event(chapter, volunteer=True)
        self.event(chapter, status="Concluded", end=NOW - timedelta(days=1), volunteer=True)
        # Draft is excluded from chapter-only queries but retained by volunteer path.
        self.event(chapter, status="Draft", volunteer=True)
        result = self.assert_parity()
        self.assertEqual(len(result["scheduled"]), 2)
        self.assertEqual(len(result["recent_concluded"]), 1)
        names = [e.name for e in result["scheduled"] + result["recent_concluded"]]
        self.assertEqual(len(names), len(set(names)))

    def test_null_dates_and_empty_chapter_are_preserved(self):
        self.chapter()
        chapter = self.chapter()
        undated = self.event(chapter, status="Concluded")
        frappe.db.set_value(EVENT, undated.name, "event_end_date", None, update_modified=False)
        result = self.assert_parity()
        self.assertEqual(len(result["chapters"]), 2)
        self.assertFalse(result["scheduled"])
        self.assertFalse(result["recent_concluded"])

    def test_duplicate_membership_does_not_duplicate_events(self):
        chapter = self.chapter()
        self.event(chapter)
        member = chapter.chapter_members[0]
        copy = frappe.copy_doc(member)
        copy.parent = chapter.name
        copy.parenttype = CHAPTER
        copy.parentfield = "chapter_members"
        copy.db_insert()
        result = self.assert_parity()
        self.assertEqual(len(result["chapters"]), 1)
        self.assertEqual(len(result["scheduled"]), 1)

    def test_expired_history_not_loaded_before_recent_filter(self):
        chapter = self.chapter()
        ancient = self.event(chapter, status="Concluded", end=NOW - timedelta(days=90))
        recent = self.event(chapter, status="Concluded", end=NOW - timedelta(days=1))
        fetched_events = []
        original_get_all = frappe.get_all

        def record_get_all(doctype, *args, **kwargs):
            rows = original_get_all(doctype, *args, **kwargs)
            if doctype == EVENT:
                fetched_events.extend(row.name for row in rows)
            return rows

        with patch("frappe.get_all", side_effect=record_get_all):
            result = self.dashboard()
        self.assertEqual([event.name for event in result["recent_concluded"]], [recent.name])
        self.assertNotIn(ancient.name, fetched_events)
        self.assertIn(recent.name, fetched_events)
