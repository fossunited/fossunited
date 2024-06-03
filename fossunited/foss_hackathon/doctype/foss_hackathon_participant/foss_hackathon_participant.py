# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FOSSHackathonParticipant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data
        full_name: DF.Data
        github: DF.Data | None
        gitlab: DF.Data | None
        hackathon: DF.Link | None
        is_student: DF.Check
        localhost: DF.Link | None
        localhost_request_status: DF.Literal[
            "Pending", "Accepted", "Rejected"
        ]
        organization: DF.Data | None
        user: DF.Link | None
        user_profile: DF.Link | None
        wants_to_attend_locally: DF.Check
    # end: auto-generated types
    pass
