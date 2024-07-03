# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

from fossunited.fossunited.utils import update_rsvp_count


class FOSSEventRSVPSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )

        chapter: DF.Data | None
        confirm_attendance: DF.Check
        custom_answers: DF.Table[FOSSCustomAnswer]
        email: DF.Data
        event: DF.Data | None
        event_name: DF.Data | None
        im_a: DF.Literal[
            "", "Student", "Professional", "FOSS Enthusiast"
        ]
        linked_rsvp: DF.Link | None
        name1: DF.Data
        submitted_by: DF.Link | None
    # end: auto-generated types
    pass
