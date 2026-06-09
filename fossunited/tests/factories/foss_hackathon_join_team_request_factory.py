from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import JOIN_TEAM_REQUEST
from fossunited.foss_hackathon.doctype.foss_hackathon_join_team_request.foss_hackathon_join_team_request import (
    FOSSHackathonJoinTeamRequest,
)
from fossunited.tests.factories.foss_hackathon_factory import FOSSHackathonFactory
from fossunited.tests.factories.foss_hackathon_team_factory import FOSSHackathonTeamFactory
from fossunited.tests.factories.user_factory import UserFactory

fake = Faker()


class FOSSHackathonJoinTeamRequestFactory(BaseFactory[FOSSHackathonJoinTeamRequest]):
    doctype = JOIN_TEAM_REQUEST

    @property
    def default_attributes(self) -> dict[str, Any]:
        hackathon = self.overrides.get("hackathon")
        team = self.overrides.get("team")

        if not hackathon and not team:
            hackathon_doc = FOSSHackathonFactory.create()
            hackathon = hackathon_doc.name
            team = FOSSHackathonTeamFactory.create(hackathon=hackathon).name
        elif not team:
            team = FOSSHackathonTeamFactory.create(hackathon=hackathon).name
        elif not hackathon:
            import frappe

            hackathon = frappe.db.get_value("FOSS Hackathon Team", team, "hackathon")

        requested_by = UserFactory.create().name if "requested_by" not in self.overrides else self.overrides["requested_by"]

        return {
            "hackathon": hackathon,
            "team": team,
            "requested_by": requested_by,
            "reciever_email": fake.email(),
        }

    @property
    def outgoing(self) -> dict[str, Any]:
        return {"is_outgoing_request": 1}
