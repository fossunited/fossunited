from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import HACKATHON_LOCALHOST
from fossunited.foss_hackathon.doctype.foss_hackathon_localhost.foss_hackathon_localhost import (
    FOSSHackathonLocalHost,
)
from fossunited.tests.factories.foss_hackathon_factory import FOSSHackathonFactory

fake = Faker()


class FOSSHackathonLocalHostFactory(BaseFactory[FOSSHackathonLocalHost]):
    doctype = HACKATHON_LOCALHOST

    @property
    def default_attributes(self) -> dict[str, Any]:
        parent_hackathon = (
            FOSSHackathonFactory.create().name
            if "parent_hackathon" not in self.overrides
            else self.overrides["parent_hackathon"]
        )
        return {
            "parent_hackathon": parent_hackathon,
            "localhost_name": fake.unique.name(),
            "is_accepting_attendees": 1,
        }

    @property
    def closed_to_attendees(self) -> dict[str, Any]:
        return {"is_accepting_attendees": 0}
