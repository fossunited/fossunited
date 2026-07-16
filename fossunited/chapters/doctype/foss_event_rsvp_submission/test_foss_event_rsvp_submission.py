import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate

from fossunited.doctype_ids import EVENT, EVENT_RSVP
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.foss_event_rsvp_factory import FOSSEventRSVPFactory
from fossunited.tests.factories.foss_event_rsvp_submission_factory import (
    FOSSEventRSVPSubmissionFactory,
)
from fossunited.tests.factories.user_factory import UserFactory

fake = Faker()


class TestFOSSEventRSVPSubmission(FrappeTestCase):
    def setUp(self):
        self.core_team_user = UserFactory.create("with_foss_website_user_role")
        self.website_user = UserFactory.create("with_foss_website_user_role")

        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.core_team_user.name]
        )
        self.event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            event_start_date=add_days(nowdate(), -1),
            event_end_date=add_days(nowdate(), 1),
        )
        self.rsvp = FOSSEventRSVPFactory.create(event=self.event.name)
        self.email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.rsvp.event,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
        )

    def test_rsvp_is_full_on_max_count(self):
        rsvp = self.rsvp

        emails = set()
        while len(emails) < int(rsvp.max_rsvp_count):
            emails.add(fake.email())

        for email in emails:
            FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name, email=email)

        rsvp.reload()
        self.assertTrue(rsvp.is_full())
        self.assertTrue(frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published"))

    def test_submission_blocked_when_rsvp_full(self):
        rsvp = self.rsvp

        emails = set()
        while len(emails) < int(rsvp.max_rsvp_count):
            emails.add(fake.email())

        for email in emails:
            FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name, email=email)

        with self.assertRaises(frappe.ValidationError):
            FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name, email=fake.email())

    def test_add_to_email_group(self):
        with self.set_user("Guest"):
            FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=self.rsvp.name,
                email=self.website_user.name,
                subscribe_chapter_mailing=1,
                confirm_attendance=1,
                status="Accepted",
            )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": self.website_user.name, "email_group": self.email_group},
            )
        )

    def test_acceptance_workflow(self):
        rsvp = self.rsvp

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name)

        self.assertEqual(submission.status, "Accepted")

    def test_pending_workflow(self):
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=rsvp.name, status="Pending"
            )

        self.assertEqual(submission.status, "Pending")

    def test_pending_to_acceptance_workflow(self):
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=rsvp.name, status="Pending"
            )
        self.assertEqual(submission.status, "Pending")

        with self.set_user(self.core_team_user.name):
            submission.status = "Accepted"
            submission.save()

    def test_invalid_status_at_creation(self):
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        with self.set_user("Guest"), self.assertRaises(frappe.PermissionError):
            FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name, status="Accepted")

    def test_status_change_after_unpublish(self):
        with self.set_user(self.core_team_user.name):
            rsvp = self.rsvp
            rsvp.requires_host_approval = True
            rsvp.save()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=rsvp.name, status="Pending"
            )

        self.assertEqual(submission.status, "Pending")

        with self.set_user(self.core_team_user.name):
            rsvp.is_published = False
            rsvp.save()

            submission.status = "Rejected"
            submission.save()

    def test_add_to_email_on_acceptance(self):
        with self.set_user(self.core_team_user.name):
            rsvp = self.rsvp
            rsvp.requires_host_approval = True
            rsvp.save()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=rsvp.name, status="Pending"
            )
        self.assertEqual(submission.status, "Pending")

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        with self.set_user(self.core_team_user.name):
            submission.status = "Accepted"
            submission.subscribe_chapter_mailing = 1
            submission.confirm_attendance = 1
            submission.save()

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

    def test_no_add_to_email_on_rejection(self):
        with self.set_user(self.core_team_user.name):
            rsvp = self.rsvp
            rsvp.requires_host_approval = True
            rsvp.save()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=rsvp.name, status="Pending"
            )
        self.assertEqual(submission.status, "Pending")

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        with self.set_user(self.core_team_user.name):
            submission.status = "Rejected"
            submission.save()

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

    def test_submission_to_unpublished_form(self):
        rsvp = self.rsvp
        rsvp.is_published = False
        rsvp.save()

        with self.set_user("Guest"), self.assertRaises(frappe.ValidationError):
            FOSSEventRSVPSubmissionFactory.create(linked_rsvp=rsvp.name)

    def test_email_group_is_not_duplicated(self):
        with self.set_user("Guest"):
            FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=self.rsvp.name,
                email=fake.unique.email(),
                subscribe_chapter_mailing=1,
            )

            FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=self.rsvp.name,
                email=fake.unique.email(),
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

        self.assertEqual(group_count, 1)

    def test_unsubscribe_from_email_group(self):
        subscriber_email = fake.unique.email()

        with self.set_user("Guest"):
            submission = FOSSEventRSVPSubmissionFactory.create(
                linked_rsvp=self.rsvp.name,
                email=subscriber_email,
                subscribe_chapter_mailing=1,
                confirm_attendance=1,
            )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": subscriber_email, "email_group": self.email_group},
            )
        )

        with self.set_user(self.core_team_user.name):
            submission.subscribe_chapter_mailing = 0
            submission.confirm_attendance = 0
            submission.save()

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {"email": subscriber_email, "email_group": self.email_group},
            )
        )

    def test_successful_checkin(self):
        with self.set_user(self.core_team_user.name):
            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=self.rsvp.name)

            submission.add_check_in()

            self.assertEqual(len(submission.check_ins), 1)
            self.assertTrue(submission.has_checked_in_today())

    def test_double_checkin_same_day_fails(self):
        with self.set_user(self.core_team_user.name):
            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=self.rsvp.name)

            submission.add_check_in()

            with self.assertRaises(frappe.ValidationError):
                submission.add_check_in()

    def test_checkin_outside_event_dates_fails(self):
        with self.set_user(self.core_team_user.name):
            event = frappe.get_doc(EVENT, self.event.name)
            event.event_start_date = add_days(nowdate(), -10)
            event.event_end_date = add_days(nowdate(), -5)
            event.save()

            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=self.rsvp.name)

            with self.assertRaises(frappe.ValidationError):
                submission.add_check_in()

    def test_has_checked_in_today_initially_false(self):
        with self.set_user(self.core_team_user.name):
            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=self.rsvp.name)

            self.assertFalse(submission.has_checked_in_today())

    def test_can_check_in_only_during_event_days(self):
        with self.set_user(self.core_team_user.name):
            submission = FOSSEventRSVPSubmissionFactory.create(linked_rsvp=self.rsvp.name)

            event = frappe.get_doc(EVENT, self.event.name)
            event.event_start_date = add_days(nowdate(), 1)
            event.event_end_date = add_days(nowdate(), 2)
            event.save()

            self.assertFalse(submission.can_check_in(event.event_start_date, event.event_end_date))

            event = frappe.get_doc(EVENT, self.event.name)
            event.event_start_date = add_days(nowdate(), -1)
            event.event_end_date = add_days(nowdate(), 1)
            event.save()

            self.assertTrue(submission.can_check_in(event.event_start_date, event.event_end_date))
