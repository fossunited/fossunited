import frappe
import requests
from frappe.utils import add_days, now_datetime

from fossunited.doctype_ids import (
    EVENT,
    EVENT_CFP,
    JOB,
    JOB_STATUS_APPROVED,
    JOB_STATUS_EXPIRED,
)

# Forklore publishes a list of {"username", "github"} maintainers at this URL.
FORKLORE_MAINTAINERS_URL = "https://forklore.in/maintainers.json"


def sync_forklore_maintainers():
    """Store Forklore maintainer handles in Ograph Settings for profile OG images.

    Forklore (https://forklore.in) publishes /maintainers.json. We refresh the
    handle set monthly so FOSS User Profile.get_profile_badges() can flag
    maintainers from a local lookup instead of calling an external service on
    every profile render.
    """
    if not frappe.db.exists("DocType", "Ograph Settings"):
        return

    try:
        resp = requests.get(FORKLORE_MAINTAINERS_URL, timeout=30)
        resp.raise_for_status()
        entries = resp.json()
    except Exception:
        frappe.log_error(
            title="Forklore maintainer sync failed",
            message=frappe.get_traceback(),
        )
        return

    # Store both handles per maintainer: a profile may match by GitHub handle or
    # by forklore username (the two can differ).
    handles = [
        handle
        for entry in entries
        if isinstance(entry, dict)
        for handle in (entry.get("github"), entry.get("username"))
        if handle
    ]
    # Preserve the saved handles on a transient empty/error response.
    if handles:
        frappe.db.set_single_value(
            "Ograph Settings", "forklore_maintainers", frappe.as_json(handles)
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
