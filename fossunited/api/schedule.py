import csv
import io
import json
from collections import defaultdict
from datetime import datetime, timedelta

import frappe
from frappe import _, local
from frappe.utils.pdf import get_pdf
from frappe.utils.response import as_csv, as_json, as_pdf, as_txt
from ics import Calendar, Event

from fossunited.doctype_ids import EVENT, EVENT_SCHEDULE, PROPOSAL, SPEAKER


def format_date(date_obj):
    """Format a date object to 'dd/mm/YYYY' string."""
    return date_obj.strftime("%d/%m/%Y")


@frappe.whitelist(allow_guest=True)
def get_event_schedule(event_id: str) -> dict:
    """
    Get the schedule for the event, grouped by date and hall.
    For each schedule item with a linked_cfp, also fetch the proposal route and speakers.

    Args:
        event_id (str): Event ID

    Returns:
        dict: {date: {hall: [sessions]}}
    """
    schedule = frappe.db.get_all(
        EVENT_SCHEDULE,
        {"parent": event_id, "parenttype": EVENT},
        ["*"],
        order_by="start_time",
    )

    # Build a sorted list of unique dates
    unique_dates = sorted({session["scheduled_date"] for session in schedule})
    date_to_day = {format_date(date): idx + 1 for idx, date in enumerate(unique_dates)}

    # Batch fetch all linked_cfp proposal routes and speakers
    linked_cfp_set = {
        session.get("linked_cfp") for session in schedule if session.get("linked_cfp")
    }
    linked_cfp_list = list(linked_cfp_set)

    # Batch fetch proposal routes
    proposal_routes = (
        frappe.db.get_all(
            PROPOSAL,
            filters={"name": ("in", linked_cfp_list)} if linked_cfp_list else {},
            fields=["name", "route"],
        )
        if linked_cfp_list
        else []
    )
    route_lookup = {row["name"]: row["route"] for row in proposal_routes}

    # Batch fetch all speakers for these proposals
    speakers = (
        frappe.db.get_all(
            SPEAKER,
            filters={"parent": ("in", linked_cfp_list)} if linked_cfp_list else {},
            fields=[
                "parent",
                "full_name",
                "designation",
                "organization",
                "bio",
                "photo",
                "linked_user",
                "social_link",
            ],
        )
        if linked_cfp_list
        else []
    )
    speakers_lookup = {}
    for speaker in speakers:
        parent = speaker.pop("parent")
        speakers_lookup.setdefault(parent, []).append(speaker)

    # Group by date and hall, enrich with batch-fetched data
    schedule_by_date_and_hall = defaultdict(lambda: defaultdict(list))
    for session in schedule:
        date_str = format_date(session["scheduled_date"])
        hall = session.get("hall") or "no-hall"
        session.day = date_to_day[date_str]

        linked_cfp = session.get("linked_cfp")
        if linked_cfp:
            session["cfp_route"] = route_lookup.get(linked_cfp)
            session["cfp_speakers"] = speakers_lookup.get(linked_cfp, [])
        else:
            session["cfp_route"] = None
            session["cfp_speakers"] = []

        schedule_by_date_and_hall[date_str][hall].append(session)

    # Convert defaultdicts to dicts and sort by date
    sorted_schedule = {
        date: dict(halls)
        for date, halls in sorted(
            schedule_by_date_and_hall.items(),
            key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"),
        )
    }
    return sorted_schedule


@frappe.whitelist(allow_guest=True)
def download_schedule(event, format="ics", days="", halls=""):
    days_list = local.request.args.getlist("days") if local.request else []
    halls_list = local.request.args.getlist("halls") if local.request else []

    # Parse days into date objects
    days_date_objects = []
    for d in days_list:
        try:
            # NOTE: changed format to match input
            days_date_objects.append(datetime.strptime(d.strip(), "%Y-%m-%d").date())
        except Exception:
            frappe.log_error(f"Invalid date format: {d}", "Download Schedule")

    doc = frappe.get_doc(EVENT, event)
    sessions = []

    for s in doc.event_schedule:
        session_date = s.scheduled_date
        if hasattr(session_date, "date"):
            session_date = session_date.date()

        if days_date_objects and session_date not in days_date_objects:
            continue
        if halls_list and s.hall not in halls_list:
            continue

        # Ensure required fields for later use
        s.start_time_str = str(timedelta(seconds=int(s.start_time.total_seconds())))
        s.end_time_str = str(timedelta(seconds=int(s.end_time.total_seconds())))
        s.speakers_list = []

        # Parse speakers (if stringified JSON)
        if s.speakers:
            try:
                s.speakers_list = json.loads(s.speakers)["speakers"]
            except Exception:
                pass

        sessions.append(s)

    if not sessions:
        message = "No matching sessions found."

        if format == "ics":
            cal = Calendar()
            # No events added, empty calendar
            frappe.response["filename"] = f"{doc.event_name}_empty.ics"
            frappe.response["type"] = "text/calendar"
            frappe.response["data"] = str(cal)
            return

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            # Write only headers
            writer.writerow(["Title", "Date", "Start Time", "End Time", "Hall"])
            frappe.response["doctype"] = doc.event_name
            frappe.response["result"] = output.getvalue()
            return as_csv()

        elif format == "txt":
            txt_data = "No matching sessions found."
            frappe.response["doctype"] = doc.event_name
            frappe.response["result"] = txt_data
            return as_txt()

        elif format == "pdf":
            html = "<h3>No matching sessions found.</h3>"
            pdf_data = get_pdf(html)
            frappe.response["filename"] = f"{doc.event_name}_empty.pdf"
            frappe.response["filecontent"] = pdf_data
            return as_pdf()

        elif format == "json":
            frappe.response["doctype"] = doc.event_name
            frappe.response["result"] = []
            return as_json()

        else:
            # Unknown format fallback
            frappe.response["result"] = message
            return

    # Prepare filename
    filename = doc.event_name.replace(" ", "_")
    if days_date_objects:
        filename += "-Days-" + "-".join([d.strftime("%Y-%m-%d") for d in days_date_objects])
    if halls_list:
        filename += "-Halls-" + "-".join(halls_list)

    # ---------- FORMAT: ICS ----------
    if format == "ics":
        cal = Calendar()
        for s in sessions:
            e = Event()
            e.name = f"{s.title} - {doc.event_name}"
            start_dt = datetime.combine(s.scheduled_date, (datetime.min + s.start_time).time())
            end_dt = datetime.combine(s.scheduled_date, (datetime.min + s.end_time).time())
            if end_dt <= start_dt:
                continue
            e.begin = start_dt
            e.end = end_dt
            e.location = f"{s.hall}, {doc.event_location}"
            e.description = f"Category: {s.category or 'N/A'}\nSpeakers: {', '.join([sp.get('name') for sp in s.speakers_list])}"  # noqa: E501
            cal.events.add(e)

        # Serve properly with "download" type
        frappe.response["type"] = "download"
        frappe.response["filename"] = filename + ".ics"
        frappe.response["filecontent"] = str(cal)
        frappe.response["headers"] = {
            "Content-Type": "text/calendar; charset=utf-8",
            "Content-Disposition": f"attachment; filename={filename}.ics",
        }
        return

    # ---------- FORMAT: CSV ----------
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Title",
                "Date",
                "Start Time",
                "End Time",
                "Hall",
                "Category",
                "CFP",
                "Speakers",
            ]
        )
        for s in sessions:
            speaker_names = ", ".join([sp.get("name") for sp in s.speakers_list])
            writer.writerow(
                [
                    s.title,
                    s.scheduled_date,
                    s.start_time_str,
                    s.end_time_str,
                    s.hall,
                    s.category,
                    s.get("cfp_route") or "",
                    speaker_names,
                ]
            )
        frappe.response["doctype"] = filename
        frappe.response["result"] = output.getvalue()
        return as_csv()

    # ---------- FORMAT: TXT ----------
    elif format == "txt":
        lines = []
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            lines.append(
                f"Title: {s.title}\n"
                f"Date: {s.scheduled_date}, {s.start_time_str} - {s.end_time_str}\n"
                f"Hall: {s.hall}\n"
                f"Category: {s.category}\n"
                f"CFP: {s.get('cfp_route') or 'N/A'}\n"
                f"Speakers: {speakers}\n"
                f"{'-' * 40}"
            )
        txt_data = "\n".join(lines)
        frappe.response["doctype"] = filename
        frappe.response["result"] = txt_data
        return as_txt()

    # ---------- FORMAT: PDF ----------
    elif format == "pdf":
        html = "<h2>Schedule</h2><ul>"
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            html += (
                f"<li><b>{s.title}</b><br>"
                f"<b>Date:</b> {s.scheduled_date}<br>"
                f"<b>Time:</b> {s.start_time_str} - {s.end_time_str}<br>"
                f"<b>Hall:</b> {s.hall}<br>"
                f"<b>Category:</b> {s.category}<br>"
                f"<b>Speakers:</b> {speakers}<br>"
                f"<b>CFP:</b> {s.get('cfp_route') or 'N/A'}"
                f"</li><br>"
            )
        html += "</ul>"

        pdf_data = get_pdf(html)
        frappe.response["filename"] = filename + ".pdf"
        frappe.response["filecontent"] = pdf_data
        return as_pdf()

    # ---------- FORMAT: JSON ----------
    elif format == "json":
        result = []
        for s in sessions:
            result.append(
                {
                    "title": s.title,
                    "date": str(s.scheduled_date),
                    "start_time": s.start_time_str,
                    "end_time": s.end_time_str,
                    "hall": s.hall,
                    "category": s.category,
                    "cfp_route": s.get("cfp_route"),
                    "speakers": s.speakers_list,
                }
            )
        frappe.response["doctype"] = filename
        frappe.response["result"] = result
        return as_json()

    # ---------- UNSUPPORTED ----------
    else:
        frappe.throw(_("Unsupported format: {0}").format(format))
