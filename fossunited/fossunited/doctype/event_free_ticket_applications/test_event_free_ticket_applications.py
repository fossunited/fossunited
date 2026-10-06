# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

from unittest.mock import patch

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
from fossunited.fossunited.doctype.event_free_ticket_applications.event_free_ticket_applications import (
    EventFreeTicketApplications,
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
        self.assertEqual(ticket.wants_tshirt, 0)
        self.assertIsNone(ticket.tshirt_size)

    def test_tshirt_coupon_passes_size_to_ticket(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, tshirt_included=1)
        application = FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, tshirt_size="L"
        )

        ticket = frappe.get_doc(
            EVENT_TICKET, {"event": self.event.name, "email": application.email}
        )
        self.assertEqual(ticket.wants_tshirt, 1)
        self.assertEqual(ticket.tshirt_size, "L")

    def test_skip_tshirt_leaves_ticket_without_size(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, tshirt_included=1)
        application = FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, tshirt_size="Skip T-shirt"
        )

        # the choice stays on the application, but the ticket gets no t-shirt
        application.reload()
        self.assertEqual(application.tshirt_size, "Skip T-shirt")

        ticket = frappe.get_doc(
            EVENT_TICKET, {"event": self.event.name, "email": application.email}
        )
        self.assertEqual(ticket.wants_tshirt, 0)
        self.assertIsNone(ticket.tshirt_size)

    def test_tshirt_coupon_without_size_throws_error(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, tshirt_included=1)
        with self.assertRaises(frappe.ValidationError):
            FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)

        self.assertFalse(frappe.db.exists(EVENT_TICKET, {"event": self.event.name}))
        coupon.reload()
        self.assertEqual(coupon.used_count, 0)

    def test_size_is_dropped_when_coupon_has_no_tshirt(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, tshirt_included=0)
        application = FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, tshirt_size="XL"
        )

        application.reload()
        self.assertIsNone(application.tshirt_size)

        ticket = frappe.get_doc(
            EVENT_TICKET, {"event": self.event.name, "email": application.email}
        )
        self.assertEqual(ticket.wants_tshirt, 0)
        self.assertIsNone(ticket.tshirt_size)

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

    def test_custom_field_answer_passed_to_ticket(self):
        event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            custom_fields=[{"field_name": "github_handle", "label": "GitHub Handle"}],
        )
        coupon = FreeTicketCodeFactory.create(event=event.name)
        application = FreeTicketApplicationFactory.create(
            coupon_id=coupon.name,
            event=event.name,
            custom_fields=[{"field_name": "github_handle", "data": "octocat"}],
        )

        ticket = frappe.get_doc(EVENT_TICKET, {"event": event.name, "email": application.email})
        self.assertEqual(len(ticket.custom_fields), 1)
        self.assertEqual(ticket.custom_fields[0].field_name, "github_handle")
        self.assertEqual(ticket.custom_fields[0].data, "octocat")
        frappe.delete_doc(EVENT, event.name, force=True)

    def test_second_application_after_max_count(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=1, used_count=0)
        FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, email=coupon.mapped_email
        )
        coupon.reload()
        self.assertEqual(coupon.is_used, 1)
        with self.assertRaisesRegex(frappe.ValidationError, "max count"):
            FreeTicketApplicationFactory.create(coupon_id=coupon.name, event=self.event.name)

    def test_single_use_coupon_rejects_other_email(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=1)
        other_email = fake.unique.email()

        with self.assertRaises(frappe.ValidationError) as ctx:
            FreeTicketApplicationFactory.create(
                coupon_id=coupon.name, event=self.event.name, email=other_email
            )

        # whoever holds the code may not be its owner - don't tell them who is
        self.assertNotIn(coupon.mapped_email, str(ctx.exception))
        self.assertFalse(
            frappe.db.exists(EVENT_TICKET, {"event": self.event.name, "email": other_email})
        )
        coupon.reload()
        self.assertEqual(coupon.used_count, 0)
        self.assertEqual(coupon.is_used, 0)

    def test_single_use_coupon_accepts_mapped_email_case_insensitively(self):
        coupon = FreeTicketCodeFactory.create(
            event=self.event.name, max_count=1, mapped_email="Speaker.Name@Example.com"
        )
        FreeTicketApplicationFactory.create(
            coupon_id=coupon.name, event=self.event.name, email="speaker.name@example.COM"
        )

        self.assertTrue(
            frappe.db.exists(
                EVENT_TICKET, {"event": self.event.name, "email": "speaker.name@example.COM"}
            )
        )
        coupon.reload()
        self.assertEqual(coupon.used_count, 1)
        self.assertEqual(coupon.is_used, 1)

    def test_multi_use_coupon_can_be_shared_with_other_emails(self):
        # e.g. a sponsor passing seats to their team: not bound to mapped_email
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=2)
        emails = [fake.unique.email(), fake.unique.email()]
        for email in emails:
            FreeTicketApplicationFactory.create(
                coupon_id=coupon.name, event=self.event.name, email=email
            )

        for email in emails:
            self.assertTrue(
                frappe.db.exists(EVENT_TICKET, {"event": self.event.name, "email": email})
            )
        coupon.reload()
        self.assertEqual(coupon.used_count, 2)
        self.assertEqual(coupon.is_used, 1)

    def test_losing_a_race_for_the_last_use_gets_no_ticket(self):
        """
        Simulate two people redeeming the last use at the same time: this
        redemption passes validate_coupon, then another one commits before it
        claims the use. It must be rejected rather than over-issuing.
        """
        coupon = FreeTicketCodeFactory.create(event=self.event.name, max_count=2, used_count=1)
        email = fake.unique.email()
        validate_coupon = EventFreeTicketApplications.validate_coupon

        def validate_then_lose_race(application):
            coupon_data = validate_coupon(application)
            frappe.db.set_value(FREE_TICKET_CODE, coupon.name, {"used_count": 2, "is_used": 1})
            return coupon_data

        with patch.object(EventFreeTicketApplications, "validate_coupon", validate_then_lose_race):
            with self.assertRaisesRegex(frappe.ValidationError, "max count"):
                FreeTicketApplicationFactory.create(
                    coupon_id=coupon.name, event=self.event.name, email=email
                )

        self.assertFalse(
            frappe.db.exists(EVENT_TICKET, {"event": self.event.name, "email": email})
        )
        coupon.reload()
        self.assertEqual(coupon.used_count, 2)
