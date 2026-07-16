from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import TICKET_TRANSFER
from fossunited.tests.factories.foss_event_ticket_factory import FOSSEventTicketFactory
from fossunited.ticketing.doctype.foss_event_ticket_transfer.foss_event_ticket_transfer import (
    FOSSEventTicketTransfer,
)

fake = Faker()


class FOSSEventTicketTransferFactory(BaseFactory[FOSSEventTicketTransfer]):
    doctype = TICKET_TRANSFER

    @property
    def default_attributes(self) -> dict[str, Any]:
        ticket_name = self.overrides.get("ticket")
        if not ticket_name:
            ticket_name = FOSSEventTicketFactory.create().name

        return {
            "ticket": ticket_name,
            "receiver_name": self.overrides.get("receiver_name", fake.name()),
            "receiver_email": self.overrides.get("receiver_email", fake.email()),
            "designation": self.overrides.get("designation", None),
            "organization": self.overrides.get("organization", None),
            "wants_tshirt": self.overrides.get("wants_tshirt", 0),
            "tshirt_size": self.overrides.get("tshirt_size", None),
        }
