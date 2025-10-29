from datetime import datetime, timedelta

import frappe
from frappe.utils import now_datetime

from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    EVENT_RSVP,
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
            doc.show_rsvp = 0
            doc.show_cfp = 0
            doc.show_speakers = 1
            doc.save(ignore_permissions=True)

            rsvps = frappe.get_all(EVENT_RSVP, filters={"event": doc.name}, fields=["name"])
            for r in rsvps:
                frappe.db.set_value(EVENT_RSVP, r.name, "is_published", 0)

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
    Updates the job status to Expired, if they are Approved (active) and
    were last modified more than 3 months ago (90 days).
    """
    cutoff_date = datetime.now() - timedelta(days=90)
    past_active_jobs = frappe.get_all(
        JOB,
        filters={"status": JOB_STATUS_APPROVED, "modified": ["<", cutoff_date]},
        fields=["name"],
    )

    for jobs in past_active_jobs:
        try:
            # Get the actual document object
            job_doc = frappe.get_doc(JOB, jobs.name)
            job_doc.status = JOB_STATUS_EXPIRED
            job_doc.save(ignore_permissions=True)

            # Send notification email after successful update
            if job_doc.mail:
                cc_email = ["foundation@fossunited.org"]
                subject = (
                    f"Job Posting Auto-Expiry Notice: "
                    f"{frappe.utils.escape_html(job_doc.name)} | "
                    f"{frappe.utils.escape_html(job_doc.job_title)}"
                )

                message = (
                    f"<p>Dear {frappe.utils.escape_html(job_doc.company_name)},</p>"
                    f"<p>Your job posting titled"
                    f"<strong>{frappe.utils.escape_html(job_doc.job_title)}</strong> "
                    f"has been up for 90 days and "
                    f"will now be automatically marked as "
                    f"<strong>Expired</strong>.</p>"
                    f"<p>If you wish to keep this job open, please reply over this email.</p>"
                    f"<p>Regards,<br>FOSS United Team</p>"
                )
                frappe.sendmail(
                    recipients=[job_doc.mail],
                    cc=cc_email,
                    subject=subject,
                    message=message,
                )
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                f"Error updating job status - ID:{job_doc.name}\nError:{str(e)}",
            )
            continue
