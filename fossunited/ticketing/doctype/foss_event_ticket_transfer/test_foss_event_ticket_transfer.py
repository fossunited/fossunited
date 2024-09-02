# Copyright (c) 2024, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase


class TestFOSSEventTicketTransfer(FrappeTestCase):
    def setUp(self):
        fake = Faker()

        event = frappe.get_doc(
            {
                "doctype": "FOSS Chapter Event",
                "event_name": fake.text(max_nb_chars=20),
                "event_permalink": fake.slug(3).replace("-", "_"),
                "status": "Approved",
                "event_type": "Conference",
                "event_start_date": datetime.today(),
                "event_end_date": datetime.today() + timedelta(1),
                "event_description": "testing",
            }
        )
        event.insert()

        self.event = event

    def tearDown(self):
        frappe.delete_doc("FOSS Chapter Event", self.event.name, force=True)

    def test_ticket_transfer(self):
        fake = Faker()

        sender = {
            "full_name": fake.name(),
            "email": fake.email(),
        }

        recipient = {
            "full_name": fake.name(),
            "email": fake.email(),
        }

        # Given for an event, a ticket is created. For that ticket, a transfer is generated.
        ticket = frappe.get_doc(
            {
                "doctype": "FOSS Event Ticket",
                "event": self.event.name,
                "full_name": sender["full_name"],
                "email": sender["email"],
            }
        )
        ticket.insert()

        transfer = frappe.get_doc(
            {
                "doctype": "FOSS Event Ticket Transfer",
                "ticket": ticket.name,
                "receiver_name": recipient["full_name"],
                "receiver_email": recipient["email"],
            }
        )
        transfer.insert()

        # When Ticket Transfer is created, status should be pending
        self.assertEqual(transfer.status, "Pending Approval")

        # Change status of transfer to completed
        transfer.status = "Completed"
        transfer.save()

        # Then check that a ticket with older credentials does not exists.
        # Also check that ticket has new details.
        old_ticket_exists = frappe.db.exists(
            "FOSS Event Ticket",
            {
                "email": sender["email"],
                "full_name": sender["full_name"],
                "event": self.event.name,
            },
        )
        self.assertFalse(old_ticket_exists)

        new_ticket_exists = frappe.db.exists(
            "FOSS Event Ticket",
            {
                "email": recipient["email"],
                "full_name": recipient["full_name"],
                "event": self.event.name,
            },
        )
        self.assertTrue(new_ticket_exists)

    def test_status_pending_on_create(self):
        fake = Faker()
        # Given an event and a ticket linked to the event
        # With a ticket created for a user, try to transfer this ticket to another user while passing "Completed" as the status
        ticket = frappe.get_doc(
            {
                "doctype": "FOSS Event Ticket",
                "event": self.event.name,
                "full_name": fake.name(),
                "email": fake.email(),
            }
        )
        ticket.insert()

        # Then verify that this operation raises a ValidationError
        with self.assertRaises(frappe.exceptions.ValidationError):
            transfer = frappe.get_doc(
                {
                    "doctype": "FOSS Event Ticket Transfer",
                    "ticket": ticket.name,
                    "receiver_name": fake.name(),
                    "receiver_email": fake.email(),
                    "status": "Completed",
                }
            )
            transfer.insert()
