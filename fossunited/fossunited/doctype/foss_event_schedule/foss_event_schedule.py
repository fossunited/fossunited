# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSEventSchedule(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        category: DF.Literal["Talk", "Lightning Talk", "Workshop", "Panel Discussion", "Opening Note", "Break", "Other"]  # noqa: F722, F821
        end_time: DF.Time | None
        hall: DF.Data | None
        linked_cfp: DF.Link | None
        other_category: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        scheduled_date: DF.Date | None
        speakers: DF.JSON | None
        start_time: DF.Time | None
        title: DF.Data | None
    # end: auto-generated types

    pass
