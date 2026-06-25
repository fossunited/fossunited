from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import EVENT_GRANTS
from fossunited.fossunited.doctype.foss_event_grant.foss_event_grant import (
    FOSSEventGrant,
)

fake = Faker()


class FOSSEventGrantFactory(BaseFactory[FOSSEventGrant]):
    doctype = EVENT_GRANTS

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "event_name": fake.catch_phrase(),
            "event_type": "Meetup",
            "event_start_date": frappe.utils.add_days(frappe.utils.today(), 15),
            "is_foss_event": "Yes",
            "event_organiser": fake.company(),
            "organizer_type": "Student community",
            "poc_name": fake.name(),
            "communication_email": fake.company_email(),
            "amount_requested": fake.random_int(min=5000, max=50000),
            "read_thesis": 1,
            "grant_status": "Open",
        }
