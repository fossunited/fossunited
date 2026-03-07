# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CFPReviewTemplateReason(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        reason: DF.Text
        type: DF.Literal["Accepted", "Rejected", "Not Sure"]
    # end: auto-generated types
    pass
