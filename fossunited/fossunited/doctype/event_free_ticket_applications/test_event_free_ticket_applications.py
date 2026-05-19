# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_TICKET,
    FREE_TICKET_APPLY,
    FREE_TICKET_CODE,
)
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FreeTicketApplicationFactory,
    FreeTicketCodeFactory,
)

fake = Faker()


class TestEventFreeTicketApplications(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.delete(FREE_TICKET_APPLY, {"event": self.event.name})
        frappe.db.delete(EVENT_TICKET, {"event": self.event.name})
        frappe.db.delete(FREE_TICKET_CODE, {"event": self.event.name})
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.commit()  # nosemgrep: frappe-manual-commit - tearDown needs commit to flush deletes before next test

    def test_valid_application_creates_ticket(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name)
        full_name = fake.name()
        application = FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, full_name=full_name
        )

        ticket = frappe.get_doc(
            EVENT_TICKET, {"event": self.event.name, "email": application.email}
        )
        self.assertEqual(ticket.full_name, full_name)
        self.assertEqual(ticket.tier, "Volunteer Free Pass")
        self.assertIsNone(ticket.designation)
        self.assertIsNone(ticket.organization)
        self.assertEqual(ticket.subscribe_chapter_mailing, 1)

    def test_coupon_usage_increments(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=5, used_count=0)
        FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
        coupon.reload()
        self.assertEqual(coupon.used_count, 1)
        self.assertEqual(coupon.is_used, 0)

    def test_coupon_marked_used_at_max_count(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=2, used_count=1)
        FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
        coupon.reload()
        self.assertEqual(coupon.used_count, 2)
        self.assertEqual(coupon.is_used, 1)

    def test_invalid_coupon_throws_error(self):
        with self.assertRaises(frappe.ValidationError):
            FreeTicketApplicationFactory.create(
                coupon_id="INVALID_COUPON_123", event=self.event.name
            )

    def test_max_count_reached_throws_error(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=3, used_count=3)
        with self.assertRaises(frappe.ValidationError):
            FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)

    def test_coupon_event_mismatch_throws_error(self):
        other_event = FOSSChapterEventFactory.create(
            chapter=self.chapter.name, event_name="Other Test Event"
        )
        coupon = FreeTicketCodeFactory.create(event=self.event.name)
        with self.assertRaises(frappe.ValidationError):
            # pass other event id explicitly
            FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=other_event.name)
        frappe.delete_doc(EVENT, other_event.name, force=True)

    def test_other_tier_formatting(self):
        coupon = FreeTicketCodeFactory.create(
            event=self.event.name, tier="Other", other_tier="VIP Guest"
        )
        FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
        ticket = frappe.get_last_doc(EVENT_TICKET)
        self.assertEqual(ticket.tier, "VIP Guest Free Pass")

    def test_multiple_applications_same_coupon(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=3, used_count=0)
        for i in range(3):
            with self.subTest(i=i):
                FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
        coupon.reload()
        self.assertEqual(coupon.used_count, 3)
        self.assertEqual(coupon.is_used, 1)
        tickets_count = frappe.db.count(
            EVENT_TICKET, {"event": self.event.name, "tier": "Volunteer Free Pass"}
        )
        self.assertEqual(tickets_count, 3)

    def test_all_tier_types(self):
        tiers = [
            "Volunteer",
            "Speaker/Workshop Host",
            "Community Partner",
            "Sponsor",
            "Diversity Scholar",
            "Booth Manager",
        ]
        for tier in tiers:
            with self.subTest(tier=tier):
                coupon = FreeTicketCodeFactory.create(event=self.event.name, tier=tier)
                FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
                ticket = frappe.get_last_doc(EVENT_TICKET)
                self.assertEqual(ticket.tier, f"{tier} Free Pass")

    def test_second_application_after_max_count(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=1, used_count=0)
        FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
        coupon.reload()
        self.assertEqual(coupon.is_used, 1)
        with self.assertRaises(frappe.ValidationError):
            FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)
