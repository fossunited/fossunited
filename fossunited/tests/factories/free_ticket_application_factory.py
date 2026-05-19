from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import FREE_TICKET_APPLY
from fossunited.fossunited.doctype.event_free_ticket_applications.event_free_ticket_applications import (
    EventFreeTicketApplications,
)

fake = Faker()


class FreeTicketApplicationFactory(BaseFactory[EventFreeTicketApplications]):
    doctype = FREE_TICKET_APPLY

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "coupon_id": self.overrides.get("coupon_id"),
            "event": self.overrides.get("event"),
            "email": self.overrides.get("email", fake.email()),
            "full_name": self.overrides.get("full_name", fake.name()),
        }

    @classmethod
    def create(cls, *_factory_traits: str, **overrides: Any):
        doc = cls.build(*_factory_traits, **overrides)
        doc.insert(ignore_permissions=True)
        cls._attach_del(doc)
        return doc
