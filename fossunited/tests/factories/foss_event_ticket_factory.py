from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import EVENT_TICKET
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket import FOSSEventTicket

fake = Faker()


class FOSSEventTicketFactory(BaseFactory[FOSSEventTicket]):
    doctype = EVENT_TICKET

    @property
    def default_attributes(self) -> dict[str, Any]:
        event_name = self.overrides.get("event")
        if not event_name:
            event_name = FOSSChapterEventFactory.create("with_paid_tickets").name

        return {
            "event": event_name,
            "full_name": self.overrides.get("full_name", fake.name()),
            "email": self.overrides.get("email", fake.email()),
            "designation": self.overrides.get("designation", fake.job()),
            "organization": self.overrides.get("organization", fake.company()),
            "tier": self.overrides.get("tier", "General"),
            "wants_tshirt": self.overrides.get("wants_tshirt", 0),
            "tshirt_size": self.overrides.get("tshirt_size", None),
            "accept_coc": self.overrides.get("accept_coc", 1),
            "subscribe_chapter_mailing": self.overrides.get("subscribe_chapter_mailing", 0),
        }

    @property
    def with_tshirt(self) -> dict[str, Any]:
        return {
            "wants_tshirt": 1,
            "tshirt_size": self.overrides.get("tshirt_size", "M"),
        }

    @property
    def with_payment(self) -> dict[str, Any]:
        return {
            "razorpay_payment": self.overrides.get("razorpay_payment"),
        }

    @property
    def checked_in(self) -> dict[str, Any]:
        from frappe.utils import now_datetime

        return {
            "check_ins": [
                {
                    "check_in_time": now_datetime(),
                }
            ]
        }
