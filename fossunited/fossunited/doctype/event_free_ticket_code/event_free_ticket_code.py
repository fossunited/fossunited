# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventFreeTicketCode(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Data | None
        event: DF.Link
        full_name: DF.Data | None
        is_used: DF.Check
        mapped_email: DF.Data
        max_count: DF.Int
        other_tier: DF.Data | None
        tier: DF.Literal[
            "Volunteer",
            "Speaker/Workshop Host",
            "Community Partner",
            "Sponsor",
            "Diversity Scholar",
            "Booth Manager",
            "Other",
        ]
        used_count: DF.Int
    # end: auto-generated types
    pass
