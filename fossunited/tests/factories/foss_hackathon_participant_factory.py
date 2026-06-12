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
        hackathon = (
            FOSSHackathonFactory.create().name
            if "hackathon" not in self.overrides
            else self.overrides["hackathon"]
        )
        return {
            "hackathon": hackathon,
            "full_name": fake.name(),
            "email": fake.unique.email(),
        }

    @property
    def with_user(self) -> dict[str, Any]:
        from fossunited.tests.factories.user_factory import UserFactory

        user = (
            UserFactory.create().name if "user" not in self.overrides else self.overrides["user"]
        )
        return {"user": user}

    @property
    def attending_locally(self) -> dict[str, Any]:
        return {"wants_to_attend_locally": 1}
