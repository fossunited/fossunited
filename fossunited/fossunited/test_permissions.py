import frappe
import frappe.client
import frappe.share
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_CFP,
    EVENT_RSVP,
    TICKET_TIER,
)
from fossunited.fossunited.permissions import cfp_submission_query, rsvp_submission_query
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
    FOSSEventRSVPFactory,
    UserFactory,
    get_foss_profile_id,
)


class TestPermissionQueries(FrappeTestCase):
    """Unit tests for cfp_submission_query and rsvp_submission_query SQL fragments."""

    def setUp(self):
        frappe.set_user("Administrator")
        self.ctm = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", self.ctm.name).add_roles("Chapter Team Member")
        self.chapter = FOSSChapterFactory.create("with_members", members=[self.ctm.name])
        self.other_chapter = FOSSChapterFactory.create()  # ctm NOT a member

        self.plain = UserFactory.create("with_foss_website_user_role")

        self.reviewer = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", self.reviewer.name).add_roles("CFP Reviewer")

        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)
        self.other_chapter.delete(force=True)
        self.chapter.delete(force=True)
        frappe.get_doc("User", self.ctm.name).remove_roles("Chapter Team Member")
        frappe.get_doc("User", self.reviewer.name).remove_roles("CFP Reviewer")

    # --- cfp_submission_query ---

    def test_cfp_system_manager_unrestricted(self):
        self.assertEqual(cfp_submission_query("Administrator"), "")

    def test_cfp_reviewer_unrestricted(self):
        self.assertEqual(cfp_submission_query(self.reviewer.name), "")

    def test_cfp_plain_user_own_only(self):
        result = cfp_submission_query(self.plain.name)
        self.assertIn("submitted_by", result)
        self.assertNotIn("chapter IN", result)

    def test_cfp_ctm_includes_own_chapter(self):
        result = cfp_submission_query(self.ctm.name)
        self.assertIn("chapter IN", result)
        self.assertIn(self.chapter.name, result)
        self.assertIn("submitted_by", result)

    def test_cfp_ctm_excludes_other_chapter(self):
        result = cfp_submission_query(self.ctm.name)
        self.assertNotIn(self.other_chapter.name, result)

    # --- rsvp_submission_query ---

    def test_rsvp_system_manager_unrestricted(self):
        self.assertEqual(rsvp_submission_query("Administrator"), "")

    def test_rsvp_plain_user_blocks_all(self):
        self.assertEqual(rsvp_submission_query(self.plain.name), "1=0")

    def test_rsvp_ctm_includes_own_chapter(self):
        result = rsvp_submission_query(self.ctm.name)
        self.assertIn("chapter IN", result)
        self.assertIn(self.chapter.name, result)

    def test_rsvp_ctm_excludes_other_chapter(self):
        result = rsvp_submission_query(self.ctm.name)
        self.assertNotIn(self.other_chapter.name, result)


class TestChapterScopedWrites(FrappeTestCase):
    """A Chapter Team Member can change only the records of chapters and events they belong to."""

    def setUp(self):
        frappe.set_user("Administrator")
        self.ctm = UserFactory.create("with_foss_website_user_role")
        self.ctm_profile = get_foss_profile_id(self.ctm.name)
        self.chapter = FOSSChapterFactory.create("with_members", members=[self.ctm.name])
        self.other_chapter = FOSSChapterFactory.create("with_members")  # ctm NOT a member

        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)
        self.other_event = FOSSChapterEventFactory.create(
            "with_paid_tickets", chapter=self.other_chapter.name
        )
        self.cfp = FOSSEventCFPFactory.create(event=self.event.name)
        self.other_cfp = FOSSEventCFPFactory.create(event=self.other_event.name)
        self.created = []

    def tearDown(self):
        frappe.set_user("Administrator")
        for doctype, name in reversed(self.created):
            frappe.delete_doc(doctype, name, force=True)
        for cfp in (self.cfp, self.other_cfp):
            frappe.delete_doc(EVENT_CFP, cfp.name, force=True)
        for event in (self.event, self.other_event):
            frappe.delete_doc(EVENT, event.name, force=True)
        for chapter in (self.chapter, self.other_chapter):
            frappe.delete_doc(CHAPTER, chapter.name, force=True)
        frappe.get_doc("User", self.ctm.name).remove_roles("Chapter Team Member")

    def roster(self, chapter: str) -> list[str]:
        return sorted(
            frappe.get_all(
                CHAPTER_MEMBER,
                {"parent": chapter, "parenttype": CHAPTER},
                pluck="chapter_member",
            )
        )

    def test_ctm_has_the_role_on_their_own_chapter(self):
        self.assertIn("Chapter Team Member", frappe.get_roles(self.ctm.name))

    def test_cannot_add_self_to_another_chapters_roster(self):
        before = self.roster(self.other_chapter.name)
        rows = [
            {"chapter_member": m.chapter_member, "role": m.role}
            for m in self.other_chapter.chapter_members
        ]
        rows.append({"chapter_member": self.ctm_profile, "role": "Volunteer"})

        frappe.set_user(self.ctm.name)
        self.assertFalse(frappe.get_doc(CHAPTER, self.other_chapter.name).has_permission("write"))
        with self.assertRaises(frappe.PermissionError):
            frappe.client.set_value(CHAPTER, self.other_chapter.name, {"chapter_members": rows})
        with self.assertRaises(frappe.PermissionError):
            frappe.client.insert_doc(
                {
                    "doctype": CHAPTER_MEMBER,
                    "parenttype": CHAPTER,
                    "parent": self.other_chapter.name,
                    "parentfield": "chapter_members",
                    "chapter_member": self.ctm_profile,
                    "role": "Volunteer",
                }
            )

        frappe.set_user("Administrator")
        self.assertEqual(self.roster(self.other_chapter.name), before)

    def test_can_still_edit_own_chapter_and_roster(self):
        new_user = UserFactory.create("with_foss_website_user_role")
        new_profile = get_foss_profile_id(new_user.name)

        frappe.set_user(self.ctm.name)
        frappe.client.set_value(CHAPTER, self.chapter.name, "x", "https://example.com/own")
        chapter = frappe.get_doc(CHAPTER, self.chapter.name)
        chapter.append("chapter_members", {"chapter_member": new_profile, "role": "Volunteer"})
        chapter.save()

        frappe.set_user("Administrator")
        self.assertEqual(
            frappe.db.get_value(CHAPTER, self.chapter.name, "x"), "https://example.com/own"
        )
        self.assertIn(new_profile, self.roster(self.chapter.name))

    def test_reads_are_unchanged(self):
        frappe.set_user(self.ctm.name)
        self.assertEqual(
            frappe.client.get(CHAPTER, self.other_chapter.name)["name"], self.other_chapter.name
        )
        self.assertEqual(
            frappe.client.get(EVENT, self.other_event.name)["name"], self.other_event.name
        )
        self.assertTrue(
            frappe.has_permission(EVENT, "read", doc=self.other_event.name, user="Guest")
        )

    def test_cannot_create_event_in_another_chapter(self):
        frappe.set_user(self.ctm.name)
        with self.assertRaises(frappe.PermissionError):
            FOSSChapterEventFactory.create(chapter=self.other_chapter.name)

        own = FOSSChapterEventFactory.create(chapter=self.chapter.name)
        self.created.append((EVENT, own.name))

    def test_cannot_edit_or_delete_another_chapters_event(self):
        tier = self.other_event.tiers[0].name
        attempts = {
            "event field": lambda: frappe.client.set_value(
                EVENT, self.other_event.name, "tickets_status", "Closed"
            ),
            "ticket tier row": lambda: frappe.client.set_value(TICKET_TIER, tier, "price", 1),
        }

        frappe.set_user(self.ctm.name)
        for label, attempt in attempts.items():
            with self.subTest(label), self.assertRaises(frappe.PermissionError):
                attempt()
        self.assertFalse(frappe.has_permission(EVENT, "delete", doc=self.other_event.name))
        self.assertTrue(frappe.has_permission(EVENT, "delete", doc=self.event.name))

        frappe.set_user("Administrator")
        self.assertEqual(
            frappe.db.get_value(EVENT, self.other_event.name, "tickets_status"), "Live"
        )
        self.assertEqual(frappe.db.get_value(TICKET_TIER, tier, "price"), 100)

    def test_can_edit_own_event_but_not_move_it_to_another_chapter(self):
        frappe.set_user(self.ctm.name)
        frappe.client.set_value(EVENT, self.event.name, "event_name", "Renamed by own team")
        with self.assertRaises(frappe.PermissionError):
            frappe.client.set_value(EVENT, self.event.name, "chapter", self.other_chapter.name)

        frappe.set_user("Administrator")
        event = frappe.db.get_value(
            EVENT, self.event.name, ["event_name", "chapter"], as_dict=True
        )
        self.assertEqual(event.event_name, "Renamed by own team")
        self.assertEqual(event.chapter, self.chapter.name)

    def test_event_team_member_can_edit_event_but_not_move_it(self):
        event = frappe.get_doc(EVENT, self.other_event.name)
        event.append("event_members", {"member": self.ctm_profile, "role": "Volunteer"})
        event.save()

        frappe.set_user(self.ctm.name)
        frappe.client.set_value(EVENT, self.other_event.name, "event_name", "Edited by event team")
        with self.assertRaises(frappe.PermissionError):
            frappe.client.set_value(EVENT, self.other_event.name, "chapter", self.chapter.name)

        frappe.set_user("Administrator")
        self.assertEqual(
            frappe.db.get_value(EVENT, self.other_event.name, "chapter"), self.other_chapter.name
        )

    def test_cannot_manage_another_chapters_rsvp_or_cfp(self):
        frappe.set_user(self.ctm.name)
        with self.assertRaises(frappe.PermissionError):
            FOSSEventRSVPFactory.create(event=self.other_event.name)
        with self.assertRaises(frappe.PermissionError):
            frappe.client.set_value(
                EVENT_CFP, self.other_cfp.name, "cfp_form_description", "Edited by outsider"
            )
        with self.assertRaises(frappe.PermissionError):
            frappe.client.set_value(EVENT_CFP, self.cfp.name, "event", self.other_event.name)

        # Own event's forms still work
        frappe.client.set_value(EVENT_CFP, self.cfp.name, "cfp_form_description", "Own edit")
        rsvp = FOSSEventRSVPFactory.create(event=self.event.name)
        self.created.append((EVENT_RSVP, rsvp.name))

        frappe.set_user("Administrator")
        self.assertEqual(frappe.db.get_value(EVENT_CFP, self.cfp.name, "event"), self.event.name)

    def test_cannot_take_rows_from_another_chapters_records(self):
        other_row = self.other_chapter.chapter_members[0].name
        other_tier = self.other_event.tiers[0].name

        own_chapter = frappe.get_doc(CHAPTER, self.chapter.name).as_dict()
        own_chapter["chapter_members"].append(frappe.get_doc(CHAPTER_MEMBER, other_row).as_dict())
        own_event = frappe.get_doc(EVENT, self.event.name).as_dict()
        own_event["tiers"] = [frappe.get_doc(TICKET_TIER, other_tier).as_dict()]

        attempts = {
            "own chapter carrying another chapter's roster row": lambda: frappe.client.save(
                own_chapter
            ),
            "own event carrying another event's ticket tier": lambda: frappe.client.save(
                own_event
            ),
            "other event saved under own event's name": lambda: frappe.client.set_value(
                EVENT,
                self.other_event.name,
                {
                    "name": self.event.name,
                    # own event's current values, so Frappe's own checks pass and the hook decides
                    **{
                        field: str(frappe.db.get_value(EVENT, self.event.name, field))
                        for field in ("modified", "creation")
                    },
                    "chapter": self.chapter.name,
                },
            ),
        }

        frappe.set_user(self.ctm.name)
        for label, attempt in attempts.items():
            with self.subTest(label), self.assertRaises(frappe.PermissionError):
                attempt()

        frappe.set_user("Administrator")
        self.assertEqual(
            frappe.db.get_value(CHAPTER_MEMBER, other_row, "parent"), self.other_chapter.name
        )
        self.assertEqual(
            frappe.db.get_value(TICKET_TIER, other_tier, "parent"), self.other_event.name
        )

    def test_write_share_does_not_allow_taking_rows(self):
        # A document shared with write access passes Frappe's permission check even when the
        # has_permission hook says no, so the row check must also hold on save.
        other_row = self.other_chapter.chapter_members[0].name
        friend = UserFactory.create("with_foss_website_user_role")

        for label, sharee in (
            ("shared with self", self.ctm.name),
            ("shared with friend", friend.name),
        ):
            with self.subTest(label):
                frappe.set_user(self.ctm.name)
                frappe.share.add(CHAPTER, self.chapter.name, sharee, write=1)

                frappe.set_user(sharee)
                own_chapter = frappe.get_doc(CHAPTER, self.chapter.name).as_dict()
                own_chapter["chapter_members"].append(
                    frappe.get_doc(CHAPTER_MEMBER, other_row).as_dict()
                )
                with self.assertRaises(frappe.PermissionError):
                    frappe.client.save(own_chapter)

                frappe.set_user("Administrator")
                self.assertEqual(
                    frappe.db.get_value(CHAPTER_MEMBER, other_row, "parent"),
                    self.other_chapter.name,
                )

    def test_event_team_can_edit_event_without_a_chapter(self):
        event = FOSSChapterEventFactory.create(chapter=None)
        self.created.append((EVENT, event.name))
        event.append("event_members", {"member": self.ctm_profile, "role": "Volunteer"})
        event.save()

        frappe.set_user(self.ctm.name)
        frappe.client.set_value(EVENT, event.name, {"event_name": "Edited", "chapter": ""})

        frappe.set_user("Administrator")
        self.assertEqual(frappe.db.get_value(EVENT, event.name, "event_name"), "Edited")
        self.assertFalse(frappe.db.get_value(EVENT, event.name, "chapter"))

    def test_system_manager_off_roster_can_edit_any_chapter(self):
        manager = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", manager.name).add_roles("System Manager")
        try:
            frappe.set_user(manager.name)
            frappe.client.set_value(
                CHAPTER, self.other_chapter.name, "x", "https://example.com/sm"
            )
            frappe.client.set_value(EVENT, self.other_event.name, "event_name", "Edited by admin")
        finally:
            frappe.set_user("Administrator")
            frappe.get_doc("User", manager.name).remove_roles("System Manager")

        self.assertEqual(
            frappe.db.get_value(EVENT, self.other_event.name, "event_name"), "Edited by admin"
        )
