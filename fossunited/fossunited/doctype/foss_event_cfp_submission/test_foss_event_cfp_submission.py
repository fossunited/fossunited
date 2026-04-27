import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import PROPOSAL
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
    FOSSEventCFPSubmissionFactory,
)

CoreTeam = "test1@example.com"
Reviewer = "test2@example.com"
Submitter = "test4@example.com"


class TestFOSSEventCFPSubmission(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create("with_members", members=[CoreTeam])
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)
        self.cfp = FOSSEventCFPFactory.create(event=self.event.name)
        self.submission = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            submitted_by=CoreTeam,
        )
        if not frappe.db.exists("Has Role", {"role": "CFP Reviewer", "parent": Reviewer}):
            frappe.get_doc("User", Reviewer).add_roles("CFP Reviewer")

    def tearDown(self):
        frappe.set_user("Administrator")
        for name in frappe.get_all(PROPOSAL, {"event": self.event.name}, pluck="name"):
            frappe.delete_doc(PROPOSAL, name, force=True)
        self.cfp.delete(force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)
        frappe.get_doc("User", Reviewer).remove_roles("CFP Reviewer")

    # --- helpers ---

    def _email_group_has(self, reference, email, group_type):
        group = frappe.db.get_value(
            "Email Group",
            {"reference_document": reference, "group_type": group_type},
        )
        return bool(frappe.db.exists("Email Group Member", {"email": email, "email_group": group}))

    def _add_review(self, reviewer, to_approve="Yes", remarks=""):
        self.submission.append(
            "reviews",
            {
                "reviewer": reviewer,
                "email": reviewer,
                "to_approve": to_approve,
                "remarks": remarks,
            },
        )
        self.submission.save()
        self.submission.reload()

    # --- permission tests ---

    def test_owner_can_edit_l1_field(self):
        frappe.set_user(Submitter)
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            submitted_by=Submitter,
        )
        sub.talk_title = "Updated Title"
        sub.save()
        sub.reload()
        self.assertEqual(sub.talk_title, "Updated Title")
        sub.delete(force=True, ignore_permissions=True)

    def test_owner_cannot_change_status(self):
        # status at L3 — "All" has no L3 write
        frappe.set_user(Submitter)
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            submitted_by=Submitter,
        )
        sub.status = "Approved"
        sub.save()
        sub.reload()
        self.assertNotEqual(sub.status, "Approved")
        sub.delete(force=True, ignore_permissions=True)

    def test_owner_cannot_write_reviews(self):
        # reviews at L2 — "All" has no L2 write
        frappe.set_user(Submitter)
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            submitted_by=Submitter,
        )
        sub.append("reviews", {"reviewer": Submitter, "email": Submitter, "to_approve": "Yes"})
        sub.save()
        sub.reload()
        self.assertEqual(len(sub.reviews), 0)
        sub.delete(force=True, ignore_permissions=True)

    def test_chapter_team_member_can_read_l1_fields(self):
        frappe.set_user(CoreTeam)
        doc = frappe.get_doc(PROPOSAL, self.submission.name)
        self.assertIsNotNone(doc.talk_title)

    def test_chapter_team_member_cannot_write_l1_fields(self):
        # Chapter Team Member has L1 read only — write silently blocked
        frappe.set_user(CoreTeam)
        original = self.submission.talk_title
        self.submission.talk_title = "CTM Attempted Edit"
        self.submission.save()
        self.submission.reload()
        self.assertEqual(self.submission.talk_title, original)

    def test_chapter_team_member_can_change_status(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()
        self.submission.reload()
        self.assertEqual(self.submission.status, "Approved")

    def test_reviewer_can_add_own_review(self):
        frappe.set_user(Reviewer)
        self.submission.append(
            "reviews",
            {
                "reviewer": Reviewer,
                "email": Reviewer,
                "to_approve": "Yes",
                "remarks": "LGTM",
            },
        )
        self.submission.save()
        self.submission.reload()
        self.assertEqual(len(self.submission.reviews), 1)

    def test_reviewer_cannot_add_review_for_other(self):
        frappe.set_user(Reviewer)
        self.submission.append(
            "reviews",
            {"reviewer": Reviewer, "email": "other@example.com", "to_approve": "Yes"},
        )
        with self.assertRaises(frappe.PermissionError):
            self.submission.save()

    def test_reviewer_cannot_add_duplicate_review(self):
        frappe.set_user(Reviewer)
        self.submission.append(
            "reviews", {"reviewer": Reviewer, "email": Reviewer, "to_approve": "Yes"}
        )
        self.submission.append(
            "reviews", {"reviewer": Reviewer, "email": Reviewer, "to_approve": "No"}
        )
        with self.assertRaises(frappe.PermissionError):
            self.submission.save()

    # --- controller tests ---

    def test_withdrawal_sets_status(self):
        frappe.set_user(CoreTeam)
        self.submission.is_withdrawn = 1
        self.submission.save()
        self.assertEqual(self.submission.status, "Withdrawn")

    def test_un_withdrawal_reverts_status(self):
        frappe.set_user(CoreTeam)
        self.submission.is_withdrawn = 1
        self.submission.save()
        self.submission.is_withdrawn = 0
        self.submission.save()
        self.assertEqual(self.submission.status, "Review Pending")

    def test_review_scores_calculated(self):
        frappe.set_user(CoreTeam)
        for verdict in ["Yes", "Yes", "No", "Maybe"]:
            self.submission.append(
                "reviews",
                {"reviewer": CoreTeam, "email": CoreTeam, "to_approve": verdict},
            )
        self.submission.save()
        scores = self.submission.get_review_scores()
        self.assertEqual(scores["positive"], 2)
        self.assertEqual(scores["negative"], 1)
        self.assertEqual(scores["unsure"], 1)

    def test_score_fields_updated_on_save(self):
        frappe.set_user(CoreTeam)
        self._add_review(CoreTeam, "Yes")
        self.assertGreater(int(self.submission.positive_reviews or 0), 0)

    def test_approved_adds_to_accepted_email_group(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()
        for speaker in self.submission.speakers:
            self.assertTrue(
                self._email_group_has(self.event.name, speaker.email, "Accepted Proposers")
            )

    def test_rejected_adds_to_rejected_email_group(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Rejected"
        self.submission.save()
        for speaker in self.submission.speakers:
            self.assertTrue(
                self._email_group_has(self.event.name, speaker.email, "Rejected Proposers")
            )

    def test_withdrawal_of_approved_sends_email(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()
        frappe.db.delete("Email Queue")
        self.submission.is_withdrawn = 1
        self.submission.save()
        self.assertTrue(
            frappe.db.exists(
                "Email Queue",
                {"reference_doctype": PROPOSAL, "reference_name": self.submission.name},
            )
        )
