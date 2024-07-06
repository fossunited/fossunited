# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSProjectGrant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        about_project: DF.SmallText
        co_sponsor: DF.Data | None
        date_of_provision: DF.Date | None
        grant_amount: DF.Data | None
        grant_status: DF.Literal[
            "Open", "Approved", "Under Review", "Rejected"
        ]
        project_name: DF.Data
        project_website: DF.Data | None
    # end: auto-generated types

    pass
