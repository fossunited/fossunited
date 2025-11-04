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
from fossunited.tests.utils import insert_test_chapter, insert_test_event


class TestEventFreeTicketApplications(FrappeTestCase):
    def setUp(self):
        self.fake = Faker()
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(
            chapter=self.chapter,
            is_paid_event=True,
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
        frappe.db.delete(FREE_TICKET_APPLY, {"event": self.event.name})
        frappe.db.delete(EVENT_TICKET, {"event": self.event.name})
        frappe.db.delete(FREE_TICKET_CODE, {"event": self.event.name})
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.commit()

    def create_test_coupon(self, max_count=5, used_count=0, tier="Volunteer", other_tier=None):
        coupon = frappe.get_doc(
            {
                "doctype": FREE_TICKET_CODE,
                "event": self.event.name,
                "tier": tier,
                "max_count": max_count,
                "used_count": used_count,
                "is_used": 0,
                "mapped_email": self.fake.email(),
                "other_tier": other_tier,
            }
        )
        coupon.insert(ignore_permissions=True)
        return coupon

    def submit_application(self, coupon_id, event=None, full_name=None, email=None, **kwargs):
        full_name = full_name or self.fake.name()
        email = email or self.fake.email()
        application = frappe.get_doc(
            {
                "doctype": FREE_TICKET_APPLY,
                "event": (event or self.event).name
                if hasattr(event, "name")
                else (event or self.event.name),
                "coupon_id": coupon_id,
                "full_name": full_name,
                "email": email,
                **kwargs,
            }
        )
        application.insert(ignore_permissions=True)
        return application, email, full_name

    def test_valid_application_creates_ticket(self):
        coupon = self.create_test_coupon()
        full_name = self.fake.name()
        _, email, _ = self.submit_application(coupon.name, full_name=full_name)

        ticket = frappe.get_doc(EVENT_TICKET, {"event": self.event.name, "email": email})
        self.assertEqual(ticket.full_name, full_name)
        self.assertEqual(ticket.tier, "Volunteer Free Pass")
        self.assertEqual(ticket.designation, None or ticket.designation)
        self.assertEqual(ticket.organization, None or ticket.organization)
        self.assertEqual(ticket.subscribe_chapter_mailing, 1)

    def test_coupon_usage_increments(self):
        coupon = self.create_test_coupon(max_count=5, used_count=0)
        self.submit_application(coupon.name)
        coupon.reload()
        self.assertEqual(coupon.used_count, 1)
        self.assertEqual(coupon.is_used, 0)

    def test_coupon_marked_used_at_max_count(self):
        coupon = self.create_test_coupon(max_count=2, used_count=1)
        self.submit_application(coupon.name)
        coupon.reload()
        self.assertEqual(coupon.used_count, 2)
        self.assertEqual(coupon.is_used, 1)

    def test_invalid_coupon_throws_error(self):
        application = frappe.get_doc(
            {
                "doctype": FREE_TICKET_APPLY,
                "event": self.event.name,
                "coupon_id": "INVALID_COUPON_123",
                "full_name": self.fake.name(),
                "email": self.fake.email(),
            }
        )
        with self.assertRaises(frappe.ValidationError):
            application.insert(ignore_permissions=True)

    def test_max_count_reached_throws_error(self):
        coupon = self.create_test_coupon(max_count=3, used_count=3)
        with self.assertRaises(frappe.ValidationError):
            self.submit_application(coupon.name)

    def test_coupon_event_mismatch_throws_error(self):
        other_event = insert_test_event(chapter=self.chapter, event_name="Other Test Event")
        coupon = self.create_test_coupon()
        with self.assertRaises(frappe.ValidationError):
            # pass other event id explicitly
            self.submit_application(coupon.name, event=other_event)
        frappe.delete_doc("FOSS Chapter Event", other_event.name, force=True)

    def test_other_tier_formatting(self):
        coupon = self.create_test_coupon(tier="Other", other_tier="VIP Guest")
        self.submit_application(coupon.name)
        ticket = frappe.get_last_doc(EVENT_TICKET)
        self.assertEqual(ticket.tier, "VIP Guest Free Pass")

    def test_multiple_applications_same_coupon(self):
        coupon = self.create_test_coupon(max_count=3, used_count=0)
        for i in range(3):
            with self.subTest(i=i):
                self.submit_application(coupon.name)
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
                coupon = self.create_test_coupon(tier=tier)
                self.submit_application(coupon.name)
                ticket = frappe.get_last_doc(EVENT_TICKET)
                self.assertEqual(ticket.tier, f"{tier} Free Pass")

    def test_second_application_after_max_count(self):
        coupon = self.create_test_coupon(max_count=1, used_count=0)
        self.submit_application(coupon.name)
        coupon.reload()
        self.assertEqual(coupon.is_used, 1)
        with self.assertRaises(frappe.ValidationError):
            self.submit_application(coupon.name)
