# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FOSSEventCFPReview(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        remarks: DF.SmallText | None
        reviewer: DF.Data | None
        reviewer_profile: DF.Link | None
        to_approve: DF.Literal["", "Yes", "No", "Maybe"]
    # end: auto-generated types

    def before_save(self):
        self.calculate_total_score()

    def calculate_total_score(self):
        if not self.scores:
            self.total_score = 0
            return

        total = 0
        for score_row in self.scores:
            if not score_row.category or not score_row.score:
                continue
            weight = frappe.db.get_value("CFP Score Category", score_row.category, "weight") or 1.0
            total += float(score_row.score) * float(weight)

        self.total_score = total
