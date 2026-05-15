from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import HACKATHON_PARTICIPANT
from fossunited.foss_hackathon.doctype.foss_hackathon_participant.foss_hackathon_participant import (
    FOSSHackathonParticipant,
)
from fossunited.tests.factories.foss_hackathon_factory import FOSSHackathonFactory

fake = Faker()


class FOSSHackathonParticipantFactory(BaseFactory[FOSSHackathonParticipant]):
    doctype = HACKATHON_PARTICIPANT

    @property
    def default_attributes(self) -> dict[str, Any]:
        hackathon = self.overrides.get("hackathon") or FOSSHackathonFactory.create().name
        return {
            "hackathon": hackathon,
            "full_name": fake.name(),
            "email": fake.unique.email(),
        }

    @property
    def with_user(self) -> dict[str, Any]:
        from fossunited.tests.factories.user_factory import UserFactory

        user = self.overrides.get("user") or UserFactory.create().name
        return {"user": user}

    @property
    def attending_locally(self) -> dict[str, Any]:
        return {"wants_to_attend_locally": 1}
