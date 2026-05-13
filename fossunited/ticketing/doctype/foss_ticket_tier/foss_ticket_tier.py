# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSTicketTier(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        currency: DF.Literal["INR"]
        description: DF.MarkdownEditor | None
        enabled: DF.Check
        maximum_tickets: DF.Int
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        price: DF.Currency
        title: DF.Data
        tshirt_included: DF.Check
        valid_till: DF.Date | None
    # end: auto-generated types
    pass
