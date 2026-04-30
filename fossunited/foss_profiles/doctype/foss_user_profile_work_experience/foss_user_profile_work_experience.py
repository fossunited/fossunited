# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSUserProfileWorkExperience(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        city: DF.Data | None
        company: DF.Data
        company_website: DF.Data
        country: DF.Data | None
        description: DF.TextEditor | None
        employment_type: DF.Literal[
            "",
            "Full-time",
            "Part-time",
            "Internship",
            "Freelance",
            "Self-employed",
            "Trainee",
        ]
        end_date: DF.Date | None
        is_remote: DF.Check
        is_working_here: DF.Check
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        start_date: DF.Date
        title: DF.Data
    # end: auto-generated types
    pass
