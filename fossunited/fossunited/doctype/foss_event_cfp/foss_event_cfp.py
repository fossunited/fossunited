# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime

from fossunited.doctype_ids import GLOBAL_CFP_SETTINGS


class FOSSEventCFP(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_question.foss_custom_question import (
            FOSSCustomQuestion,
        )
        from fossunited.fossunited.doctype.foss_event_cfp_reviewer.foss_event_cfp_reviewer import (
            FOSSEventCFPReviewer,
        )

        allow_cfp_edit: DF.Check
        anonymise_proposals: DF.Check
        cfp_custom_questions: DF.Table[FOSSCustomQuestion]
        cfp_form_description: DF.TextEditor | None
        cfp_reviewers: DF.Table[FOSSEventCFPReviewer]
        chapter: DF.Data | None
        deadline: DF.Datetime | None
        event: DF.Link
        event_name: DF.Data | None
        has_public_custom_responses: DF.Check
        only_talk_proposals: DF.Check
        only_workshops: DF.Check
        status: DF.Literal["Closed", "Live"]
    # end: auto-generated types

    def is_past_deadline(self) -> bool:
        """True when a deadline is set and has already passed (full datetime precision)."""
        return bool(self.deadline and get_datetime(self.deadline) < now_datetime())

    def close_if_past_deadline(self) -> bool:
        """Lazily flip Live -> Closed once the deadline has passed.

        Returns True only when this call performed the flip. Uses db_set, so it is safe
        to call from a Guest read context and mutates self.status in memory for the caller.
        """
        if self.status == "Live" and self.is_past_deadline():
            self.db_set("status", "Closed")
            return True
        return False

    def can_edit_proposal(self) -> bool:
        """Whether a proposer may still edit their proposal content.

        allow_cfp_edit is the master switch. status auto-closes once the deadline
        passes, but we also check the deadline live in case that lazy flip has not
        run yet.
        """
        return bool(self.allow_cfp_edit) and self.status == "Live" and not self.is_past_deadline()

    def before_insert(self):
        self.assign_reviewers()

    def assign_reviewers(self):
        reviewers = frappe.get_single(GLOBAL_CFP_SETTINGS).members
        for reviewer in reviewers:
            self.append(
                "cfp_reviewers",
                {
                    "reviewer": reviewer.profile,
                    "email": reviewer.email,
                    "full_name": reviewer.full_name,
                },
            )
