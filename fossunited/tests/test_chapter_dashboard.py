from datetime import timedelta

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

from fossunited.api.chapter import get_my_chapter_dashboard
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_VOLUNTEER
from fossunited.tests.factories import FOSSChapterFactory, UserFactory, get_foss_profile_id
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory


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
            event_start_date=start or now_datetime() - timedelta(days=1),
            event_end_date=end or now_datetime() + timedelta(days=1),
        )
        # before_insert copies chapter members into event volunteers. Remove those
        # inherited rows so each test explicitly controls membership vs volunteering.
        frappe.db.delete(EVENT_VOLUNTEER, {"parent": event.name, "parenttype": EVENT})
        # Set fixture status without event lifecycle transitions.
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

    def test_member_chapter_events(self):
        chapter = self.chapter()
        live = self.event(chapter)
        recent = self.event(chapter, status="Concluded", end=now_datetime() - timedelta(days=1))
        self.event(chapter, status="Draft")
        self.event(chapter, status="Cancelled")
        self.event(chapter, status="Concluded", end=now_datetime() - timedelta(days=22))
        self.event(self.chapter(member=False))
        with self.set_user(self.user.name):
            result = get_my_chapter_dashboard()
        self.assertEqual({event.name for event in result["scheduled"]}, {live.name})
        self.assertEqual({event.name for event in result["recent_concluded"]}, {recent.name})

    def test_volunteer_events(self):
        draft = self.event(self.chapter(member=False), status="Draft", volunteer=True)
        overlap = self.event(self.chapter(), volunteer=True)
        with self.set_user(self.user.name):
            result = get_my_chapter_dashboard()
        self.assertCountEqual(
            [event.name for event in result["scheduled"]], [draft.name, overlap.name]
        )
        self.assertEqual(result["recent_concluded"], [])
