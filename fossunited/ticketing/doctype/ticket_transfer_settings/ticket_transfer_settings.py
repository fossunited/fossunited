# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TicketTransferSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        banner_image: DF.AttachImage | None
        web_page_description: DF.TextEditor | None
    # end: auto-generated types
    pass
