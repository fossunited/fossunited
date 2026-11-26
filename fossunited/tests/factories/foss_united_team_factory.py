from typing import Any

from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import FOSS_UNITED_TEAM
from fossunited.fossunited.doctype.foss_united_team.foss_united_team import FOSSUnitedTeam


class FOSSUnitedTeamFactory(BaseFactory[FOSSUnitedTeam]):
    doctype = FOSS_UNITED_TEAM

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "foss_user_profile": self.overrides.get("foss_user_profile"),
            "other_profile": self.overrides.get("other_profile"),
            "org_role": self.overrides.get("org_role", "Full-Time"),
            "joined_on": self.overrides.get("joined_on"),
            "exited_on": self.overrides.get("exited_on"),
        }
