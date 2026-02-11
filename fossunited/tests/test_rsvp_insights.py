import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime

from fossunited.api.rsvp import (
    get_rsvp_checkin_stats,
    get_rsvp_checkins,
    get_submissions_with_answers,
    if_rsvp_show_checkins,
)
from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_RSVP,
    RSVP_RESPONSE,
    USER_PROFILE,
)
from fossunited.tests.utils import (
    insert_rsvp_form,
    insert_rsvp_submission,
    insert_test_chapter,
    insert_test_event,
)


class TestRSVPInsightsAPI(FrappeTestCase):
    """Test cases for RSVP insights API functions."""

    def setUp(self):
        self.core_team_email = "core1@example.com"
        self.other_chapter_core = "othercore@example.com"

        self.chapter = insert_test_chapter(members=[self.core_team_email])
        self.event = insert_test_event(
            chapter=self.chapter,
            event_start_date=add_days(now_datetime(), -1),
            event_end_date=add_days(now_datetime(), 3),
        )
        self.rsvp = insert_rsvp_form(self.event)

        self.other_chapter = insert_test_chapter(
            members=[self.other_chapter_core],
        )

        self._submissions = []

    def tearDown(self):
        frappe.set_user("Administrator")
        for sub in self._submissions:
            frappe.delete_doc(RSVP_RESPONSE, sub.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(CHAPTER, self.other_chapter.name, force=True)
        frappe.db.delete(USER_PROFILE, {"email": self.core_team_email})
        frappe.db.delete(CHAPTER_MEMBER, {"email": self.core_team_email})

    def test_get_submissions_guest_denied(self):
        """Guest users should not access RSVP submissions."""
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_submissions_with_answers(event_id=self.event.name)

    def test_get_submissions_other_chapter_core_denied(self):
        """Core members from other chapters should not access submissions."""
        frappe.set_user(self.other_chapter_core)
        with self.assertRaises(frappe.PermissionError):
            get_submissions_with_answers(event_id=self.event.name)

    def test_get_submissions_chapter_core_allowed(self):
        """Chapter core team should access submissions."""
        # Create a submission
        sub = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="John Doe",
            email="john@example.com",
            im_a="Student",
        )
        self._submissions.append(sub)

        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(event_id=self.event.name)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name1"], "John Doe")
        self.assertEqual(result[0]["email"], "john@example.com")

    def test_get_submissions_flattens_custom_fields(self):
        """Custom field answers should be flattened into submission dict."""
        sub = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Alice",
            email="alice@example.com",
            im_a="Professional",
            custom_answers=[
                {"question": "What's your goal?", "response": "Learn Frappe"},
                {"question": "Experience level?", "response": "Beginner"},
            ],
        )
        self._submissions.append(sub)

        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(event_id=self.event.name)

        self.assertEqual(len(result), 1)
        self.assertIn("What's your goal?", result[0])
        self.assertEqual(result[0]["What's your goal?"], "Learn Frappe")
        self.assertIn("Experience level?", result[0])
        self.assertEqual(result[0]["Experience level?"], "Beginner")

    def test_get_submissions_empty_response_handled(self):
        """Empty custom field responses should be stored as empty string."""
        sub = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Bob",
            email="bob@example.com",
            im_a="Student",
            custom_answers=[
                {"question": "Optional question?", "response": None},
            ],
        )
        self._submissions.append(sub)

        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(event_id=self.event.name)

        self.assertIn("Optional question?", result[0])
        self.assertEqual(result[0]["Optional question?"], "")

    def test_get_submissions_multiple_submissions(self):
        """Should return all submissions for the event."""
        sub1 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Alice",
            email="alice@example.com",
            im_a="Student",
        )
        sub2 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Bob",
            email="bob@example.com",
            im_a="Professional",
        )
        self._submissions.extend([sub1, sub2])

        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(event_id=self.event.name)

        self.assertEqual(len(result), 2)
        names = {r["name1"] for r in result}
        self.assertEqual(names, {"Alice", "Bob"})

    def test_get_checkins_guest_denied(self):
        """Guest users should not access check-ins."""
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_rsvp_checkins(event_id=self.event.name)

    def test_get_checkins_other_chapter_core_denied(self):
        """Core members from other chapters should not access check-ins."""
        frappe.set_user(self.other_chapter_core)
        with self.assertRaises(frappe.PermissionError):
            get_rsvp_checkins(event_id=self.event.name)

    def test_get_checkins_returns_accepted_attendees_only(self):
        """Should only return check-ins for accepted attendees."""
        # Accepted submission with check-in
        accepted_sub = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Checked In User",
            email="checkedin@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        accepted_sub.append("check_ins", {"check_in_time": now_datetime()})
        accepted_sub.save()

        # Rejected submission (should not appear)
        rejected_sub = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Rejected User",
            email="rejected@example.com",
            im_a="Student",
            status="Rejected",
            confirm_attendance=0,
        )

        self._submissions.extend([accepted_sub, rejected_sub])

        frappe.set_user(self.core_team_email)
        result = get_rsvp_checkins(event_id=self.event.name)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name1"], "Checked In User")
        self.assertEqual(result[0]["email"], "checkedin@example.com")
        self.assertIn("check_in_time", result[0])

    def test_get_checkins_ordered_by_time_desc(self):
        """Check-ins should be ordered by time (most recent first)."""
        sub1 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="First Check-in",
            email="first@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        sub1.append("check_ins", {"check_in_time": add_days(now_datetime(), -2)})
        sub1.save()

        sub2 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Recent Check-in",
            email="recent@example.com",
            im_a="Professional",
            status="Accepted",
            confirm_attendance=1,
        )
        sub2.append("check_ins", {"check_in_time": now_datetime()})
        sub2.save()

        self._submissions.extend([sub1, sub2])

        frappe.set_user(self.core_team_email)
        result = get_rsvp_checkins(event_id=self.event.name)

        # Most recent should be first
        self.assertEqual(result[0]["name1"], "Recent Check-in")
        self.assertEqual(result[1]["name1"], "First Check-in")

    def test_show_checkins_returns_true_for_started_event(self):
        """Should return True if event has started."""
        frappe.set_user(self.core_team_email)
        result = if_rsvp_show_checkins(event_id=self.event.name)
        self.assertTrue(result)

    def test_get_stats_guest_denied(self):
        """Guest users should not access stats."""
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_rsvp_checkin_stats(event_id=self.event.name)

    def test_get_stats_counts_accepted_confirmed_only(self):
        """Should only count accepted submissions with confirmed attendance."""
        # Accepted + Confirmed
        accepted1 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Accepted 1",
            email="a1@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=1,
        )
        accepted2 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Accepted 2",
            email="a2@example.com",
            im_a="Professional",
            status="Accepted",
            confirm_attendance=1,
        )

        # Accepted but not confirmed (should not count)
        not_confirmed = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Not Confirmed",
            email="nc@example.com",
            im_a="Student",
            status="Accepted",
            confirm_attendance=0,
        )

        self._submissions.extend([accepted1, accepted2, not_confirmed])

        frappe.set_user(self.core_team_email)
        result = get_rsvp_checkin_stats(event_id=self.event.name)
        self.assertEqual(result["total_accepted"], 2)

    def test_get_stats_returns_zero_for_no_submissions(self):
        """Should return 0 when no accepted submissions exist."""
        frappe.set_user(self.core_team_email)
        result = get_rsvp_checkin_stats(event_id=self.event.name)
        self.assertEqual(result["total_accepted"], 0)
