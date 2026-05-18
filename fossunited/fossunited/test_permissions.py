import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import EVENT
from fossunited.fossunited.permissions import cfp_submission_query, rsvp_submission_query
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    UserFactory,
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
