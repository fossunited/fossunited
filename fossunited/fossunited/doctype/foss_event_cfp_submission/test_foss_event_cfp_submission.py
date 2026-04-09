import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    PROPOSAL,
)
from fossunited.tests.utils import (
    insert_cfp_form,
    insert_cfp_submission,
    insert_test_chapter,
    insert_test_event,
)

fake = Faker()

CoreTeam = "test1@example.com"


class TestFOSSEventCFPSubmission(FrappeTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter(members=[CoreTeam])
        self.event = insert_test_event(chapter=self.chapter)

        self.cfp = insert_cfp_form(event=self.event.name, status="Live")
        speakers = [
            {
                "full_name": fake.name(),
                "email": fake.email(),
                "designation": fake.job(),
                "organization": fake.company(),
                "bio": "Test Submission",
            }
        ]
        self.submission = insert_cfp_submission(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            speakers=speakers,
            submitted_by=CoreTeam,
        )

    def tearDown(self):
        frappe.set_user("Administrator")

        submissions = frappe.get_all(PROPOSAL, {"event": self.event.name}, pluck="name")
        for submission in submissions:
            frappe.delete_doc(PROPOSAL, submission, force=True)
        self.cfp.delete(force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def test_add_to_email_group(self):
        # given a cfp form
        cfp = self.cfp

        # When a submission is done by user
        # Then the speaker emails should be added to an email group for this event,
        # where type==CFP Proposers

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(cfp.event, speaker.email, "CFP Proposers")
            )

    def test_add_to_group_on_accept(self):
        # given a cfp and its submission

        frappe.set_user(CoreTeam)
        # When the status is changed to Approved
        self.submission.status = "Approved"
        self.submission.save()

        # Then the speaker emails of this submission should be added to an email group
        # for this event, where type==Accepted Proposers

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "Accepted Proposers")
            )

    def test_add_to_group_on_reject(self):
        # given a cfp and its submission
        frappe.set_user(CoreTeam)
        # When the status is changed to Approved
        self.submission.status = "Rejected"
        self.submission.save()

        # Then the speaker emails of this submission should be added to an email group
        # for this event, where type==Rejected Proposers

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "Rejected Proposers")
            )

    def test_multiple_submission_by_same_email(self):
        # given a cfp
        # When multiple submissions are done by the same email
        # Then they should be submitted without any error.
        submission_email = "test4@example.com"

        frappe.set_user(submission_email)
        for _ in range(3):
            submission = insert_cfp_submission(
                linked_cfp=self.cfp.name,
                event=self.event.name,
                email=submission_email,
                submitted_by=submission_email,
            )

            self.assertTrue(submission)

        # And the speakers of these submissions should be added to the email group for this event
        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "CFP Proposers")
            )

    def is_added_to_email_group(self, event_id, email, group_type):
        email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": event_id,
                "document_type": EVENT,
                "group_type": group_type,
            },
        )

        return bool(
            frappe.db.exists("Email Group Member", {"email": email, "email_group": email_group})
        )

    def test_no_email_group_when_unsubscribed(self):
        # Given a CFP form and submission
        speakers = [
            {
                "full_name": fake.name(),
                "email": "nosubscribe@example.com",
                "designation": fake.job(),
                "organization": fake.company(),
                "bio": "Test Submission",
            }
        ]
        submission = insert_cfp_submission(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            speakers=speakers,
            submitted_by=CoreTeam,
        )
        submission.subscribe_chapter_mailing = 0
        submission.save()

        # They should must be added to CFP Proposers group by default
        for speaker in submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "CFP Proposers")
            )
        chapter_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.chapter.name,
                "document_type": CHAPTER,
                "group_type": "Chapter CFP Proposers",
            },
        )
        submission.delete(force=True, ignore_permissions=True)

        for sp in submission.speakers:
            self.assertFalse(
                frappe.db.exists(
                    "Email Group Member",
                    {"email": sp.email, "email_group": chapter_group},
                )
            )

    def test_status_change_no_add_when_unsubscribed(self):
        # Given a submission with mailing unsubscribed
        self.submission.subscribe_chapter_mailing = 0
        self.submission.save()

        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "Accepted Proposers")
            )

    def test_removal_from_email_group_on_unsubscribe(self):
        # Given a submission with subscription enabled
        self.assertEqual(self.submission.subscribe_chapter_mailing, 1)

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, speaker.email, "CFP Proposers")
            )

        # When user unsubscribes & is rejected
        self.submission.subscribe_chapter_mailing = 0
        self.submission.status = "Rejected"
        self.submission.save()

        # they should not be in chapter group, can be in cfp proposers group
        for speaker in self.submission.speakers:
            chapter_group = frappe.db.get_value(
                "Email Group",
                {
                    "reference_document": self.chapter.name,
                    "document_type": CHAPTER,
                    "group_type": "Chapter CFP Proposers",
                },
            )
            self.assertFalse(
                frappe.db.exists(
                    "Email Group Member",
                    {"email": speaker.email, "email_group": chapter_group},
                )
            )
        # should still present in event CFP Proposers
        for sp in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event.name, sp.email, "CFP Proposers")
            )

    def test_withdrawal_changes_status_to_withdrawn(self):
        # Given an approved submission
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()

        self.submission.is_withdrawn = 1
        self.submission.save()

        self.assertEqual(self.submission.status, "Withdrawn")

    def _get_single_email(self, reference_doctype=PROPOSAL, reference_name=None):
        """Return the single Email Queue doc for a given reference."""
        if reference_name is None:
            reference_name = self.submission.name

        email_name = frappe.db.get_value(
            "Email Queue",
            {
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
            },
            "name",
        )

        self.assertIsNotNone(
            email_name,
            f"No Email Queue record found for {reference_doctype} {reference_name}",
        )

        return frappe.get_doc("Email Queue", email_name)

    def _assert_email_sent(
        self,
        subject_contains: str,
        expected_recipients: list[str],
        reference_doctype=PROPOSAL,
        reference_name=None,
    ):
        """Assert an email was queued with the given subject fragment and recipients."""
        email = self._get_single_email(reference_doctype, reference_name)

        self.assertIn(subject_contains, email.message)

        # Recipients is a child table; collect all emails into a set
        recipients = {r.recipient for r in email.recipients}
        for addr in expected_recipients:
            self.assertIn(
                addr,
                recipients,
                f"Expected recipient {addr} not found in {recipients}",
            )

    def test_un_withdrawal_restores_status(self):
        # Given a withdrawn submission
        frappe.set_user(CoreTeam)
        self.submission.is_withdrawn = 1
        self.submission.save()
        self.assertEqual(self.submission.status, "Withdrawn")

        # When withdrawal is reverted
        self.submission.is_withdrawn = 0
        self.submission.save()

        # Then status should be Review Pending
        self.assertEqual(self.submission.status, "Review Pending")

    def test_session_type_invited_talk_blocked_for_website_users(self):
        # Given a website user
        frappe.set_user("test_website_user@example.com")

        # When trying to set session_type to Invited Talk
        # Then it should raise PermissionError
        with self.assertRaises(frappe.PermissionError):
            self.submission.session_type = "Invited Talk"
            self.submission.save()

    def test_withdrawal_notifies_team_when_approved(self):
        # Given an approved submission
        frappe.set_user(CoreTeam)
        self.submission.status = "Approved"
        self.submission.save()

        # Clear email queue
        frappe.db.delete("Email Queue")

        # When it is withdrawn
        self.submission.is_withdrawn = 1
        self.submission.save()

        # Then team should be notified via email
        self._assert_email_sent(
            subject_contains="Withdrawn",
            expected_recipients=[self.chapter.email],
        )

    def test_notify_proposer_on_new_review(self):
        # Given a submission
        frappe.set_user(CoreTeam)
        frappe.db.delete("Email Queue")

        # When a review is added
        self.submission.append(
            "reviews",
            {
                "reviewer": CoreTeam,
                "to_approve": "Yes",
                "remarks": "Great proposal!",
            },
        )
        self.submission.save()

        # Then proposer should be notified
        self._assert_email_sent(
            subject_contains="New review",
            expected_recipients=[self.submission.email],
        )

    def test_notify_proposer_on_remarks_changed(self):
        frappe.set_user(CoreTeam)

        # When a review is added
        self.submission.append(
            "reviews",
            {
                "reviewer": CoreTeam,
                "to_approve": "Maybe",
                "remarks": "This needs more explanation.",
            },
        )
        self.submission.save()

        frappe.db.delete("Email Queue")
        self.submission.reviews[0].remarks = "This is promising now!"
        self.submission.save()

        self._assert_email_sent(
            subject_contains="Review remarks updated on your proposal for",
            expected_recipients=[self.submission.email],
        )

    def test_get_review_scores_calculation(self):
        # Given a submission with multiple reviews
        frappe.set_user(CoreTeam)
        self.submission.append(
            "reviews", {"reviewer": CoreTeam, "to_approve": "Yes", "remarks": ""}
        )
        self.submission.append(
            "reviews", {"reviewer": CoreTeam, "to_approve": "Yes", "remarks": ""}
        )
        self.submission.append(
            "reviews", {"reviewer": CoreTeam, "to_approve": "No", "remarks": ""}
        )
        self.submission.append(
            "reviews", {"reviewer": CoreTeam, "to_approve": "Maybe", "remarks": ""}
        )
        self.submission.save()

        # When getting review scores
        scores = self.submission.get_review_scores()

        # Then scores should be calculated correctly
        self.assertEqual(scores["positive"], 2)
        self.assertEqual(scores["negative"], 1)
        self.assertEqual(scores["unsure"], 1)

    def test_set_scores_updates_fields(self):
        # Given a submission with reviews
        frappe.set_user(CoreTeam)
        self.submission.append(
            "reviews", {"reviewer": CoreTeam, "to_approve": "Yes", "remarks": ""}
        )
        self.submission.save()

        # Then score fields should be updated
        self.assertIsNotNone(self.submission.positive_reviews)
        self.assertIsNotNone(self.submission.negative_reviews)
