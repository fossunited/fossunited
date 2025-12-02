import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.chapter import get_submissions_with_answers
from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_RSVP,
    RSVP_RESPONSE,
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
        self.volunteer_user = "volunteer1@example.com"
        self.chapter = insert_test_chapter(
            members=[self.core_team_email, self.volunteer_user],
        )
        self.event = insert_test_event(self.chapter)
        self.rsvp = insert_rsvp_form(self.event)
        # Create one submission with a custom question
        self.submission = insert_rsvp_submission(
            linked_rsvp=self.rsvp.name,
            name="Alice",
            email="alicewonderland@example.com",
            im_a="Student",
            custom_answers=[
                {
                    "question": "What’s your goal?",
                    "response": "To become the king of the pirates and greatest swordsmen.",
                }
            ],
        )
        self._extra_responses = []

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

    def test_event_core_team_full_email(self):
        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(self.event.name)
        self.assertTrue(result)
        self.assertIn("@", result[0]["email"])
        self.assertEqual(result[0]["email"], "alicewonderland@example.com")

    def test_event_core_team_gets_full_answers(self):
        frappe.set_user(self.core_team_email)
        result = get_submissions_with_answers(self.event.name)
        self.assertIn("What’s your goal?", result[0])
        self.assertEqual(
            result[0]["What’s your goal?"],
            "To become the king of the pirates and greatest swordsmen.",
        )

    def test_custom_field(self):
        # Simulate a user who is part of the chapter (member)
        frappe.set_user(self.core_team_email)

        result = get_submissions_with_answers(self.event.name)
        for submission in result:
            self.assertIn("name1", submission)
            self.assertIn("email", submission)
            self.assertIn("im_a", submission)
            self.assertIn("What’s your goal?", submission)
