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
        team = (
            FOSSHackathonTeamFactory.create().name
            if "team" not in self.overrides
            else self.overrides["team"]
        )
        hackathon = self.overrides.get("hackathon") or frappe.db.get_value(
            HACKATHON_TEAM, team, "hackathon"
        )

        return {
            "hackathon": hackathon,
            "team": team,
            "title": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
        }
