from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import HACKATHON_PROJECT, HACKATHON_TEAM
from fossunited.foss_hackathon.doctype.foss_hackathon_project.foss_hackathon_project import (
    FOSSHackathonProject,
)
from fossunited.tests.factories.foss_hackathon_team_factory import FOSSHackathonTeamFactory

fake = Faker()


class FOSSHackathonProjectFactory(BaseFactory[FOSSHackathonProject]):
    doctype = HACKATHON_PROJECT

    @property
    def default_attributes(self) -> dict[str, Any]:
        hackathon_override = self.overrides.get("hackathon")

        if "team" in self.overrides:
            team = self.overrides["team"]
        elif hackathon_override:
            team = FOSSHackathonTeamFactory.create(hackathon=hackathon_override).name
        else:
            team = FOSSHackathonTeamFactory.create().name

        hackathon = hackathon_override or frappe.db.get_value(HACKATHON_TEAM, team, "hackathon")

        return {
            "hackathon": hackathon,
            "team": team,
            "title": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
        }
