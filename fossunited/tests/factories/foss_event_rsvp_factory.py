from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.chapters.doctype.foss_event_rsvp.foss_event_rsvp import FOSSEventRSVP
from fossunited.doctype_ids import EVENT_RSVP
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory

fake = Faker()


class FOSSEventRSVPFactory(BaseFactory[FOSSEventRSVP]):
    doctype = EVENT_RSVP

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "event": FOSSChapterEventFactory.create().name
            if "event" not in self.overrides
            else None,
            "allow_edit": 1,
            "max_rsvp_count": 5,
            "requires_host_approval": False,
            "rsvp_description": fake.text(max_nb_chars=200).strip(),
            "custom_questions": [],
        }

    @property
    def with_host_approval(self) -> dict[str, Any]:
        return {"requires_host_approval": True}

    @property
    def with_large_capacity(self) -> dict[str, Any]:
        return {"max_rsvp_count": 100}
