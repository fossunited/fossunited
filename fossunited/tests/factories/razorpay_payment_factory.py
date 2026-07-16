from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import EVENT, RAZORPAY_PAYMENT, TICKET_TIER
from fossunited.payments.doctype.razorpay_payment.razorpay_payment import RazorpayPayment
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory

fake = Faker()


def _make_attendee(**kwargs) -> dict:
    return {
        "full_name": kwargs.get("full_name", fake.name()),
        "email": kwargs.get("email", fake.email()),
        "designation": kwargs.get("designation", fake.job()),
        "organization": kwargs.get("organization", fake.company()),
        "wants_tshirt": kwargs.get("wants_tshirt", 0),
        "tshirt_size": kwargs.get("tshirt_size", None),
        "ticket_type": kwargs.get("ticket_type", None),
    }


class RazorpayPaymentFactory(BaseFactory[RazorpayPayment]):
    doctype = RAZORPAY_PAYMENT

    @property
    def default_attributes(self) -> dict[str, Any]:
        event_name = self.overrides.get("event")
        if not event_name:
            event = FOSSChapterEventFactory.create("with_paid_tickets")
            event_name = event.name

        tier = self.overrides.get("tier") or frappe.get_doc(
            TICKET_TIER, {"parent": event_name, "parenttype": EVENT}
        )

        attendees = self.overrides.get("attendees")
        num_seats = self.overrides.get("num_seats", 1)
        if attendees is None:
            attendees = [_make_attendee(ticket_type=tier.name) for _ in range(num_seats)]

        tier_counts = self.overrides.get("tier_counts", {tier.name: len(attendees)})

        for a in attendees:
            if not a.get("ticket_type"):
                a["ticket_type"] = tier.name

        paid_tshirts_available, tshirt_price = frappe.db.get_value(
            EVENT, event_name, ["paid_tshirts_available", "t_shirt_price"]
        )
        amount = float(tier.price) * len(attendees)
        if paid_tshirts_available:
            num_tshirts = sum(
                1 for a in attendees if a.get("wants_tshirt") and not bool(tier.tshirt_included)
            )
            amount += float(tshirt_price or 0) * num_tshirts

        meta_data = {
            "attendees": attendees,
            "event": event_name,
            "num_seats": len(attendees),
            "tier_counts": tier_counts,
            "tier": tier.as_dict(),
        }

        return {
            "document_type": EVENT,
            "document_name": event_name,
            "email": self.overrides.get("email", attendees[0].get("email")),
            "amount": self.overrides.get("amount", amount),
            "currency": "INR",
            "status": self.overrides.get("status", "Pending"),
            "meta_data": frappe.as_json(meta_data),
        }

    @property
    def with_multi_tier(self) -> dict[str, Any]:
        """
        Expects overrides: event, tier_counts ({tier_name: count}), attendees.
        Computes correct amount automatically.
        """
        event_name = self.overrides.get("event")
        tier_counts: dict = self.overrides.get("tier_counts", {})
        attendees: list = self.overrides.get("attendees", [])

        paid_tshirts_available, tshirt_price = frappe.db.get_value(
            EVENT, event_name, ["paid_tshirts_available", "t_shirt_price"]
        )
        amount = 0.0
        for tier_name, count in tier_counts.items():
            price = frappe.db.get_value(TICKET_TIER, tier_name, "price")
            amount += float(price) * int(count)
        if paid_tshirts_available:
            tier_tshirt_included = {
                tier_name: bool(frappe.db.get_value(TICKET_TIER, tier_name, "tshirt_included"))
                for tier_name in tier_counts.keys()
            }
            num_tshirts = sum(
                1
                for a in attendees
                if a.get("wants_tshirt")
                and not tier_tshirt_included.get(a.get("ticket_type"), False)
            )
            amount += float(tshirt_price or 0) * num_tshirts

        meta_data = {
            "attendees": attendees,
            "event": event_name,
            "num_seats": len(attendees),
            "tier_counts": tier_counts,
        }

        return {
            "document_type": EVENT,
            "document_name": event_name,
            "email": self.overrides.get(
                "email", attendees[0].get("email") if attendees else fake.email()
            ),
            "amount": self.overrides.get("amount", amount),
            "currency": "INR",
            "status": self.overrides.get("status", "Pending"),
            "meta_data": frappe.as_json(meta_data),
        }
