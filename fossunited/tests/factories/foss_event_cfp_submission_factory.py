from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import EVENT, EVENT_CFP, PROPOSAL
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory

fake = Faker()


class FOSSEventCFPFactory(BaseFactory):
    doctype = EVENT_CFP

    @property
    def default_attributes(self) -> dict[str, Any]:
        event = (
            FOSSChapterEventFactory.create().name
            if "event" not in self.overrides
            else self.overrides["event"]
        )
        return {
            "event": event,
            "chapter": frappe.db.get_value(EVENT, event, "chapter"),
            "cfp_form_description": fake.text(max_nb_chars=100),
            "deadline": frappe.utils.add_days(frappe.utils.today(), 7),
            "status": self.overrides.get("status", "Live"),
            "allow_cfp_edit": self.overrides.get("allow_cfp_edit", 1),
        }


class FOSSEventCFPSubmissionFactory(BaseFactory):
    doctype = PROPOSAL

    @property
    def default_attributes(self) -> dict[str, Any]:
        cfp = (
            FOSSEventCFPFactory.create().name
            if "linked_cfp" not in self.overrides
            else self.overrides["linked_cfp"]
        )
        event = self.overrides.get("event") or frappe.db.get_value(EVENT_CFP, cfp, "event")
        submitted_by = self.overrides.get("submitted_by", "")
        return {
            "linked_cfp": cfp,
            "event": event,
            "chapter": frappe.db.get_value(EVENT, event, "chapter"),
            "submitted_by": submitted_by,
            "email": self.overrides.get("email", submitted_by),
            "talk_title": fake.text(max_nb_chars=60).strip("."),
            "talk_description": fake.paragraph(),
            "session_type": "Talk",
            "is_first_talk": "No",
            "status": "Review Pending",
            "subscribe_chapter_mailing": 1,
            "accept_coc": 1,
            "speakers": self.overrides.get("speakers", [self._default_speaker()]),
            "references": [{"link": fake.url()}],
        }

    def _default_speaker(self) -> dict:
        return {
            "full_name": fake.name(),
            "email": fake.email(),
            "designation": fake.job(),
            "organization": fake.company(),
            "bio": fake.paragraph(),
        }

    @property
    def with_approved_status(self) -> dict[str, Any]:
        return {"status": "Approved"}

    @property
    def with_withdrawn(self) -> dict[str, Any]:
        return {"is_withdrawn": 1}

    @property
    def with_review(self) -> dict[str, Any]:
        reviewer = self.overrides.get("reviewer", frappe.session.user)
        return {
            "reviews": [
                {
                    "reviewer": reviewer,
                    "email": reviewer,
                    "to_approve": self.overrides.get("to_approve", "Yes"),
                    "remarks": fake.sentence(),
                }
            ]
        }
