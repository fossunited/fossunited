# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OrganizationTeamMember(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        org_member: DF.Link
        org_role: DF.Literal[
            "Lead",  # noqa: F821
            "Core Team Member",  # noqa: F722
            "Volunteer",  # noqa: F821
            "Graphic Designer",  # noqa: F722
            "Content Writer",  # noqa: F722
            "Marketing",  # noqa: F821
            "Developer",  # noqa: F821
            "Manager",  # noqa: F821
        ]
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types
    pass
