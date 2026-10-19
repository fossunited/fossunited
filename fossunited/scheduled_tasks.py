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
from fossunited.fossunited.utils import FORKLORE_MAINTAINERS_CACHE_KEY

# Forklore stores one file per maintainer at content/maintainers/<github-username>.json
FORKLORE_MAINTAINERS_API = (
    "https://api.github.com/repos/fossunited/forklore/contents/content/maintainers"
)


def sync_forklore_maintainers():
    """Cache the set of forklore maintainer usernames for the profile OG image.

    Forklore (https://forklore.in) is a static site; a user is a maintainer iff a
    file content/maintainers/<github-username>.json exists in the forklore repo.
    We refresh the username set daily so FOSS User Profile.get_profile_badges() can
    flag maintainers locally instead of hitting GitHub's (rate-limited) API on every
    profile render.
    """
    try:
        resp = requests.get(
            FORKLORE_MAINTAINERS_API,
            headers={"Accept": "application/vnd.github+json"},
            timeout=30,
        )
        resp.raise_for_status()
        entries = resp.json()
    except Exception:
        frappe.log_error(
            title="Forklore maintainer sync failed",
            message=frappe.get_traceback(),
        )
        return

    usernames = [
        entry["name"].removesuffix(".json")
        for entry in entries
        if isinstance(entry, dict) and entry.get("name", "").endswith(".json")
    ]
    # Guard against a transient empty/error response wiping a good cache.
    if usernames:
        frappe.cache().set_value(FORKLORE_MAINTAINERS_CACHE_KEY, usernames)


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
