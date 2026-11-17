from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.api.dashboard import create_razorpay_order
from fossunited.doctype_ids import EVENT, EVENT_TICKET, RAZORPAY_PAYMENT, TICKET_TIER
from fossunited.payments.doctype.razorpay_payment.razorpay_payment import (
    capture_payment,
    fail_payment,
)
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    RazorpayPaymentFactory,
)
from fossunited.tests.factories.razorpay_payment_factory import _make_attendee
from fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket import (
    TicketTierMismatchError,
    validate_attendee_tiers,
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

    def test_expired_pending_payment_skips_ticket_on_capture(self):
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        payment.db_set("order_id", "order_expired", update_modified=False)
        payment.order_id = "order_expired"
        self.event.tiers[0].valid_till = date.today() - timedelta(days=1)
        self.event.save()

        capture_payment(payment.order_id, "pay_expired")

        payment.reload()
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(payment.payment_id, "pay_expired")
        self.assertFalse(frappe.db.exists(EVENT_TICKET, {"razorpay_payment": payment.name}))

    def test_sold_out_pending_payment_skips_ticket_on_capture(self):
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        payment.db_set("order_id", "order_sold_out", update_modified=False)
        payment.order_id = "order_sold_out"
        tier = self.event.tiers[0]
        tier.maximum_tickets = 1
        self.event.save()
        frappe.get_doc(
            {
                "doctype": EVENT_TICKET,
                "event": self.event.name,
                "tier": tier.title,
                "full_name": "Existing Attendee",
                "email": "existing@example.com",
            }
        ).insert(ignore_permissions=True)

        capture_payment(payment.order_id, "pay_sold_out")

        payment.reload()
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"event": self.event.name}), 1)

    def test_capture_replay_does_not_duplicate_ticket(self):
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        payment.db_set("order_id", "order_replay", update_modified=False)
        payment.order_id = "order_replay"
        capture_payment(payment.order_id, "pay_first")
        capture_payment(payment.order_id, "pay_replayed")

        payment.reload()
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(payment.payment_id, "pay_first")
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), 1)

    def test_late_capture_after_failure_creates_ticket(self):
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        payment.db_set("order_id", "order_late_capture", update_modified=False)
        payment.db_set("status", "Failed", update_modified=False)

        capture_payment("order_late_capture", "pay_late_capture")

        payment.reload()
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(payment.payment_id, "pay_late_capture")
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), 1)

    def test_failure_after_capture_does_not_overwrite_status(self):
        payment = RazorpayPaymentFactory.create(event=self.event.name)
        payment.db_set("order_id", "order_captured_then_failed", update_modified=False)

        capture_payment("order_captured_then_failed", "pay_captured")
        fail_payment("order_captured_then_failed")

        payment.reload()
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(payment.payment_id, "pay_captured")
        self.assertEqual(frappe.db.count(EVENT_TICKET, {"razorpay_payment": payment.name}), 1)

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


class TestRazorpayPaymentTierRejection(FrappeTestCase):
    """Disabled, expired, and houseful tiers share one event with one tier each."""

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tickets_status="Live",
            tiers=[
                {"enabled": 0, "title": "Disabled", "price": 100},
                {"enabled": 1, "title": "Expired", "price": 100, "valid_till": yesterday},
                {"enabled": 1, "title": "Limited", "price": 100, "maximum_tickets": 1},
            ],
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": self.event.name, "parenttype": EVENT}, ["name", "title"]
        )
        self.tier_disabled = next(t for t in tiers if t.title == "Disabled")
        self.tier_expired = next(t for t in tiers if t.title == "Expired")
        self.tier_limited = next(t for t in tiers if t.title == "Limited")

    def tearDown(self):
        frappe.set_user("Administrator")
        for payment in frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name}):
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def test_disabled_tier_rejected(self):
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_disabled.name: 1},
                attendees=[_make_attendee(ticket_type=self.tier_disabled.name)],
            )

    def test_expired_tier_rejected(self):
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_expired.name: 1},
                attendees=[_make_attendee(ticket_type=self.tier_expired.name)],
            )

    def test_houseful_tier_rejected(self):
        # Fill the one available slot
        first_payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_limited.name: 1},
            attendees=[_make_attendee(ticket_type=self.tier_limited.name)],
        )
        first_payment.status = "Captured"
        first_payment.save()

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_limited.name: 1},
                attendees=[_make_attendee(ticket_type=self.tier_limited.name)],
            )


class TestRazorpayPaymentMultiTier(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tickets_status="Live",
            tiers=[
                {"enabled": 1, "title": "Early Bird", "price": 200, "maximum_tickets": 10},
                {"enabled": 1, "title": "General", "price": 500, "maximum_tickets": 10},
            ],
        )
        tiers = frappe.get_all(
            TICKET_TIER,
            {"parent": self.event.name, "parenttype": EVENT},
            ["name", "price", "title"],
        )
        self.tier_eb = next(t for t in tiers if t.title == "Early Bird")
        self.tier_gen = next(t for t in tiers if t.title == "General")

    def tearDown(self):
        frappe.set_user("Administrator")
        for payment in frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name}):
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def test_multi_tier_payment_creation(self):
        # 2 early bird + 1 general → amount = 200*2 + 500*1 = 900
        attendees = [
            _make_attendee(ticket_type=self.tier_eb.name),
            _make_attendee(ticket_type=self.tier_eb.name),
            _make_attendee(ticket_type=self.tier_gen.name),
        ]
        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_eb.name: 2, self.tier_gen.name: 1},
            attendees=attendees,
        )
        self.assertTrue(payment)
        self.assertEqual(float(payment.amount), 900.0)

    def test_multi_tier_ticket_creation_and_tier_assignment(self):
        # When captured, tickets carry correct tier titles
        attendees = [
            _make_attendee(ticket_type=self.tier_eb.name),
            _make_attendee(ticket_type=self.tier_gen.name),
        ]
        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_eb.name: 1, self.tier_gen.name: 1},
            attendees=attendees,
        )
        payment.status = "Captured"
        payment.save()

        tickets = frappe.get_all(EVENT_TICKET, {"razorpay_payment": payment.name}, ["tier"])
        self.assertEqual(len(tickets), 2)
        tier_titles = {t.tier for t in tickets}
        self.assertIn("Early Bird", tier_titles)
        self.assertIn("General", tier_titles)


class TestRazorpayPaymentTshirt(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[
                {
                    "enabled": 1,
                    "title": "Premium",
                    "price": 800,
                    "maximum_tickets": 10,
                    "tshirt_included": 1,
                },
                {"enabled": 1, "title": "Standard", "price": 400, "maximum_tickets": 10},
            ],
            paid_tshirts_available=1,
            t_shirt_price=200,
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": self.event.name, "parenttype": EVENT}, ["name", "title"]
        )
        self.tier_premium = next(t for t in tiers if t.title == "Premium")
        self.tier_standard = next(t for t in tiers if t.title == "Standard")

    def tearDown(self):
        frappe.set_user("Administrator")
        for payment in frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name}):
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def test_tshirt_included_tier_not_charged_extra(self):
        # Included tier: tshirt is free, no extra charge even if paid_tshirts_available
        attendee = _make_attendee(
            ticket_type=self.tier_premium.name, wants_tshirt=1, tshirt_size="M"
        )

        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_premium.name: 1},
            attendees=[attendee],
        )
        self.assertEqual(float(payment.amount), 800.0)

        # Sending 1000 (800 + 200) must be rejected — tshirt is not an add-on here
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_premium.name: 1},
                attendees=[attendee],
                amount=1000.0,
            )

    def test_paid_tshirt_addon_correct_amounts(self):
        # Non-included tier: wants_tshirt adds price; opting out does not
        with_tshirt = _make_attendee(
            ticket_type=self.tier_standard.name, wants_tshirt=1, tshirt_size="L"
        )
        payment_with = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_standard.name: 1},
            attendees=[with_tshirt],
        )
        self.assertEqual(float(payment_with.amount), 600.0)  # 400 + 200

        without_tshirt = _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=0)
        payment_without = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_standard.name: 1},
            attendees=[without_tshirt],
        )
        self.assertEqual(float(payment_without.amount), 400.0)

        # Sending tshirt price for opt-out attendee → rejected
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_standard.name: 1},
                attendees=[without_tshirt],
                amount=600.0,
            )

    def test_tshirt_amount_required_when_opted_in(self):
        # Opted-in attendee but amount missing tshirt cost → rejected
        attendee = _make_attendee(
            ticket_type=self.tier_standard.name, wants_tshirt=1, tshirt_size="M"
        )
        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts={self.tier_standard.name: 1},
            attendees=[attendee],
        )
        self.assertEqual(float(payment.amount), 600.0)  # 400 + 200

        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts={self.tier_standard.name: 1},
                attendees=[attendee],
                amount=400,  # tshirt cost missing
            )

    def test_mixed_tiers_only_addon_tshirt_charged(self):
        # One included, one non-included: only non-included tshirt counts toward amount
        attendees = [
            _make_attendee(ticket_type=self.tier_premium.name, wants_tshirt=1, tshirt_size="M"),
            _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=1, tshirt_size="L"),
        ]
        tier_counts = {self.tier_premium.name: 1, self.tier_standard.name: 1}

        payment = RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            tier_counts=tier_counts,
            attendees=attendees,
        )
        # 800 + 400 + 200 (only standard addon) = 1400
        self.assertEqual(float(payment.amount), 1400.0)

        # Charging both tshirts (1600) → rejected
        with self.assertRaises(TicketTierMismatchError):
            RazorpayPaymentFactory.create(
                "with_multi_tier",
                event=self.event.name,
                tier_counts=tier_counts,
                attendees=attendees,
                amount=1600.0,
            )


class TestCreateRazorpayOrderAmount(FrappeTestCase):
    """Verify _compute_order_amount (used to create Razorpay order) and
    validate_payment_before_insert agree on amount for every tshirt scenario.
    Both must produce the same number or valid orders get rejected at the API layer.
    """

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tickets_status="Live",
            tiers=[
                {
                    "enabled": 1,
                    "title": "Premium",
                    "price": 800,
                    "maximum_tickets": 10,
                    "tshirt_included": 1,
                },
                {"enabled": 1, "title": "Standard", "price": 400, "maximum_tickets": 10},
            ],
            paid_tshirts_available=1,
            t_shirt_price=200,
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": self.event.name, "parenttype": EVENT}, ["name", "title"]
        )
        self.tier_premium = next(t for t in tiers if t.title == "Premium")
        self.tier_standard = next(t for t in tiers if t.title == "Standard")

    def tearDown(self):
        frappe.set_user("Administrator")
        for payment in frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name}):
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def _mock_client(self, order_id):
        mock = MagicMock()
        mock.order.create.return_value = {"id": order_id}
        mock.auth = ["rzp_test_key", "secret"]
        return mock

    def _create_order(self, client_amount, tier_counts, attendees, order_id):
        meta_data = {
            "event": self.event.name,
            "tier_counts": tier_counts,
            "attendees": attendees,
            "num_seats": sum(tier_counts.values()),
        }
        with patch(
            "fossunited.api.dashboard.get_razorpay_client",
            return_value=self._mock_client(order_id),
        ):
            return create_razorpay_order(
                checkout_info={
                    "amount": client_amount,
                    "email": "buyer@example.com",
                    "tax_details": {},
                },
                meta_data=meta_data,
                ref_doctype=EVENT,
                ref_docname=self.event.name,
            )

    def test_create_order_uses_supported_order_fields(self):
        attendee = _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=0)
        client = self._mock_client("ord_expire")
        with (
            patch("fossunited.api.dashboard.get_razorpay_client", return_value=client),
        ):
            create_razorpay_order(
                checkout_info={
                    "amount": 400,
                    "email": "buyer@example.com",
                    "tax_details": {},
                },
                meta_data={
                    "event": self.event.name,
                    "tier_counts": {self.tier_standard.name: 1},
                    "attendees": [attendee],
                    "num_seats": 1,
                },
                ref_doctype=EVENT,
                ref_docname=self.event.name,
            )
        payload = client.order.create.call_args.kwargs["data"]
        self.assertEqual(payload, {"amount": 40000, "currency": "INR"})

    def test_standard_tier_no_tshirt(self):
        attendee = _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=0)
        result = self._create_order(400, {self.tier_standard.name: 1}, [attendee], "ord_001")
        self.assertEqual(result["order_id"], "ord_001")

    def test_standard_tier_with_tshirt_addon(self):
        attendee = _make_attendee(
            ticket_type=self.tier_standard.name, wants_tshirt=1, tshirt_size="M"
        )
        result = self._create_order(600, {self.tier_standard.name: 1}, [attendee], "ord_002")
        self.assertEqual(result["order_id"], "ord_002")

    def test_included_tier_tshirt_not_charged_extra(self):
        # Regression: before fix, backend computed 800+200=1000 while frontend sent 800.
        attendee = _make_attendee(
            ticket_type=self.tier_premium.name, wants_tshirt=1, tshirt_size="L"
        )
        result = self._create_order(800, {self.tier_premium.name: 1}, [attendee], "ord_003")
        self.assertEqual(result["order_id"], "ord_003")

    def test_mixed_tiers_only_addon_tshirt_charged(self):
        # 800 + 400 + 200 (only standard addon) = 1400
        attendees = [
            _make_attendee(ticket_type=self.tier_premium.name, wants_tshirt=1, tshirt_size="M"),
            _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=1, tshirt_size="L"),
        ]
        result = self._create_order(
            1400, {self.tier_premium.name: 1, self.tier_standard.name: 1}, attendees, "ord_004"
        )
        self.assertEqual(result["order_id"], "ord_004")

    def test_tampered_amount_rejected(self):
        attendee = _make_attendee(ticket_type=self.tier_standard.name, wants_tshirt=0)
        with self.assertRaises(frappe.ValidationError):
            self._create_order(1, {self.tier_standard.name: 1}, [attendee], "ord_005")


class TestRazorpayPaymentAttendeeTiers(FrappeTestCase):
    """Tickets are issued only for the tiers that were priced and paid for."""

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tickets_status="Live",
            tiers=[
                {"enabled": 1, "title": "Cheap", "price": 100, "maximum_tickets": 10},
                {"enabled": 1, "title": "Dear", "price": 1000, "maximum_tickets": 1},
            ],
        )
        tiers = frappe.get_all(
            TICKET_TIER, {"parent": self.event.name, "parenttype": EVENT}, ["name", "title"]
        )
        tier_names = {t.title: t.name for t in tiers}
        self.cheap, self.dear = tier_names["Cheap"], tier_names["Dear"]

    def tearDown(self):
        frappe.set_user("Administrator")
        for payment in frappe.get_all(RAZORPAY_PAYMENT, {"document_name": self.event.name}):
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name, force=True)
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def create_payment(self, tier_counts, ticket_types):
        return RazorpayPaymentFactory.create(
            "with_multi_tier",
            event=self.event.name,
            email=fake.email(),
            tier_counts=tier_counts,
            attendees=[_make_attendee(ticket_type=t) for t in ticket_types],
        )

    def capture(self, payment, **meta_changes) -> list[str]:
        """Capture the payment, optionally after changing its stored order details."""
        if meta_changes:
            meta = frappe.parse_json(payment.meta_data)
            meta.update(meta_changes)
            payment.db_set("meta_data", frappe.as_json(meta), update_modified=False)
        order_id = f"order_{payment.name}"
        payment.db_set("order_id", order_id, update_modified=False)
        capture_payment(order_id, f"pay_{payment.name}")
        payment.reload()
        return frappe.get_all(EVENT_TICKET, {"razorpay_payment": payment.name}, pluck="tier")

    def test_attendees_must_match_the_priced_tiers(self):
        cases = {
            "extra expensive attendee": ({self.cheap: 1}, [self.cheap, self.dear]),
            "cheap tier swapped for expensive": ({self.cheap: 1}, [self.dear]),
            "invented tier": ({self.cheap: 1}, [self.cheap, "vip-backstage"]),
            "fewer attendees than paid for": ({self.cheap: 2}, [self.cheap]),
        }
        for label, (tier_counts, attendees) in cases.items():
            with self.subTest(label), self.assertRaises(TicketTierMismatchError):
                self.create_payment(tier_counts, attendees)

        self.assertEqual(frappe.db.count(RAZORPAY_PAYMENT, {"document_name": self.event.name}), 0)

    def test_every_attendee_needs_a_ticket_tier(self):
        # Called directly: the payment factory fills in a missing ticket_type on its own.
        cases = {
            "missing": _make_attendee(ticket_type=None),
            "empty": _make_attendee(ticket_type=""),
            "dict": _make_attendee(ticket_type={"name": self.dear}),
            "list": _make_attendee(ticket_type=[self.cheap]),
            "attendee is not a dict": self.cheap,
        }
        for label, attendee in cases.items():
            meta = {"tier_counts": {self.cheap: 1}, "attendees": [attendee]}
            with (
                self.subTest(label),
                self.assertRaisesRegex(TicketTierMismatchError, "needs a ticket tier"),
            ):
                validate_attendee_tiers(meta)

    def test_zero_count_tiers_are_ignored(self):
        payment = self.create_payment({self.cheap: 1, self.dear: 0}, [self.cheap])
        self.assertEqual(self.capture(payment), ["Cheap"])

    def test_ticket_tier_title_comes_from_the_event(self):
        payment = self.create_payment({self.cheap: 1}, [self.cheap])
        tiers = self.capture(payment, tiers_snapshot={self.cheap: {"title": "VIP Backstage"}})
        self.assertEqual(tiers, ["Cheap"])

    def test_attendees_changed_after_checkout_get_no_tickets(self):
        cases = {
            "extra expensive attendee": {
                "attendees": [_make_attendee(ticket_type=t) for t in (self.cheap, self.dear)],
            },
            "invented tier": {
                "attendees": [_make_attendee(ticket_type=t) for t in (self.cheap, "vip")],
                "tiers_snapshot": {"vip": {"title": "VIP Backstage"}},
            },
        }
        for label, meta_changes in cases.items():
            with self.subTest(label):
                payment = self.create_payment({self.cheap: 1}, [self.cheap])
                tiers = self.capture(payment, **meta_changes)
                self.assertEqual(payment.status, "Captured")
                self.assertEqual(tiers, [])

        # The single-seat expensive tier was not sold out by the rejected tickets.
        self.assertEqual(frappe.db.get_value(TICKET_TIER, self.dear, "enabled"), 1)

    def test_payment_without_tier_counts_gets_no_tickets(self):
        payment = self.create_payment({self.cheap: 1}, [self.cheap])
        tiers = self.capture(payment, tier_counts={})
        self.assertEqual(payment.status, "Captured")
        self.assertEqual(tiers, [])
