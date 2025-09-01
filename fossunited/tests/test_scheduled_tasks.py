from datetime import datetime, timedelta
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_CFP, EVENT_RSVP
from fossunited.scheduled_tasks import conclude_events

from .utils import (
    insert_cfp_form,
    insert_rsvp_form,
    insert_test_chapter,
    insert_test_event,
)


class TestScheduledTasks(FrappeTestCase):
    def setUp(self):
        today = datetime.today()
        self.chapter = insert_test_chapter()

        # Event 1 is live and is to end tomorrow
        self.event1 = insert_test_event(
            chapter=self.chapter,
            start_date=today.replace(hour=9, minute=00),
            end_date=today.replace(hour=15, minute=30),
        )

        self.event1_cfp = insert_cfp_form(event=self.event1.name, status="Live")
        self.event1_rsvp = insert_rsvp_form(event=self.event1.name, is_published=1)

        # Event 2 is cancelled, and was supposed to end tomorrow
        self.event2 = insert_test_event(
            chapter=self.chapter,
            status="Cancelled",
            start_date=today.replace(hour=9, minute=00),
            end_date=today.replace(hour=15, minute=30),
        )
        self.event2_cfp = insert_cfp_form(event=self.event2.name, status="Live")
        self.event2_rsvp = insert_rsvp_form(event=self.event2.name, is_published=1)

        # Event 3 starts tomorrow, and ends the day-after tomorrow
        self.event3 = insert_test_event(
            chapter=self.chapter,
            start_date=today.replace(hour=9, minute=00) + timedelta(days=1),
            end_date=today.replace(hour=14, minute=00) + timedelta(days=2),
        )
        self.event3_cfp = insert_cfp_form(event=self.event3.name, status="Live")
        self.event3_rsvp = insert_rsvp_form(event=self.event3.name, is_published=1)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT_CFP, self.event1_cfp.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.event1_rsvp.name, force=True)
        frappe.delete_doc(EVENT, self.event1.name, force=True)
        frappe.delete_doc(EVENT, self.event2.name, force=True)
        frappe.delete_doc(EVENT, self.event3.name, force=True)

    # Only patching the datetime within the `scheduled_tasks` module
    @patch("fossunited.scheduled_tasks.datetime")
    def test_concluded_events(self, mock_datetime):
        # Set the mock datetime to return a specific date
        mock_datetime.today.return_value = datetime.today().replace(hour=00, minute=1) + timedelta(
            days=1
        )
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Call the function to test
        conclude_events()

        # Fetch events to check their status
        self.event1.reload()
        self.event1_cfp.reload()
        self.event1_rsvp.reload()
        self.event2.reload()
        self.event2_cfp.reload()
        self.event2_rsvp.reload()
        self.event3.reload()
        self.event3_cfp.reload()
        self.event3_rsvp.reload()

        # First event should change the status to concluded
        self.assertEqual(self.event1.status, "Concluded")
        self.assertEqual(self.event1_cfp.status, "Closed")
        self.assertEqual(self.event1_rsvp.is_published, 0)

        # Second event should not change it's status, since it was cancelled
        self.assertEqual(self.event2.status, "Cancelled")
        self.assertEqual(self.event2_cfp.status, "Closed")
        self.assertEqual(self.event2_rsvp.is_published, 0)

        # Third event is still live, since its end_date > mock date set here
        self.assertEqual(self.event3.status, "Live")
        self.assertEqual(self.event3_cfp.status, "Live")
        self.assertEqual(self.event3_rsvp.is_published, 1)
