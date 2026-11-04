"""Cached chapter/event roster identity is scrubbed on account anonymization."""

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CHAPTER_MEMBER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_VOLUNTEER,
    USER_PROFILE,
)
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.user_factory import UserFactory, get_foss_profile_id


class TestAccountDeletionChapterRosters(FrappeTestCase):
    def setUp(self):
        self.addCleanup(frappe.db.rollback)
        self.target = UserFactory.create(first_name="Jane", last_name="Doe")
        self.target_profile = get_foss_profile_id(self.target.name)
        frappe.db.set_value(USER_PROFILE, self.target_profile, "full_name", "Jane Doe")
        self.other = UserFactory.create(first_name="Other", last_name="Person")
        self.other_profile = get_foss_profile_id(self.other.name)
        frappe.db.set_value(USER_PROFILE, self.other_profile, "full_name", "Other Person")

        self.chapter = FOSSChapterFactory.create(
            "with_members",
            chapter_name="Roster Test City",
            slug="roster_test_city",
            chapter_type=CITY_COMMUNITY,
            chapter_status="Active",
            is_published=1,
            city="Bangalore",
            state="Karnataka",
            members=[self.target.name, self.other.name],
        )

        event = FOSSChapterEventFactory.create(
            "with_chapter",
            chapter=self.chapter.name,
            is_published=1,
            event_name="Roster Test Event",
        )
        ev = frappe.get_doc(EVENT, event.name)
        ev.event_members = []  # replace any auto-copied rows with a known set
        for profile in (self.target_profile, self.other_profile):
            ev.append("event_members", {"member": profile, "role": "Volunteer"})
        ev.save(ignore_permissions=True)

    def _row(self, doctype, link_field, profile):
        return frappe.db.get_value(
            doctype, {link_field: profile}, ["name", "full_name", "email"], as_dict=True
        )

    def _run_deletion(self):
        req = frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.target.name}
        ).insert(ignore_permissions=True)
        req.status = "Pending Approval"
        req.save(ignore_permissions=True)
        req.trigger_data_deletion()
        req.reload()
        return req

    def test_cached_roster_identity_is_scrubbed(self):
        chap = self._row(CHAPTER_MEMBER, "chapter_member", self.target_profile)
        evm = self._row(EVENT_VOLUNTEER, "member", self.target_profile)
        self.assertEqual(chap.full_name, "Jane Doe")
        self.assertEqual(evm.full_name, "Jane Doe")

        self._run_deletion()

        anon = frappe.db.get_value(
            USER_PROFILE, self.target_profile, ["full_name", "email"], as_dict=True
        )
        self.assertNotEqual(anon.full_name, "Jane Doe")  # the profile itself was redacted
        # cached roster copies now mirror the anonymized profile, not the real identity
        for doctype, name in ((CHAPTER_MEMBER, chap.name), (EVENT_VOLUNTEER, evm.name)):
            row = frappe.db.get_value(doctype, name, ["full_name", "email"], as_dict=True)
            self.assertEqual(row.full_name, anon.full_name)
            self.assertEqual(row.email, anon.email)

        # control: a different member is untouched
        other = self._row(CHAPTER_MEMBER, "chapter_member", self.other_profile)
        self.assertEqual(other.full_name, "Other Person")
