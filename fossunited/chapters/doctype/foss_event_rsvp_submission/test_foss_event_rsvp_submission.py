# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase


def create_event(event_type: str = "FOSS Meetup"):
    if frappe.flags.test_event_created:
        return

    event = frappe.get_doc(
        {
            "doctype": "FOSS Chapter Event",
            "event_name": "_Test_Event",
            "event_permalink": "test-event-1234",
            "status": "Live",
            "event_type": event_type,
            "event_start_date": datetime.today(),
            "event_end_date": datetime.today() + timedelta(1),
            "event_description": "testing",
        }
    )
    event.insert()

    frappe.flags.test_event_created = True


class TestFOSSEventRSVPSubmission(FrappeTestCase):
    def setUp(self):
        create_event
        self.create_rsvp()

    def tearDown(self):
        frappe.set_user("Administrator")

    def create_rsvp(self):
        if frappe.flags.test_rsvp_created:
            return

        if not frappe.flags.test_event_created:
            create_event()

        event = frappe.db.get_value(
            "FOSS Chapter Event",
            {"event_name": "_Test_Event"},
            "name",
        )

        rsvp = frappe.get_doc(
            {
                "doctype": "FOSS Event RSVP",
                "event": event,
                "max_rsvp_count": 5,
            }
        )
        rsvp.insert()

        self.test_rsvp_id = rsvp.name
        frappe.flags.test_rsvp_created = True

    def test_submission_on_unpublished_rsvp(self):
        # Given an RSVP which is not published
        rsvp = frappe.get_doc(
            {
                "doctype": "FOSS Event RSVP",
                "max_rsvp_count": 5,
                "is_published": False,
            }
        )
        rsvp.insert()

        # When a submission is made for this RSVP
        # Then it should throw an error

        fake = Faker()
        with self.assertRaises(frappe.exceptions.ValidationError):
            submission = frappe.get_doc(
                {
                    "doctype": "FOSS Event RSVP Submission",
                    "linked_rsvp": rsvp.name,
                    "name1": fake.name(),
                    "email": fake.email(),
                    "im_a": "Professional",
                }
            )
            submission.insert()
