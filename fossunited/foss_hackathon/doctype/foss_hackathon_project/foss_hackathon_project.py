# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FOSSHackathonProject(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        demo_link: DF.Data | None
        description: DF.TextEditor
        hackathon: DF.Link
        is_published: DF.Check
        repo_link: DF.Data
        route: DF.Data | None
        short_description: DF.SmallText | None
        team: DF.Link
        title: DF.Data

    # end: auto-generated types
    def before_save(self):
        self.set_route()

    def set_route(self):
        hackathon = frappe.get_doc("FOSS Hackathon", self.hackathon)
        self.route = f"{hackathon.route}/p/{self.name}"
