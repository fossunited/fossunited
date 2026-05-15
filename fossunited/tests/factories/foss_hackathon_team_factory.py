from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import HACKATHON_TEAM
from fossunited.foss_hackathon.doctype.foss_hackathon_team.foss_hackathon_team import (
    FOSSHackathonTeam,
)
from fossunited.tests.factories.foss_hackathon_factory import FOSSHackathonFactory

fake = Faker()


class FOSSHackathonTeamFactory(BaseFactory[FOSSHackathonTeam]):
    doctype = HACKATHON_TEAM

    @property
    def default_attributes(self) -> dict[str, Any]:
        hackathon = self.overrides.get("hackathon") or FOSSHackathonFactory.create().name
        return {
            "hackathon": hackathon,
            "team_name": fake.unique.name(),
        }

    @property
    def looking_for_members(self) -> dict[str, Any]:
        return {"looking_for_members": 1}
