from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import EVENT, EVENT_RSVP, RSVP_RESPONSE
from fossunited.tests.factories.foss_event_rsvp_factory import FOSSEventRSVPFactory

fake = Faker()


class FOSSEventRSVPSubmissionFactory(BaseFactory):
    doctype = RSVP_RESPONSE

    @property
    def default_attributes(self) -> dict[str, Any]:
        linked_rsvp = FOSSEventRSVPFactory.create().name if "linked_rsvp" not in self.overrides else self.overrides["linked_rsvp"]
        event = self.overrides.get("event") or frappe.db.get_value(
            EVENT_RSVP, linked_rsvp, "event"
        )
        chapter = frappe.db.get_value(EVENT, event, "chapter")
        return {
            "linked_rsvp": linked_rsvp,
            "event": event,
            "chapter": chapter,
            "name1": self.overrides.get("name1", fake.name()),
            "email": self.overrides.get("email", fake.email()),
            "im_a": self.overrides.get("im_a", "FOSS Enthusiast"),
            "status": self.overrides.get("status", "Accepted"),
            "accept_coc": 1,
            "subscribe_chapter_mailing": 0,
            "confirm_attendance": 0,
            "custom_answers": [],
        }

    @classmethod
    def create(cls, *traits, **overrides):
        """Override to force status via db.set_value after insert,
        bypassing handle_submission_status in before_insert."""
        # Resolve desired status from merged attrs (traits + overrides) before insert
        instance = cls(*traits)
        instance.overrides = overrides
        desired_status = {**instance.attributes, **overrides}.get("status", "Accepted")

        doc = super().create(*traits, **overrides)
        if doc.status != desired_status:
            frappe.db.set_value(RSVP_RESPONSE, doc.name, "status", desired_status)
            doc.reload()
        return doc

    @property
    def with_accepted(self) -> dict[str, Any]:
        return {"status": "Accepted"}

    @property
    def with_rejected(self) -> dict[str, Any]:
        return {"status": "Rejected"}

    @property
    def with_pending(self) -> dict[str, Any]:
        return {"status": "Pending"}
