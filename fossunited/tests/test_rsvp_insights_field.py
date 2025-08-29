import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.chapter import get_submissions_with_answers
from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_RSVP,
    RSVP_RESPONSE,
    USER_PROFILE,
)

from .utils import (
    insert_rsvp_form,
    insert_rsvp_submission,
    insert_test_chapter,
    insert_test_event,
)


class TestGetSubmissionsWithAnswersAPI(FrappeTestCase):
    def setUp(self):
        # Create a chapter → event → RSVP form
        self.core_team_email = "test1@example.com"
        self.volunteer_user = "volunteer@example.com"
        self.chapter = insert_test_chapter(
            members=[self.core_team_email, self.volunteer_user],
        )
        self.event = insert_test_event(self.chapter)
        self.rsvp = insert_rsvp_form(self.event)
        # Create one submission with a custom question
        self.submission = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Alice",
            email="alice@example.com",
            im_a="Student",
            custom_answers=[{"question": "What’s your goal?", "response": "To learn"}],
        )
        self._extra_responses = []

        # After insert_test_chapter is called
        self.event.reload()
        for member in self.event.event_members:
            if frappe.db.get_value(USER_PROFILE, member.member, "user") == self.volunteer_user:
                member.role = "Volunteer"

        self.event.save(ignore_permissions=True)
        self.event.reload()

    def tearDown(self):
        frappe.set_user("Administrator")
        # Delete children first, then parents
        for name in self._extra_responses:
            frappe.delete_doc(RSVP_RESPONSE, name, force=True)
        frappe.delete_doc(RSVP_RESPONSE, self.submission.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def test_guest_user_denied(self):
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_submissions_with_answers(self.event.name)

    def test_non_event_core_team_masks_email(self):
        frappe.set_user(self.volunteer_user)
        result = get_submissions_with_answers(self.event.name, full=False)
        self.assertTrue(result)
        # Check email is masked: basic pattern check
        self.assertIn("@", result[0]["email"])
        self.assertNotEqual(result[0]["email"], "alice@example.com")

    def test_event_core_team_full_email(self):
        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(self.event.name, full=False)
        self.assertTrue(result)
        self.assertIn("@", result[0]["email"])
        self.assertEqual(result[0]["email"], "alice@example.com")

    def test_event_core_team_gets_full_answers(self):
        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(self.event.name, full=True)
        self.assertIn("cf_whats_your_goal", result[0])
        self.assertEqual(result[0]["cf_whats_your_goal"], "To learn")
        self.assertEqual(result[0]["_answers"]["cf_whats_your_goal"], "What’s your goal?")

    def test_truncation_when_full_false(self):
        frappe.set_user(self.core_team_email)
        # Use long question/response to test truncation
        long_q = "Q" * 100
        long_r = "R" * 100
        # Create another submission
        _bob = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Bob",
            email="bob@example.com",
            custom_answers=[{"question": long_q, "response": long_r}],
        )
        result = get_submissions_with_answers(self.event.name, full=False)
        for s in result:
            for key, val in s.items():
                if key.startswith("cf_"):
                    self.assertLessEqual(len(val), 52)

    def test_no_truncation_when_full_true(self):
        frappe.set_user(self.core_team_email)
        question = "What do you bring?"
        response = "Experience and energy."
        _charlie = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Charlie",
            email="charlie@example.com",
            custom_answers=[{"question": question, "response": response}],
        )
        self._extra_responses.append(_charlie.name)

        result = get_submissions_with_answers(self.event.name, full=True)
        found = False
        for s in result:
            if s.get("email") == "charlie@example.com":
                found = True
                self.assertEqual(s["cf_what_do_you_bring"], response)
                self.assertEqual(s["_answers"]["cf_what_do_you_bring"], question)
        self.assertTrue(found, "Charlie submission not found in results")

    def test_non_core_basic_fields(self):
        # Simulate a user who is part of the chapter (member) but not the core member
        frappe.set_user(self.volunteer_user)

        # Add another submission with custom fields
        _bob2 = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Bob",
            email="bob@example.com",
            im_a="Student",
            custom_answers=[{"question": "Why are you attending?", "response": "To network"}],
        )
        self._extra_responses.append(_bob2.name)

        result = get_submissions_with_answers(self.event.name)
        for submission in result:
            self.assertIn("name1", submission)
            self.assertIn("email", submission)
            self.assertIn("im_a", submission)

            # Ensure no custom fields (starting with 'cf_') are present
            for key in submission.keys():
                self.assertFalse(
                    key.startswith("cf_"),
                    f"Non-core_team should not see custom field: {key}",
                )
            self.assertNotIn("_answers", submission, "Non-core_team should not see _answers")
