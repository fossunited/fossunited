# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import EVENT, EVENT_RSVP, RSVP_RESPONSE

fake = Faker()

class TestFOSSEventRSVPSubmission(IntegrationTestCase):
    def test_unpublish_on_max_count(self):
        # Given an RSVP with max count of 5
        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "event_name": fake.name(),
                "event_permalink": fake.slug(),
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
                "doctype": EVENT_RSVP,
                "max_rsvp_count": 5,
                "event": event.name,
            }
        )
        rsvp.insert()

        # When submission count reaches the max count
        for i in range(5):
            frappe.get_doc(
                {
                    "doctype": RSVP_RESPONSE,
                    "linked_rsvp": rsvp.name,
                    "event": rsvp.event,
                    "name1": fake.name(),
                    "email": fake.email(),
                    "im_a": "Student",
                }
            ).insert()

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published")
        self.assertFalse(is_published)
