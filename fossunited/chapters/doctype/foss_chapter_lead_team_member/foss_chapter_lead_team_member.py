# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
from frappe.model.document import Document


class FOSSChapterLeadTeamMember(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        chapter_member: DF.Link | None
        email: DF.Data | None
        full_name: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        role: DF.Literal[
            "Core Team Member", "Volunteer", "Graphic Designer", "Content Writer", "Marketing"  # noqa: F722, F821
        ]
    # end: auto-generated types
    pass
