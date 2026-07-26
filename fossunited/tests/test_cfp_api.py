import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.cfp import get_cfp_submissions, set_submission_reviewers
from fossunited.doctype_ids import EVENT, PROPOSAL
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
    FOSSEventCFPSubmissionFactory,
    UserFactory,
)
from fossunited.tests.utils import insert_user_profile

CTM = "test1@example.com"


class TestCFPAssignmentAPIs(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        frappe.set_user("Administrator")

        cls.reviewer = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", cls.reviewer.name).add_roles("CFP Reviewer")
        insert_user_profile(cls.reviewer.name)

        insert_user_profile(CTM)
        cls.chapter = FOSSChapterFactory.create("with_members", members=[CTM])
        frappe.get_doc("User", CTM).add_roles("Chapter Team Member")
        cls.event = FOSSChapterEventFactory.create(chapter=cls.chapter.name)
        cls.cfp = FOSSEventCFPFactory.create(event=cls.event.name)
        cls.sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=cls.cfp.name, event=cls.event.name, submitted_by=CTM
        )

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")
        frappe.db.delete("ToDo", {"reference_type": PROPOSAL, "reference_name": cls.sub.name})
        frappe.delete_doc(PROPOSAL, cls.sub.name, force=True, ignore_missing=True)
        cls.cfp.delete(force=True)
        frappe.delete_doc(EVENT, cls.event.name, force=True)
        cls.chapter.delete(force=True)
        if frappe.db.exists("User", cls.reviewer.name):
            frappe.get_doc("User", cls.reviewer.name).remove_roles("CFP Reviewer")
        if frappe.db.exists("User", CTM):
            frappe.get_doc("User", CTM).remove_roles("Chapter Team Member")
        super().tearDownClass()

    def tearDown(self):
        # Clean up only per-test side effects; fixtures live for the whole class.
        frappe.set_user("Administrator")
        frappe.db.delete("ToDo", {"reference_type": PROPOSAL, "reference_name": self.sub.name})
        frappe.db.delete("Notification Log", {"for_user": self.reviewer.name})

    def test_assign_sends_notification(self):
        frappe.set_user(CTM)
        set_submission_reviewers(self.sub.name, [self.reviewer.name])
        self.assertTrue(
            frappe.db.exists(
                "Notification Log",
                {
                    "for_user": self.reviewer.name,
                    "document_type": PROPOSAL,
                    "document_name": self.sub.name,
                },
            )
        )

    def test_unassign_deletes_todo(self):
        frappe.set_user(CTM)
        set_submission_reviewers(self.sub.name, [self.reviewer.name])
        set_submission_reviewers(self.sub.name, [])
        self.assertFalse(
            frappe.db.exists("ToDo", {"reference_type": PROPOSAL, "reference_name": self.sub.name})
        )

    def test_idempotent_assign_no_duplicate_todo(self):
        # Saving the same reviewer twice must not double-notify.
        frappe.set_user(CTM)
        set_submission_reviewers(self.sub.name, [self.reviewer.name])
        set_submission_reviewers(self.sub.name, [self.reviewer.name])
        count = len(
            frappe.db.get_all(
                "ToDo", {"reference_type": PROPOSAL, "reference_name": self.sub.name}
            )
        )
        self.assertEqual(count, 1)

    def test_get_cfp_submissions_enrichment_keys(self):
        frappe.set_user(CTM)
        results = get_cfp_submissions(self.event.name)
        sub = next((r for r in results if r["name"] == self.sub.name), None)
        self.assertIsNotNone(sub)
        for key in (
            "_is_reviewed",
            "_is_assigned",
            "_likes_count",
            "_review_count",
            "approved_percent",
            "speakers",
            "_assigned_users",
        ):
            self.assertIn(key, sub)


class TestCFPEditWindowAPI(FrappeTestCase):
    def tearDown(self):
        frappe.set_user("Administrator")

    def test_can_edit_proposal_returns_bool(self):
        from frappe.utils import add_to_date, now_datetime

        from fossunited.api.cfp import can_edit_proposal

        cfp = FOSSEventCFPFactory.create(
            allow_cfp_edit=1, status="Live", deadline=add_to_date(now_datetime(), days=2)
        )
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=cfp.name, submitted_by="Administrator", email="Administrator"
        )
        frappe.set_user("Administrator")
        self.assertTrue(can_edit_proposal(sub.name))
