import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_RSVP
from fossunited.tests.utils import (
    insert_rsvp_form,
    insert_rsvp_submission,
    insert_test_chapter,
    insert_test_event,
)

fake = Faker()

WEBSITE_USER = "test2@example.com"
CORE_TEAM = "test1@example.com"


class TestFOSSEventRSVPSubmission(FrappeTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter(members=[CORE_TEAM])
        self.event = insert_test_event(chapter=self.chapter)
        self.rsvp = insert_rsvp_form(event=self.event.name)
        self.email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.rsvp.event,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=True)

    def test_unpublish_on_max_count(self):
        # Given an RSVP form with max count
        rsvp = self.rsvp

        # We are using distinct emails here to avoid any unintended duplicate error.
        # So that we can insert the max count of submissions
        emails = set()
        while len(emails) < int(rsvp.max_rsvp_count):
            emails.add(fake.email())

        # When submission count reaches the max count
        for email in emails:
            insert_rsvp_submission(linked_rsvp=self.rsvp.name, email=email)

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published")
        self.assertFalse(is_published)

    def test_add_to_email_group(self):
        # Given an RSVP form for an event
        # When an RSVP response is done by a user
        frappe.set_user("Guest")
        insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            email=WEBSITE_USER,
            subscribe_chapter_mailing=1,
            status="Accepted",
        )

        # Then the email should be added to an email group linked to event for participants
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": WEBSITE_USER, "email_group": self.email_group},
            )
        )

    def test_acceptance_workflow(self):
        # Given an RSVP form with accept all incoming responses
        rsvp = self.rsvp

        frappe.set_user("Guest")
        # When a submission is done
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be accepted
        self.assertTrue(submission.status, "Accepted")

    def test_pending_workflow(self):
        # Given an rsvp with requires_host_approval = True
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is created
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be pending
        self.assertTrue(submission.status, "Pending")

    def test_pending_to_acceptance_workflow(self):
        # Given an rsvp with requires_host_approval = True
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is created
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        # The status should be pending
        self.assertTrue(submission.status, "Pending")

        # Now, as the chapter member,
        frappe.set_user("test1@example.com")
        # We know `test1@example.com` is a chapter member
        # because of how insert_test_chapter is implemented

        # When the submission is accepted
        submission.status = "Accepted"
        # Then it should save without any errors
        submission.save()
        submission.delete(force=True, ignore_permissions=True)

    def test_invalid_status_at_creation(self):
        # Given an rsvp with requires_host_approval = False
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is done with status accepted
        # Then a frappe.PermissionError should be raised
        with self.assertRaises(frappe.PermissionError):
            insert_rsvp_submission(linked_rsvp=rsvp.name, status="Accepted")

    def test_status_change_after_unpublish(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(CORE_TEAM)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is done
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # It should be saved with status as pending
        self.assertEqual(submission.status, "Pending")

        frappe.set_user(CORE_TEAM)
        # When the RSVP form is unpublished
        rsvp.is_published = False
        rsvp.save()
        # and the lead user / system user try to make a change to status
        # Then the status should change without errors
        submission.status = "Rejected"
        submission.save()
        submission.delete(force=True, ignore_permissions=True)

    def test_add_to_email_on_acceptance(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(CORE_TEAM)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is made
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        self.assertEqual(submission.status, "Pending")

        # Then the email should not be added to email group
        # When status is pending

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        # When status is changed to "Accepted"
        frappe.set_user(CORE_TEAM)
        submission.status = "Accepted"
        submission.subscribe_chapter_mailing = 1
        submission.save()

        # Then the email should be added to email group
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )
        submission.delete(force=True, ignore_permissions=True)

    def test_no_add_to_email_on_rejection(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(CORE_TEAM)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is made
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        self.assertEqual(submission.status, "Pending")

        # Then the email should not be added to email group
        # When status is pending

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        # When status is changed to "Accepted"
        frappe.set_user(CORE_TEAM)
        submission.status = "Rejected"
        submission.save()

        # Then the email should be added to email group
        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )
        submission.delete(force=True, ignore_permissions=True)

    def test_submission_to_unpublished_form(self):
        # Given an rsvp form which is unpublished
        rsvp = self.rsvp
        rsvp.is_published = False
        rsvp.save()

        # When a user tries to create a submission
        # Then a validation error must be thrown

        frappe.set_user("Guest")
        with self.assertRaises(frappe.ValidationError):
            insert_rsvp_submission(linked_rsvp=rsvp.name)

    def test_email_group_is_not_duplicated(self):
        frappe.set_user("Guest")

        # First submission
        sub1 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            email="test@example.com",
            subscribe_chapter_mailing=1,
        )

        # Trigger again by second submission
        sub2 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            email="another@example.com",
            subscribe_chapter_mailing=1,
        )

        group_count = frappe.db.count(
            "Email Group",
            {
                "reference_document": self.event.name,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
        )

        # Only one email group should exist
        self.assertEqual(group_count, 1)
        sub1.delete(force=True, ignore_permissions=True)
        sub2.delete(force=True, ignore_permissions=True)

    def test_unsubscribe_from_email_group(self):
        frappe.set_user("Guest")

        # First subscribe
        submission = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            email="unsubscribe@example.com",
            subscribe_chapter_mailing=True,
        )

        # Confirm user is added
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": "unsubscribe@example.com", "email_group": self.email_group},
            )
        )

        # Unsubscribe
        frappe.set_user(CORE_TEAM)  # So user can update doc
        submission.subscribe_chapter_mailing = 0
        submission.save()

        # Confirm user is removed
        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {"email": "unsubscribe@example.com", "email_group": self.email_group},
            )
        )
        submission.delete(force=True, ignore_permissions=True)
