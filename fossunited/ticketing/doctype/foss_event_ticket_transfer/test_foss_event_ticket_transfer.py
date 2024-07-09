# Copyright (c) 2024, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFOSSEventTicketTransfer(FrappeTestCase):
    def test_ticket_transfer(self):
        # Given for an event, a ticket is created. For that ticket, a transfer is generated.
        event = frappe.get_doc(
            {
                "doctype": "FOSS Chapter Event",
                "event_name": "Test Event",
                "event_permalink": "test_perma",
                "status": "Approved",
                "event_type": "Conference",
                "event_start_date": datetime.today(),
                "event_end_date": datetime.today() + timedelta(1),
                "event_description": "testing",
            }
        )
        event.insert()

        ticket = frappe.get_doc(
            {
                "doctype": "FOSS Event Ticket",
                "event": event.name,
                "full_name": "Harsh Tandiya",
                "email": "harsh@test.xyz",
            }
        )
        ticket.insert()

        transfer = frappe.get_doc(
            {
                "doctype": "FOSS Event Ticket Transfer",
                "ticket": ticket.name,
                "receiver_name": "Rahul",
                "receiver_email": "rahul@test.xyz",
            }
        )
        transfer.insert()

        # When Ticket Transfer is created, status should be pending
        self.assertEqual(transfer.status, "Pending Approval")

        # Change status of transfer to completed
        transfer.status = "Completed"
        transfer.save()
        self.assertEqual(transfer.status, "Completed")

        # Then check that a ticket with older credentials does not exists.
        # Also check that ticket has new details.
        old_ticket_exists = frappe.db.exists(
            "FOSS Event Ticket",
            {
                "email": "harsh@test.xyz",
                "full_name": "Harsh Tandiya",
                "event": event.name,
            },
        )
        self.assertFalse(old_ticket_exists)

        new_ticket_exists = frappe.db.exists(
            "FOSS Event Ticket",
            {
                "email": "rahul@test.xyz",
                "full_name": "Rahul",
                "event": event.name,
            },
        )
        self.assertTrue(new_ticket_exists)

        transfer.delete()
        ticket.delete()
        event.delete()
