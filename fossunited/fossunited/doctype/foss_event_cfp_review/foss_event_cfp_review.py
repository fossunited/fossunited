# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import PROPOSAL


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
        to_approve: DF.Literal["", "Yes", "No", "Maybe"]  # noqa: F722, F821
    # end: auto-generated types

    def after_insert(self):
        self.review_mail()

    def on_update(self):
        self.review_mail()

    def review_mail(self):
        submission = frappe.db.get_value(
            PROPOSAL,
            {"name": self.parent},
            ["email", "route", "full_name", "talk_title", "event_name"],
            as_dict=1,
        )

        message = f"""
        Dear {submission.full_name},
        <br>
        Your CFP for {submission.event_name}, {submission.talk_title} has gotten a new review<br>
        Review Conclusion: {self.to_approve}<br>
        Remarks: {self.remarks}<br>
        You can access the CFP here: https://fossunited.org/{submission.route}<br>
        Regards,<br>
        FOSS United Team
        """

        frappe.sendmail(
            recipients=submission.email,
            subject="New review on your CFP for " + submission.event_name,
            message=message,
        )
