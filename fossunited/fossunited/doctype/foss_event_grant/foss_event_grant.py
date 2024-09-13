# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSEventGrant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        application_details: DF.SmallText | None
        checked_guidelines: DF.Check
        communication_email: DF.Data | None
        custom_amount: DF.Data | None
        event_end_date: DF.Date | None
        event_location: DF.Data | None
        event_name: DF.Data | None
        event_organiser: DF.Data | None
        event_start_date: DF.Date | None
        event_type: DF.Literal["Hackathon", "Meetup", "Conference"]  # noqa: F821
        event_website: DF.Data | None
        grant_amount: DF.Literal["", "Rs. 10,000", "Rs. 25,000", "Rs. 50,000", "Custom"]  # noqa: F722, F821
        grant_status: DF.Literal["Open", "Approved", "Rejected", "Under Review"]  # noqa: F722, F821
        poc_name: DF.Data | None
        post_event_report: DF.Attach | None
        post_event_report_received: DF.Check
        reason_for_rejection: DF.SmallText | None
        source_of_info: DF.Data | None
        support_document: DF.Attach | None
    # end: auto-generated types

    pass
