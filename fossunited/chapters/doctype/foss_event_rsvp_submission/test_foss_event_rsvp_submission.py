# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase


class TestFOSSEventRSVPSubmission(FrappeTestCase):
    def test_unpublish_on_max_count(self):
        # Given an RSVP with max count of 5
        event = frappe.get_doc(
            {
                "doctype": "FOSS Chapter Event",
                "event_name": "_Test_Event",
                "event_permalink": "test-event-12345",
                "status": "Live",
                "event_type": "FOSS Meetup",
                "event_start_date": datetime.today(),
                "event_end_date": datetime.today() + timedelta(1),
                "event_description": "testing",
            }
        )
        event.insert()

        rsvp = frappe.get_doc(
            {
                "doctype": "FOSS Event RSVP",
                "max_rsvp_count": 5,
                "event": event.name,
            }
        )
        rsvp.insert()

        # When submission count reaches the max count
        fake = Faker()
        for i in range(5):
            frappe.get_doc(
                {
                    "doctype": "FOSS Event RSVP Submission",
                    "linked_rsvp": rsvp.name,
                    "event": rsvp.event,
                    "name1": fake.name(),
                    "email": fake.email(),
                    "im_a": "Student",
                }
            ).insert()

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(
            "FOSS Event RSVP", rsvp.name, "is_published"
        )
        self.assertFalse(is_published)
