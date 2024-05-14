# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FOSSHackathonLocalHost(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hack_localhost_organizer.foss_hack_localhost_organizer import (
            FOSSHackLocalHostOrganizer,
        )

        city: DF.Link | None
        localhost_name: DF.Data
        location: DF.Data | None
        map_link: DF.Data | None
        organizers: DF.Table[FOSSHackLocalHostOrganizer]
        parent_hackathon: DF.Link
        state: DF.Link | None
    # end: auto-generated types
    pass
