import frappe
from frappe.utils import add_days, now_datetime

from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    JOB,
    JOB_STATUS_APPROVED,
    JOB_STATUS_EXPIRED,
)


def conclude_events():
    """
    Get all the events which have ended (end_date < today) and set their status to concluded.
    Also hide RSVP/CFP if present.
    """

    events = frappe.db.get_all(
        EVENT,
        {
            "status": "Live",
            "event_end_date": ["<", now_datetime()],
        },
        ["name", "status", "event_end_date", "event_start_date"],
        page_length=999,
    )

    for event in events:
        try:
            doc = frappe.get_doc(EVENT, event.name)
            doc.status = "Concluded"
            doc.show_speakers = 1
            doc.save(ignore_permissions=True)

            cfps = frappe.get_all(EVENT_CFP, filters={"event": doc.name}, fields=["name"])
            for c in cfps:
                frappe.db.set_value(EVENT_CFP, c.name, "status", "Closed")

        except Exception:
            frappe.log_error(
                title=f"Error concluding event: {event.name}",
                message=frappe.get_traceback(),
            )


def update_past_job_status():
    """
    Expire jobs that were published more than 90 days ago.
    """
    cutoff_date = add_days(now_datetime(), -90)

    past_active_jobs = frappe.get_all(
        JOB,
        filters=[
            ["status", "=", JOB_STATUS_APPROVED],
            ["publish_date", "is", "set"],
            ["publish_date", "<=", cutoff_date],
        ],
        fields=["name"],
    )

    for job in past_active_jobs:
        try:
            job_doc = frappe.get_doc(JOB, job.name)
            job_doc.status = JOB_STATUS_EXPIRED
            job_doc.save(ignore_permissions=True)

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Error updating job status - ID:{job.name}",
            )
