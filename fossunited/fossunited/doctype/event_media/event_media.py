# Copyright (c) 2026, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventMedia(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.cfp_submission_speaker.cfp_submission_speaker import (
            CFPSubmissionSpeaker,
        )

        duration: DF.Duration | None
        event: DF.Link | None
        event_name: DF.Data | None
        proposal: DF.Link | None
        proposal_route: DF.Data | None
        speakers: DF.Table[CFPSubmissionSpeaker]
        title: DF.Data | None
        video_type: DF.Literal[
            "Talk", "Keynote", "Panel Discussion", "Workshop", "Lightning Talk", "Live Stream"
        ]
        video_url: DF.Data | None
    # end: auto-generated types
    pass
