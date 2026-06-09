from datetime import datetime, timedelta
from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import HACKATHON
from fossunited.foss_hackathon.doctype.foss_hackathon.foss_hackathon import FOSSHackathon
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory

fake = Faker()


class FOSSHackathonFactory(BaseFactory[FOSSHackathon]):
    doctype = HACKATHON

    @property
    def default_attributes(self) -> dict[str, Any]:
        chapter = FOSSChapterFactory.create().name if "chapter" not in self.overrides else self.overrides["chapter"]
        return {
            "chapter": chapter,
            "permalink": fake.slug().replace("-", "_"),
            "hackathon_name": fake.text(max_nb_chars=20).strip(),
            "hackathon_type": "Hybrid",
            "start_date": datetime.today() + timedelta(days=1),
            "end_date": datetime.today() + timedelta(days=2),
            "hackathon_description": "Test Hackathon",
            "is_registration_live": 1,
            "max_team_members": 4,
        }

    @property
    def registration_closed(self) -> dict[str, Any]:
        return {"is_registration_live": 0}

    @property
    def with_past_dates(self) -> dict[str, Any]:
        return {
            "start_date": datetime.today() - timedelta(days=10),
            "end_date": datetime.today() - timedelta(days=5),
        }

    @property
    def with_ongoing_dates(self) -> dict[str, Any]:
        return {
            "start_date": datetime.today() - timedelta(days=1),
            "end_date": datetime.today() + timedelta(days=1),
        }
