from datetime import date, timedelta

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import EVENT, EVENT_TICKET, RAZORPAY_PAYMENT, TICKET_TIER
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    RazorpayPaymentFactory,
)
from fossunited.tests.factories.razorpay_payment_factory import _make_attendee
from fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket import (
    TicketTierMismatchError,
)

fake = Faker()


class TestRazorpayPayment(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tickets_status="Live",
            tiers=[{"enabled": 1, "title": "Test", "price": 100, "maximum_tickets": 5}],
        )

    def tearDown(self):
        frappe.set_user("Administrator")

        payments = frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name})
        for payment in payments:
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)

        tickets = frappe.get_all(EVENT_TICKET, {"event": self.event.name})
        for ticket in tickets:
            frappe.delete_doc(EVENT_TICKET, ticket.name)

        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def test_payment_creation(self):
        # Given, as administrator
        frappe.set_user("Administrator")
        # When a payment is created, it succeeds
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        self.assertTrue(payment)
        payment.delete(force=True)

        # When a non system user tries to create a payment, it fails
        frappe.set_user("test1@example.com")
        with self.assertRaises(frappe.PermissionError):
            RazorpayPaymentFactory.create(event=self.event.name)

    def test_ticket_creation_on_capture(self):
        # Given a pending payment
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        self.assertEqual(payment.status, "Pending")
        self.assertIsNone(frappe.db.exists(EVENT_TICKET, {"razorpay_payment": payment.name}))

        # When captured, a ticket is created
        payment.status = "Captured"
        payment.save()
        payment.reload()

        self.assertIsNotNone(frappe.db.exists(EVENT_TICKET, {"razorpay_payment": payment.name}))

    def test_multiple_ticket_creation_on_capture(self):
        # Given a payment with 3 attendees
        number_of_attendees = 3
        payment = RazorpayPaymentFactory.create(
            event=self.event.name, num_seats=number_of_attendees
        )
        self.assertEqual(payment.status, "Pending")
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), 0)

        # When captured, 3 tickets created
        payment.status = "Captured"
        payment.save()

        self.assertEqual(
            frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), number_of_attendees
        )

    def test_payment_creation_on_closed_tickets(self):
        # Given an event with tickets closed
        self.event.tickets_status = "Closed"
        self.event.save()
        self.event.reload()

        with self.assertRaises(frappe.PermissionError):
            RazorpayPaymentFactory.create(event=self.event.name)

    def test_event_ticket_tier_mismatch(self):
        event_2 = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[{"enabled": 1, "title": "Faulty", "price": 5, "maximum_tickets": 5}],
            tickets_status="Live",
        )
        event_2_tier = frappe.get_doc(TICKET_TIER, {"parent": event_2.name, "parenttype": EVENT})

        # Payment for event_1 but with event_2 tier → mismatch
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(event=self.event.name, tier=event_2_tier)

        event_2.delete(force=True)

    def test_multi_tier_payment_creation(self):
        # Given an event with two tiers via factory
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[
                {"enabled": 1, "title": "Early Bird", "price": 200, "maximum_tickets": 10},
                {"enabled": 1, "title": "General", "price": 500, "maximum_tickets": 10},
            ],
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": event.name, "parenttype": EVENT}, ["name", "price", "title"]
        )
        tier_a = next(t for t in tiers if t.title == "Early Bird")
        tier_b = next(t for t in tiers if t.title == "General")

        # 2 early bird + 1 general
        attendees = [
            _make_attendee(ticket_type=tier_a.name),
            _make_attendee(ticket_type=tier_a.name),
            _make_attendee(ticket_type=tier_b.name),
        ]
        tier_counts = {tier_a.name: 2, tier_b.name: 1}

        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=event.name,
            tier_counts=tier_counts,
            attendees=attendees,
        )

        # amount = 200*2 + 500*1 = 900
        self.assertTrue(payment)
        self.assertEqual(float(payment.amount), 900.0)

        payment.delete(force=True)
        event.delete(force=True)

    def test_multi_tier_ticket_creation_and_tier_assignment(self):
        # Given an event with two tiers via factory
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[
                {"enabled": 1, "title": "Early Bird", "price": 200, "maximum_tickets": 10},
                {"enabled": 1, "title": "General", "price": 500, "maximum_tickets": 10},
            ],
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": event.name, "parenttype": EVENT}, ["name", "price", "title"]
        )
        tier_a = next(t for t in tiers if t.title == "Early Bird")
        tier_b = next(t for t in tiers if t.title == "General")

        attendees = [
            _make_attendee(ticket_type=tier_a.name),
            _make_attendee(ticket_type=tier_b.name),
        ]
        tier_counts = {tier_a.name: 1, tier_b.name: 1}

        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=event.name,
            tier_counts=tier_counts,
            attendees=attendees,
        )

        # When captured
        payment.status = "Captured"
        payment.save()

        # Then 2 tickets with correct tier titles
        tickets = frappe.get_all(EVENT_TICKET, {"razorpay_payment": payment.name}, ["tier"])
        self.assertEqual(len(tickets), 2)
        tier_titles = {t.tier for t in tickets}
        self.assertIn("Early Bird", tier_titles)
        self.assertIn("General", tier_titles)

        event.delete(force=True)

    def test_amount_mismatch_rejected(self):
        # Given a payment where amount was tampered
        tier = frappe.get_doc(EVENT, self.event.name).get("tiers")[0]

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={tier.name: 1},
                attendees=[_make_attendee(ticket_type=tier.name)],
                amount=1,  # wrong amount
            )

    def test_disabled_tier_rejected(self):
        # Given an event with a disabled tier
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[{"enabled": 0, "title": "Disabled", "price": 100}],
        )
        tier = frappe.get_doc(TICKET_TIER, {"parent": event.name, "parenttype": EVENT})

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=event.name,
                tier_counts={tier.name: 1},
                attendees=[_make_attendee(ticket_type=tier.name)],
            )

        event.delete(force=True)

    def test_expired_tier_rejected(self):
        # Given an event with an expired tier
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[
                {
                    "enabled": 1,
                    "title": "Expired",
                    "price": 100,
                    "valid_till": (date.today() - timedelta(days=1)).isoformat(),
                }
            ],
        )
        tier = frappe.get_doc(TICKET_TIER, {"parent": event.name, "parenttype": EVENT})

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=event.name,
                tier_counts={tier.name: 1},
                attendees=[_make_attendee(ticket_type=tier.name)],
            )

        event.delete(force=True)

    def test_houseful_tier_rejected(self):
        # Given a tier already at max capacity
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[{"enabled": 1, "title": "Limited", "price": 100, "maximum_tickets": 1}],
        )
        tier = frappe.get_doc(TICKET_TIER, {"parent": event.name, "parenttype": EVENT})

        # Fill the tier: create pending then capture so tickets are created
        first_payment = RazorpayPaymentFactory.create(event=event.name)
        first_payment.status = "Captured"
        first_payment.save()

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=event.name,
                tier_counts={tier.name: 1},
                attendees=[_make_attendee(ticket_type=tier.name)],
            )

        first_payment.delete(force=True)
        event.delete(force=True)

    def test_tshirt_amount_included_in_validation(self):
        # Given an event with paid t-shirts
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[{"enabled": 1, "title": "Standard", "price": 100, "maximum_tickets": 10}],
            paid_tshirts_available=1,
            t_shirt_price=200,
        )
        tier = frappe.get_doc(TICKET_TIER, {"parent": event.name, "parenttype": EVENT})
        attendee = _make_attendee(ticket_type=tier.name, wants_tshirt=1)

        # Payment with tshirt cost: 100 + 200 = 300
        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=event.name,
            tier_counts={tier.name: 1},
            attendees=[attendee],
        )
        self.assertEqual(float(payment.amount), 300.0)

        # Tshirt cost missing → rejected
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=event.name,
                tier_counts={tier.name: 1},
                attendees=[attendee],
                amount=100,
            )

        payment.delete(force=True)
        event.delete(force=True)
        event.delete(force=True)
