# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSEventGrant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        agree_fosshack_rule: DF.Literal["Yes", "No", "Not applicable"]
        amount_requested: DF.Currency
        communication_email: DF.Data
        custom_amount: DF.Data | None
        custom_sponsor_request: DF.Data | None
        event_count: DF.Data | None
        event_edition: DF.Data | None
        event_end_date: DF.Date
        event_location: DF.Data | None
        event_name: DF.Data
        event_organiser: DF.Data
        event_start_date: DF.Date
        event_type: DF.Literal[
            "Hackathon", "Meetup", "Conference", "Workshop", "Devsprint", "Other"
        ]
        event_website: DF.Data | None
        foss_creation: DF.SmallText | None
        foss_relation: DF.SmallText | None
        grant_amount: DF.Literal["Rs. 10,000", "Rs. 25,000", "Rs. 50,000", "Custom"]
        grant_status: DF.Literal["Open", "Under Review", "Approved", "Rejected"]
        if_foss_creation: DF.Literal["Yes", "No"]
        if_license_cc: DF.Literal["Yes", "No"]
        if_recurring_event: DF.Literal["Yes", "No"]
        is_foss_event: DF.Literal["Yes", "No"]
        organizer_type: DF.Literal[
            "Student community",
            "Professional community",
            "Individual",
            "Non-profit organization",
            "Other",
        ]
        organizer_type_other: DF.Data | None
        poc_name: DF.Data
        poc_phone: DF.Data | None
        post_event_report: DF.Attach | None
        post_event_report_received: DF.Check
        prev_edition_details: DF.SmallText | None
        read_thesis: DF.Check
        reason_for_rejection: DF.SmallText | None
        source_of_info: DF.Data | None
        sponsor_request: DF.Literal[
            "Monetary grant", "Diversity sponsorship", "Custom sponsorship"
        ]
        sponsorship_desk: DF.Attach | None
        support_document: DF.Attach | None
        total_event_budget: DF.Currency
    # end: auto-generated types

    pass
