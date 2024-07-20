# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from fossunited.doctype_ids import FOSS_USER_PROFILE


class FOSSUnitedTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        designation: DF.Data | None
        foss_user_profile: DF.Link | None
        full_name: DF.Data
        headshot: DF.AttachImage | None
        is_active: DF.Check
        org_role: DF.Literal[
            "",
            "Founder",
            "Board",
            "Full-Time",
            "Part-Time",
            "Intern",
            "Fellow",
            "Volunteer",
        ]
        portfolio_url: DF.Data | None
        user_bio: DF.SmallText | None
        username: DF.Data | None
    # end: auto-generated types

    pass
