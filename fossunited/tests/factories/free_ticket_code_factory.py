from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import FREE_TICKET_CODE
from fossunited.fossunited.doctype.event_free_ticket_code.event_free_ticket_code import (
    EventFreeTicketCode,
)

fake = Faker()


class FreeTicketCodeFactory(BaseFactory[EventFreeTicketCode]):
    doctype = FREE_TICKET_CODE

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "event": self.overrides.get("event"),
            "mapped_email": self.overrides.get("mapped_email", fake.email()),
            "full_name": self.overrides.get("full_name", fake.name()),
            "max_count": self.overrides.get("max_count", 10),
            "tier": self.overrides.get("tier", "Volunteer"),
        }

    @classmethod
    def create(cls, *_factory_traits: str, **overrides: Any):
        doc = cls.build(*_factory_traits, **overrides)
        doc.insert(ignore_permissions=True)
        cls._attach_del(doc)
        return doc
