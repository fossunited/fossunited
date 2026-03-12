# Copyright (c) 2026, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HackathonResult(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        cash_prize: DF.Currency
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        project: DF.Link | None
        status: DF.Literal["Winner", "Commendation"]
        team: DF.Link | None
    # end: auto-generated types
    pass
