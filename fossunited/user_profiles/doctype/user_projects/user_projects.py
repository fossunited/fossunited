# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from urllib.parse import urlparse

import frappe
from frappe import _
from frappe.model.document import Document


class UserProjects(Document):
    def validate(self):
        if self.project_link:
            parsed = urlparse(self.project_link)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                frappe.throw(_("Project Link must be a valid HTTP(S) URL"))
