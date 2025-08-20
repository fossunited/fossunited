from datetime import datetime, timedelta

import frappe

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
    Get all the events which have ended (end_date < today) and set their status to concluded
    """
    events = frappe.db.get_all(
        EVENT,
        {"status": "Live", "event_end_date": ["<", datetime.today()]},
        ["name", "status", "event_end_date", "event_start_date"],
        page_length=999,
    )

    for event in events:
        doc = frappe.get_doc(EVENT, event.name)
        doc.status = "Concluded"
        doc.show_rsvp = 0
        doc.show_cfp = 0
        past_rsvp = frappe.get_doc(EVENT_RSVP, {"event_name": doc.event_name})
        past_rsvp.is_published = 0
        past_cfp = frappe.get_doc(EVENT_CFP, {"event_name": doc.event_name})
        past_cfp.status = "Closed"
        try:
            doc.save(ignore_permissions=True)
            past_rsvp.save(ignore_permissions=True)
            past_cfp.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                f"Error while concluding events through scheduler- ID:{doc.name}\nError:{str(e)}",
            )
            continue


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
            frappe.db.commit()

            # Send notification email after successful update
            if job_doc.mail:
                cc_email = ["developers@fossunited.org"]
                subject = (
                    f"Job Posting Auto-Expiry Notice: "
                    f"{frappe.utils.escape_html(job_doc.name)} | "
                    f"{frappe.utils.escape_html(job_doc.job_title)}"
                )

                message = (
                    f"<p>Dear {frappe.utils.escape_html(job_doc.company_name)},</p>"
                    f"<p>Your job posting titled"
                    f"<strong>{frappe.utils.escape_html(job_doc.job_title)}</strong> "
                    f"has not been updated in over 90 days and "
                    f"will now be automatically marked as "
                    f"<strong>Expired</strong>.</p>"
                    f"<p>If you wish to keep this job open, please update the job post.</p>"
                    f"<p>Regards,<br>FossUnited Team</p>"
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
