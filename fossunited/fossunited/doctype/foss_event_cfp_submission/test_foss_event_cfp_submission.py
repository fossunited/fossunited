import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
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

LEAD = "test1@example.com"


class TestFOSSEventCFPSubmission(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter(lead_email=LEAD)
        self.event = insert_test_event(chapter=self.chapter)

        self.cfp = insert_cfp_form(event=self.event.name)
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

        frappe.set_user(LEAD)
        # When the status is changed to Approved
        self.submission.status = "Approved"
        self.submission.save()

        # Then the speaker emails of this submission should be added to an email group
        # for this event, where type==Accepted Proposers

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event, speaker.email, "Accepted Proposers")
            )

    def test_add_to_group_on_reject(self):
        # given a cfp and its submission
        frappe.set_user(LEAD)
        # When the status is changed to Approved
        self.submission.status = "Rejected"
        self.submission.save()

        # Then the speaker emails of this submission should be added to an email group
        # for this event, where type==Rejected Proposers

        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event, speaker.email, "Rejected Proposers")
            )

    def test_multiple_submission_by_same_email(self):
        # given a cfp
        # When multiple submissions are done by the same email
        # Then they should be submitted without any error.
        submission_email = "test4@example.com"

        frappe.set_user(submission_email)
        for _ in range(3):
            submission = insert_cfp_submission(
                linked_cfp=self.cfp.name, event=self.cfp.event, email=submission_email
            )

            self.assertTrue(submission)

        # And the speakers of these submissions should be added to the email group for this event
        for speaker in self.submission.speakers:
            self.assertTrue(
                self.is_added_to_email_group(self.event, speaker.email, "CFP Proposers")
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
