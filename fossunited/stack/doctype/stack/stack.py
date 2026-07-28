# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Stack(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        category: DF.Data
        description: DF.MarkdownEditor | None
        hosted_url: DF.Data | None
        icon: DF.AttachImage | None
        link: DF.Data
        status: DF.Literal["Active", "Not Actively Used", "Deprecated"]
        title: DF.Data
    # end: auto-generated types

    pass
