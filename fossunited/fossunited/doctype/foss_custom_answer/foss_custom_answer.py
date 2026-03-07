# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSCustomAnswer(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        question: DF.SmallText | None
        response: DF.LongText | None
        type: DF.Data | None
    # end: auto-generated types
    pass
