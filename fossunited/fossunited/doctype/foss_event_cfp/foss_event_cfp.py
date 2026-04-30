# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT, GLOBAL_CFP_SETTINGS


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

    def before_save(self):
        self.enable_cfp_tab()

    def enable_cfp_tab(self):
        frappe.db.set_value(EVENT, self.event, "show_cfp", 1)
