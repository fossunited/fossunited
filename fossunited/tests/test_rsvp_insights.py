import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime

from fossunited.api.rsvp import (
    get_rsvp_checkin_stats,
    get_rsvp_checkins,
    get_submissions_with_answers,
    if_rsvp_show_checkins,
)
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.foss_event_rsvp_factory import FOSSEventRSVPFactory
from fossunited.tests.factories.foss_event_rsvp_submission_factory import (
    FOSSEventRSVPSubmissionFactory,
)
from fossunited.tests.factories.user_factory import UserFactory


class TestRSVPInsightsAPI(FrappeTestCase):
    """Test cases for RSVP insights API functions."""

    def setUp(self):
        self.core_team_user = UserFactory.create("with_foss_website_user_role")
        self.other_chapter_core_user = UserFactory.create("with_foss_website_user_role")

        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.core_team_user.name]
        )
        self.event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            event_start_date=add_days(now_datetime(), -1),
            event_end_date=add_days(now_datetime(), 3),
        )
        self.rsvp = FOSSEventRSVPFactory.create(event=self.event.name)

        self.other_chapter = FOSSChapterFactory.create(
            "with_members", members=[self.other_chapter_core_user.name]
        )

    def test_get_submissions_guest_denied(self):
        with self.set_user("Guest"), self.assertRaises(frappe.PermissionError):
            get_submissions_with_answers(event_id=self.event.name)

    def test_get_submissions_other_chapter_core_denied(self):
        with (
            self.set_user(self.other_chapter_core_user.name),
            self.assertRaises(frappe.PermissionError),
        ):
            get_submissions_with_answers(event_id=self.event.name)

    def test_get_submissions_chapter_core_allowed(self):
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="John Doe",
            email="john@example.com",
            im_a="Student",
            status="Pending",
        )

        with self.set_user(self.core_team_user.name):
            result = get_submissions_with_answers(event_id=self.event.name)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name1"], "John Doe")
        self.assertEqual(result[0]["email"], "john@example.com")

    def test_get_submissions_flattens_custom_fields(self):
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Alice",
            email="alice@example.com",
            im_a="Professional",
            status="Pending",
            custom_answers=[
                {"question": "What's your goal?", "response": "Learn Frappe"},
                {"question": "Experience level?", "response": "Beginner"},
            ],
        )

        with self.set_user(self.core_team_user.name):
            result = get_submissions_with_answers(event_id=self.event.name)

        self.assertEqual(len(result), 1)
        self.assertIn("What's your goal?", result[0])
        self.assertEqual(result[0]["What's your goal?"], "Learn Frappe")
        self.assertIn("Experience level?", result[0])
        self.assertEqual(result[0]["Experience level?"], "Beginner")

    def test_get_submissions_empty_response_handled(self):
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Bob",
            email="bob@example.com",
            im_a="Student",
            status="Pending",
            custom_answers=[
                {"question": "Optional question?", "response": None},
            ],
        )

        with self.set_user(self.core_team_user.name):
            result = get_submissions_with_answers(event_id=self.event.name)

        self.assertIn("Optional question?", result[0])
        self.assertEqual(result[0]["Optional question?"], "")

    def test_get_submissions_multiple_submissions(self):
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Alice",
            email="alice@example.com",
            im_a="Student",
            status="Pending",
        )
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Bob",
            email="bob@example.com",
            im_a="Professional",
            status="Pending",
        )

        with self.set_user(self.core_team_user.name):
            result = get_submissions_with_answers(event_id=self.event.name)

        self.assertEqual(len(result), 2)
        names = {r["name1"] for r in result}
        self.assertEqual(names, {"Alice", "Bob"})

    def test_get_checkins_guest_denied(self):
        with self.set_user("Guest"), self.assertRaises(frappe.PermissionError):
            get_rsvp_checkins(event_id=self.event.name)

    def test_get_checkins_other_chapter_core_denied(self):
        with (
            self.set_user(self.other_chapter_core_user.name),
            self.assertRaises(frappe.PermissionError),
        ):
            get_rsvp_checkins(event_id=self.event.name)

    def test_get_checkins_returns_accepted_attendees_only(self):
        accepted_sub = FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Checked In User",
            email="checkedin@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        accepted_sub.append("check_ins", {"check_in_time": now_datetime()})
        accepted_sub.save()

        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Rejected User",
            email="rejected@example.com",
            im_a="Student",
            status="Rejected",
            confirm_attendance=0,
        )

        with self.set_user(self.core_team_user.name):
            result = get_rsvp_checkins(event_id=self.event.name)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name1"], "Checked In User")
        self.assertEqual(result[0]["email"], "checkedin@example.com")
        self.assertIn("check_in_time", result[0])

    def test_get_checkins_ordered_by_time_desc(self):
        sub1 = FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="First Check-in",
            email="first@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        sub1.append("check_ins", {"check_in_time": add_days(now_datetime(), -2)})
        sub1.save()

        sub2 = FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Recent Check-in",
            email="recent@example.com",
            im_a="Professional",
            status="Accepted",
            confirm_attendance=1,
        )
        sub2.append("check_ins", {"check_in_time": now_datetime()})
        sub2.save()

        with self.set_user(self.core_team_user.name):
            result = get_rsvp_checkins(event_id=self.event.name)

        self.assertEqual(result[0]["name1"], "Recent Check-in")
        self.assertEqual(result[1]["name1"], "First Check-in")

    def test_show_checkins_returns_true_for_started_event(self):
        with self.set_user(self.core_team_user.name):
            result = if_rsvp_show_checkins(event_id=self.event.name)
        self.assertTrue(result)

    def test_get_stats_guest_denied(self):
        with self.set_user("Guest"), self.assertRaises(frappe.PermissionError):
            get_rsvp_checkin_stats(event_id=self.event.name)

    def test_get_stats_counts_accepted_confirmed_only(self):
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Accepted 1",
            email="a1@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Accepted 2",
            email="a2@example.com",
            im_a="Professional",
            status="Accepted",
            confirm_attendance=1,
        )
        FOSSEventRSVPSubmissionFactory.create(
            linked_rsvp=self.rsvp.name,
            name1="Not Confirmed",
            email="nc@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=0,
        )

        with self.set_user(self.core_team_user.name):
            result = get_rsvp_checkin_stats(event_id=self.event.name)
        self.assertEqual(result["total_accepted"], 2)

    def test_get_stats_returns_zero_for_no_submissions(self):
        with self.set_user(self.core_team_user.name):
            result = get_rsvp_checkin_stats(event_id=self.event.name)
        self.assertEqual(result["total_accepted"], 0)
