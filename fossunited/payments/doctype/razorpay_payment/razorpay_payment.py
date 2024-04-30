# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RazorpayPayment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        billing_address: DF.SmallText | None
        currency: DF.Literal["INR"]
        document_name: DF.DynamicLink | None
        document_type: DF.Link | None
        email: DF.Data
        gstn: DF.Data | None
        meta_data: DF.Code | None
        order_id: DF.Data | None
        payment_id: DF.Data | None
        status: DF.Literal["Captured", "Failed", "Pending"]
    # end: auto-generated types

    pass
