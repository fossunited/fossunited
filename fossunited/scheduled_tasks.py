import frappe
from frappe.utils import add_days, now_datetime

from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    JOB,
    JOB_STATUS_APPROVED,
    JOB_STATUS_EXPIRED,
)
from fossunited.utils.notifications import send_event_rsvp_reminder


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
            doc.show_rsvp = 0
            doc.show_cfp = 0
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


def send_rsvp_event_reminders():
    tomorrow = add_days(frappe.utils.today(), 1)
    day_after = add_days(frappe.utils.today(), 2)

    events = frappe.db.get_all(
        EVENT,
        filters=[
            ["status", "=", "Live"],
            ["is_paid_event", "=", 0],
            ["reminder_sent", "=", 0],
            ["event_start_date", ">=", tomorrow],
            ["event_start_date", "<", day_after],
        ],
        pluck="name",
        page_length=999,
    )

    for event_id in events:
        try:
            send_event_rsvp_reminder(event_id)
        except Exception:
            frappe.log_error(
                title=f"Error sending RSVP reminder: {event_id}",
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
