# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

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
    pass
