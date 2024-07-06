# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSUSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        code_of_conduct: DF.Check
        code_of_conduct_page: DF.Link | None
        cookie_policy: DF.Check
        cookie_policy_page: DF.Link | None
        privacy_policy: DF.Check
        privacy_policy_page: DF.Link | None
        terms_of_use: DF.Check
        terms_page: DF.Link | None
    # end: auto-generated types
    pass
