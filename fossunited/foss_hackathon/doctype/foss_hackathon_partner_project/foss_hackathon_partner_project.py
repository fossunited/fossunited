# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSHackathonPartnerProject(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.hackathon_project_issue_pr.hackathon_project_issue_pr import (  # noqa: E501
            HackathonProjectIssuePR,
        )

        about: DF.SmallText | None
        description: DF.MarkdownEditor | None
        hackathon: DF.Link | None
        logo: DF.AttachImage | None
        poc_email: DF.Data | None
        project_name: DF.Data | None
        project_thread: DF.Table[HackathonProjectIssuePR]
        repo_link: DF.Data | None
    # end: auto-generated types
    pass
