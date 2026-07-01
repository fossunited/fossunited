import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from fossunited.doctype_ids import EVENT, EVENT_CFP, PROPOSAL
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
    FOSSEventCFPSubmissionFactory,
    UserFactory,
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
        self._added_cfp_reviewer = not frappe.db.exists(
            "Has Role", {"role": "CFP Reviewer", "parent": Reviewer}
        )
        if self._added_cfp_reviewer:
            frappe.get_doc("User", Reviewer).add_roles("CFP Reviewer")

    def tearDown(self):
        frappe.set_user("Administrator")
        for name in frappe.get_all(PROPOSAL, {"event": self.event.name}, pluck="name"):
            frappe.delete_doc(PROPOSAL, name, force=True)
        self.cfp.delete(force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)
        if self._added_cfp_reviewer:
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

    # --- deadline auto-close tests ---

    def test_submit_past_deadline_throws(self):
        past_cfp = FOSSEventCFPFactory.create(
            event=self.event.name,
            deadline=add_to_date(now_datetime(), days=-1),
            status="Live",
        )
        frappe.set_user(CoreTeam)
        with self.assertRaises(frappe.PermissionError):
            FOSSEventCFPSubmissionFactory.create(
                linked_cfp=past_cfp.name,
                event=self.event.name,
                submitted_by=CoreTeam,
            )
        # submit path rejects but does not write; status flips only on the next read
        self.assertEqual(frappe.db.get_value(EVENT_CFP, past_cfp.name, "status"), "Live")
        past_cfp.delete(force=True)

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

    # --- proposer edit-lock tests ---

    def _closed_submission(self, **cfp_overrides):
        """A submission whose CFP is closed to proposer edits, owned by Submitter."""
        cfp = FOSSEventCFPFactory.create(event=self.event.name, **cfp_overrides)
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=cfp.name, event=self.event.name, submitted_by=Submitter, email=Submitter
        )
        return cfp, sub

    def test_proposer_edit_blocked_when_allow_cfp_edit_off(self):
        _, sub = self._closed_submission(allow_cfp_edit=0, status="Live")
        frappe.set_user(Submitter)
        sub.talk_title = "Edited after lock"
        with self.assertRaises(frappe.PermissionError):
            sub.save()

    def test_proposer_edit_blocked_past_deadline(self):
        _, sub = self._closed_submission(
            allow_cfp_edit=1, status="Live", deadline=add_to_date(now_datetime(), days=-1)
        )
        frappe.set_user(Submitter)
        sub.talk_description = "Edited after deadline"
        with self.assertRaises(frappe.PermissionError):
            sub.save()

    def test_proposer_edit_blocked_when_status_closed(self):
        _, sub = self._closed_submission(
            allow_cfp_edit=1, status="Closed", deadline=add_to_date(now_datetime(), days=3)
        )
        frappe.set_user(Submitter)
        sub.talk_title = "Edited while closed"
        with self.assertRaises(frappe.PermissionError):
            sub.save()

    def test_proposer_edit_allowed_when_window_open(self):
        cfp = FOSSEventCFPFactory.create(
            event=self.event.name,
            allow_cfp_edit=1,
            status="Live",
            deadline=add_to_date(now_datetime(), days=3),
        )
        sub = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=cfp.name, event=self.event.name, submitted_by=Submitter, email=Submitter
        )
        frappe.set_user(Submitter)
        sub.talk_title = "Edited within window"
        sub.save()  # must not raise
        sub.reload()
        self.assertEqual(sub.talk_title, "Edited within window")

    def test_proposer_can_withdraw_after_close(self):
        _, sub = self._closed_submission(allow_cfp_edit=0, status="Live")
        frappe.set_user(Submitter)
        sub.is_withdrawn = 1
        sub.save()  # withdraw is not a content change -> allowed
        sub.reload()
        self.assertEqual(sub.status, "Withdrawn")

    def test_reviewer_can_review_after_close(self):
        _, sub = self._closed_submission(
            allow_cfp_edit=1, status="Live", deadline=add_to_date(now_datetime(), days=-1)
        )
        frappe.set_user(Reviewer)
        sub.append("reviews", {"reviewer": Reviewer, "email": Reviewer, "to_approve": "Yes"})
        sub.save()  # no content change -> allowed
        sub.reload()
        self.assertEqual(len(sub.reviews), 1)

    def test_system_manager_can_edit_after_close(self):
        _, sub = self._closed_submission(allow_cfp_edit=0, status="Live")
        frappe.set_user("Administrator")
        sub.talk_title = "Edited by admin"
        sub.save()  # System Manager bypass
        sub.reload()
        self.assertEqual(sub.talk_title, "Edited by admin")

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

    def test_chapter_team_member_l1_write_allowed_server_side_frappe_bug(self):
        # Frappe bug: get_permlevel_access() ignores if_owner at permlevel 1+, so the
        # FOSS Website User role (if_owner) grants CTM effective L1 write server-side.
        # Desk UI enforces read-only via JS. Test documents the known incorrect behaviour.
        # TODO: remove/flip once upstream Frappe fixes if_owner permlevel enforcement.
        frappe.set_user(CoreTeam)
        self.submission.talk_title = "CTM Attempted Edit"
        self.submission.save()
        self.submission.reload()
        self.assertEqual(self.submission.talk_title, "CTM Attempted Edit")

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
        self.submission = frappe.get_doc(PROPOSAL, self.submission.name)
        self.assertEqual(len(self.submission.reviews), 0)

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
        self.submission = frappe.get_doc(PROPOSAL, self.submission.name)
        self.assertEqual(len(self.submission.reviews), 0)

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
        frappe.set_user("Administrator")
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
        self.assertGreater(len(self.submission.speakers), 0)
        for speaker in self.submission.speakers:
            self.assertTrue(
                self._email_group_has(self.event.name, speaker.email, "Accepted Proposers")
            )

    def test_rejected_adds_to_rejected_email_group(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Rejected"
        self.submission.save()
        self.assertGreater(len(self.submission.speakers), 0)
        for speaker in self.submission.speakers:
            self.assertTrue(
                self._email_group_has(self.event.name, speaker.email, "Rejected Proposers")
            )

    def test_withdrawal_of_approved_sends_email(self):
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()
        frappe.db.delete(
            "Email Queue",
            {"reference_doctype": PROPOSAL, "reference_name": self.submission.name},
        )
        self.submission.is_withdrawn = 1
        self.submission.save()
        self.assertTrue(
            frappe.db.exists(
                "Email Queue",
                {"reference_doctype": PROPOSAL, "reference_name": self.submission.name},
            )
        )

    def test_insert_to_closed_cfp_throws(self):
        self.cfp.status = "Closed"
        self.cfp.save()
        try:
            frappe.set_user(CoreTeam)
            with self.assertRaises(frappe.PermissionError):
                FOSSEventCFPSubmissionFactory.create(
                    linked_cfp=self.cfp.name,
                    event=self.event.name,
                    submitted_by=CoreTeam,
                )
        finally:
            self.cfp.status = "Live"
            self.cfp.save()

    def test_invited_talk_blocked_for_website_user(self):
        frappe.set_user("test_website_user@example.com")
        with self.assertRaises(frappe.PermissionError):
            self.submission.session_type = "Invited Talk"
            self.submission.save()

    def test_new_review_notifies_proposer(self):
        frappe.set_user(CoreTeam)
        frappe.db.delete("Email Queue")
        self._add_review(CoreTeam, "Yes", "Great proposal!")
        self.assertTrue(
            frappe.db.exists(
                "Email Queue",
                {"reference_doctype": PROPOSAL, "reference_name": self.submission.name},
            )
        )

    def test_review_remarks_change_notifies_proposer(self):
        frappe.set_user(CoreTeam)
        self._add_review(CoreTeam, "Maybe", "Needs more detail.")
        self.submission.reload()
        frappe.db.delete("Email Queue")
        self.submission.reviews[0].remarks = "Actually looks great now!"
        self.submission.save()
        self.assertTrue(
            frappe.db.exists(
                "Email Queue",
                {"reference_doctype": PROPOSAL, "reference_name": self.submission.name},
            )
        )


class TestCFPHasPermission(FrappeTestCase):
    """CTM chapter-scoped has_permission checks."""

    def setUp(self):
        self.ctm = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", self.ctm.name).add_roles("Chapter Team Member")

        self.reviewer = UserFactory.create("with_foss_website_user_role")
        frappe.get_doc("User", self.reviewer.name).add_roles("CFP Reviewer")

        self.chapter_a = FOSSChapterFactory.create("with_members", members=[self.ctm.name])
        self.chapter_b = FOSSChapterFactory.create()

        self.event_a = FOSSChapterEventFactory.create(chapter=self.chapter_a.name)
        self.cfp_a = FOSSEventCFPFactory.create(event=self.event_a.name)
        self.sub_a = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp_a.name, event=self.event_a.name, submitted_by=Submitter
        )

        self.event_b = FOSSChapterEventFactory.create(chapter=self.chapter_b.name)
        self.cfp_b = FOSSEventCFPFactory.create(event=self.event_b.name)
        self.sub_b = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp_b.name, event=self.event_b.name, submitted_by=Submitter
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        for name in [self.sub_a.name, self.sub_b.name]:
            frappe.delete_doc(PROPOSAL, name, force=True)
        for cfp in [self.cfp_a, self.cfp_b]:
            cfp.delete(force=True)
        for event_name in [self.event_a.name, self.event_b.name]:
            frappe.delete_doc(EVENT, event_name, force=True)
        self.chapter_a.delete(force=True)
        self.chapter_b.delete(force=True)
        frappe.get_doc("User", self.ctm.name).remove_roles("Chapter Team Member")
        frappe.get_doc("User", self.reviewer.name).remove_roles("CFP Reviewer")

    def test_submitter_can_read(self):
        doc = frappe.get_doc(PROPOSAL, self.sub_a.name)
        self.assertTrue(doc.has_permission("read", user=Submitter))

    def test_ctm_same_chapter_can_read(self):
        doc = frappe.get_doc(PROPOSAL, self.sub_a.name)
        self.assertTrue(doc.has_permission("read", user=self.ctm.name))

    def test_ctm_other_chapter_denied(self):
        doc = frappe.get_doc(PROPOSAL, self.sub_b.name)
        self.assertFalse(doc.has_permission("read", user=self.ctm.name))

    def test_cfp_reviewer_can_read_any(self):
        doc = frappe.get_doc(PROPOSAL, self.sub_b.name)
        self.assertTrue(doc.has_permission("read", user=self.reviewer.name))
