from datetime import datetime, timedelta
from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.chapters.doctype.foss_chapter_event.foss_chapter_event import (
    FOSSChapterEvent,
)
from fossunited.doctype_ids import EVENT
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory

fake = Faker()


class FOSSChapterEventFactory(BaseFactory[FOSSChapterEvent]):
    doctype = EVENT

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "chapter": FOSSChapterFactory.create().name
            if "chapter" not in self.overrides
            else None,
            "event_name": self.overrides.get("event_name", fake.text(max_nb_chars=20).strip()),
            "event_permalink": fake.slug().replace("-", "_"),
            "status": "Live",
            "event_type": self.overrides.get("event_type", "Meet Up"),
            "event_start_date": self.overrides.get(
                "event_start_date", frappe.utils.add_days(frappe.utils.today(), 1)
            ),
            "event_end_date": self.overrides.get(
                "event_end_date", frappe.utils.add_days(frappe.utils.today(), 2)
            ),
            "event_description": self.overrides.get(
                "event_description", fake.text(max_nb_chars=200).strip()
            ),
            "is_paid_event": 0,
            "tickets_status": "Closed",
        }

    @property
    def with_chapter(self) -> dict[str, Any]:
        chapter = self.overrides.get("chapter")
        if not chapter:
            chapter = FOSSChapterFactory.create()
        chapter_name = chapter.name if hasattr(chapter, "name") else chapter
        return {"chapter": chapter_name}

    @property
    def with_paid_tickets(self) -> dict[str, Any]:
        return {
            "is_paid_event": 1,
            "tickets_status": "Live",
            "tiers": [
                {
                    "enabled": 1,
                    "title": "General",
                    "price": 100,
                    "maximum_tickets": 100,
                }
            ],
        }

    @property
    def with_map_link(self) -> dict[str, Any]:
        map_link = self.overrides.get("map_link") or "https://maps.google.com/?q=12.9716,77.5946"
        return {"map_link": map_link}

    @property
    def with_past_dates(self) -> dict[str, Any]:
        return {
            "event_start_date": datetime.today() - timedelta(days=10),
            "event_end_date": datetime.today() - timedelta(days=5),
        }

    @property
    def with_ongoing_dates(self) -> dict[str, Any]:
        return {
            "event_start_date": datetime.today() - timedelta(days=1),
            "event_end_date": datetime.today() + timedelta(days=1),
        }
