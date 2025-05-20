import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import EVENT, EVENT_TICKET, RAZORPAY_PAYMENT, TICKET_TIER
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_event,
    insert_test_razorpay_payment,
)
from fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket import (
    TicketTierMismatchError,
)

fake = Faker()


class TestRazorpayPayment(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(
            chapter=self.chapter,
            is_paid_event=1,
            tickets_status="Live",
            tiers=[
                {
                    "enabled": 1,
                    "title": "Test",
                    "price": 100,
                    "maximum_tickets": 5,
                }
            ],
        )

    def tearDown(self):
        frappe.set_user("Administrator")

        # Delete any created Razorpay Payment documents
        payments = frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event})
        for payment in payments:
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)

        tickets = frappe.get_all(EVENT_TICKET, {"event": self.event})
        for ticket in tickets:
            frappe.delete_doc(EVENT_TICKET, ticket.name)

        self.chapter.delete(force=True)
        self.event.delete(force=True)

    def test_payment_creation(self):
        # Given, as administrator
        frappe.set_user("Administrator")
        # When a payment doctype is created
        # Then it should be created without any errors
        payment = insert_test_razorpay_payment(event=self.event.name)
        self.assertTrue(payment)
        payment.delete(force=True)

        # When a non system user tries to create a payment,
        # Then it should throw error
        frappe.set_user("test1@example.com")
        with self.assertRaises(frappe.PermissionError):
            insert_test_razorpay_payment(event=self.event.name)

    def test_ticket_creation_on_capture(self):
        # Given a paid event
        # When a payment doctype linked to this event is created
        payment = insert_test_razorpay_payment(event=self.event.name)
        self.assertTrue(payment)
        # Then the payment's status should be Pending
        self.assertEqual(payment.status, "Pending")
        # And there should be no ticket linked to this payment doctype
        self.assertIsNone(frappe.db.exists(EVENT_TICKET, {"razorpay_payment": payment.name}))

        # When the payment status is changed to "Captured"
        payment.status = "Captured"
        payment.save()
        payment.reload()

        # Then a ticket should be created
        self.assertIsNotNone(frappe.db.exists(EVENT_TICKET, {"razorpay_payment": payment.name}))

    def test_multiple_ticket_creation_on_capture(self):
        # Given a event ticket payment with multiple participants
        number_of_attendees = 3
        payment = insert_test_razorpay_payment(
            event=self.event.name, attendees=[], num_seats=number_of_attendees
        )
        # The initial status should be `Pending`
        self.assertEqual(payment.status, "Pending")
        # And there should be no tickets linked to this payment
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), 0)

        # When the status for the payment is changed to "Captured"
        payment.status = "Captured"
        payment.save()

        # Then tickets equal to `number_of_attendees` count should be created
        # which are linked to this payment
        self.assertEqual(
            frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), number_of_attendees
        )

    def test_payment_creation_on_closed_tickets(self):
        # Given an event with tickets closed
        self.event.tickets_status = "Closed"
        self.event.save()
        self.event.reload()

        # When a payment linked to this event is created
        # Then it should throw an error before it is created
        with self.assertRaises(frappe.PermissionError):
            insert_test_razorpay_payment(event=self.event.name)

    def test_event_ticket_tier_mismatch(self):
        event_1 = self.event
        event_2 = insert_test_event(
            chapter=self.chapter,
            is_paid_event=1,
            tiers=[
                {
                    "enabled": 1,
                    "title": "Faulty",
                    "price": 5,
                    "maximum_tickets": 5,
                }
            ],
            tickets_status="Live",
        )

        event_2_tier = frappe.get_doc(TICKET_TIER, {"parent": event_2.name, "parenttype": EVENT})

        # create a payment for event_1 but with event_2 tier
        with self.assertRaises(TicketTierMismatchError):
            insert_test_razorpay_payment(event=event_1.name, tier=event_2_tier)

        event_2.delete()
