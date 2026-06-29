from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import PROJ_GRANTS
from fossunited.fossunited.doctype.foss_project_grant.foss_project_grant import (
    FOSSProjectGrant,
)

fake = Faker()


class FOSSProjectGrantFactory(BaseFactory[FOSSProjectGrant]):
    doctype = PROJ_GRANTS

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "project_name": fake.catch_phrase(),
            "about_project": fake.text(max_nb_chars=300),
            "grant_status": "Open",
        }
