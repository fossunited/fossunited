# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class IndustryPartners(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Data
        fosshack_sponsor_tier: DF.Literal[
            "Platinum", "Gold", "Silver", "Bronze"
        ]
        indiafoss_sponsor_tier: DF.Literal[
            "Platinum", "Gold", "Silver", "Bronze"
        ]
        is_current_partner: DF.Check
        is_fosshack_sponsor: DF.Check
        is_indiafoss_sponsor: DF.Check
        joining_date: DF.Date | None
        logo: DF.AttachImage
        special_category: DF.Data | None
        tier: DF.Literal[
            "Patron",
            "Platinum",
            "Gold",
            "Silver",
            "Bronze",
            "Special",
            "Flagship Event Sponsor",
        ]
        website: DF.Data
    # end: auto-generated types

    pass
