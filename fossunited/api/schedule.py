import csv
import io
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import frappe
from frappe import _, local
from frappe.utils.pdf import get_pdf
from frappe.utils.response import as_csv, as_json, as_pdf
from ics import Calendar, Event
from ics.grammar.parse import ContentLine

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
    """
    Download Event Schedule in various formats for given days and halls.

    Args:
      event: Event ID
      format: File formats - ics, csv, txt, md, org, json, pdf
      days: Dates in ISO format (since function converts it to str)
      halls: Venue of Hall names
    """

    if local.request:
        days_list = local.request.args.getlist("days")
        halls_list = local.request.args.getlist("halls")
    else:
        # fallback: parse comma-separated string params if provided
        days_list = days.split(",") if days else []
        halls_list = halls.split(",") if halls else []

    # Parse days into date objects
    days_date_objects = []
    for d in days_list:
        try:
            days_date_objects.append(datetime.strptime(d.strip(), "%Y-%m-%d").date())
        except ValueError as e:
            frappe.log_error(f"Invalid date format: {d}. Error: {e}", "Download Schedule")

    doc = frappe.get_doc(EVENT, event)
    sessions = get_event_sessions(doc, days_date_objects, halls_list)

    # Event metadata (shared across all formats)
    event_metadata = {
        "Event Name": doc.event_name,
        "Event Type": doc.event_type,
        "Event Route": f"https://fossunited.org/{doc.route}" if doc.route else "",
        "Location": doc.event_location or "Online",
        "Map Link": doc.map_link or "",
        "Description": frappe.utils.strip_html(doc.event_description or "") or "N/A",
    }

    # Sanitize filename
    filename = re.sub(r"[^A-Za-z0-9._-]+", "_", doc.event_name)
    if days_date_objects:
        filename += "-Days-" + "-".join([d.strftime("%Y-%m-%d") for d in days_date_objects])
    if halls_list:
        filename += "-Halls-" + "-".join(
            [re.sub(r"[^A-Za-z0-9._-]+", "_", hall) for hall in halls_list]
        )

    if not sessions:
        return build_response(format, "No matching sessions found.", filename, empty=True)

    format_alias = {
        "orgmode": "org",
        "markdown": "md",
    }
    format = format_alias.get(format.lower(), format)

    content = format_schedule_data(format, doc, sessions, event_metadata)
    return build_response(format, content, filename)


def get_event_sessions(doc, days_date_objects, halls_list):
    """
    Get event session with information on speakers and CFP link.

    Args:
      doc: Event doctype data type fetched
      days_date_objects: The converted date for days in str
      halls_list: List of halls to get schedule
    """

    sessions = []
    for s in doc.event_schedule:
        session_date = (
            s.scheduled_date.date() if hasattr(s.scheduled_date, "date") else s.scheduled_date
        )
        if days_date_objects and session_date not in days_date_objects:
            continue
        if halls_list and s.hall not in halls_list:
            continue

        s.start_time_str = str(timedelta(seconds=int(s.start_time.total_seconds())))
        s.end_time_str = str(timedelta(seconds=int(s.end_time.total_seconds())))
        s.speakers_list = []

        if s.speakers:
            try:
                speakers_data = json.loads(s.speakers)
                s.speakers_list = speakers_data.get("speakers", [])
            except Exception as e:
                frappe.log_error(
                    f"Failed to parse speakers JSON for session {s.title}: {e}",
                    "Download Schedule",
                )

        sessions.append(s)

    # Attach CFP route
    linked_cfps = [s.linked_cfp for s in sessions if s.get("linked_cfp")]
    if linked_cfps:
        proposals = frappe.db.get_all(
            PROPOSAL, filters={"name": ("in", linked_cfps)}, fields=["name", "route"]
        )
        route_lookup = {p["name"]: p["route"] for p in proposals}
        for s in sessions:
            if s.get("linked_cfp"):
                s.cfp_route = route_lookup.get(s.linked_cfp)

    return sessions


def format_schedule_data(format, doc, sessions, metadata):
    """
    File format the given schedule data.

    Args:
      format: file format - ics, md, csv, orgmode, txt
    """

    if format == "json":
        return [
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
            for s in sessions
        ]

    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        for k, v in metadata.items():
            writer.writerow([k, v])
        writer.writerow([])
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
        return output.getvalue()

    elif format == "txt":
        lines = [f"{k}: {v}" for k, v in metadata.items()] + ["-" * 40, ""]
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            lines.append(
                f"Title: {s.title}\nDate: {s.scheduled_date}, {s.start_time_str} - {s.end_time_str}\n"  # noqa: E501
                f"Hall: {s.hall}\nCategory: {s.category}\nCFP: {s.get('cfp_route') or 'N/A'}\n"
                f"Speakers: {speakers}\n{'-' * 40}"
            )
        return "\n".join(lines)

    elif format == "pdf":
        html = f"<h2>{metadata['Event Name']}</h2><p>"
        for k, v in metadata.items():
            html += f"<b>{k}:</b> {v}<br>"
        html += "</p><hr><ul>"
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            html += f"<li><b>{s.title}</b><br><b>Date:</b> {s.scheduled_date}<br><b>Time:</b> {s.start_time_str} - {s.end_time_str}<br><b>Hall:</b> {s.hall}<br><b>Category:</b> {s.category}<br><b>CFP:</b> {s.get('cfp_route') or 'N/A'}<br><b>Speakers:</b> {speakers}</li><br>"  # noqa: E501
        html += "</ul>"
        return get_pdf(html)

    elif format == "ics":
        cal = Calendar()
        cal.extra.append(
            ContentLine(
                name="X-WR-CALDESC",
                value="\n".join([f"{k}: {v}" for k, v in metadata.items()]),
            )
        )
        tz = ZoneInfo(frappe.db.get_single_value("System Settings", "time_zone") or "Asia/Kolkata")
        for s in sessions:
            e = Event()
            e.name = f"{s.title} - {doc.event_name}"
            start = datetime.combine(
                s.scheduled_date, (datetime.min + s.start_time).time(), tzinfo=tz
            )
            end = datetime.combine(s.scheduled_date, (datetime.min + s.end_time).time(), tzinfo=tz)
            if end <= start:
                continue
            e.begin = start
            e.end = end
            e.location = f"{s.hall}, {metadata['Location']}"
            e.description = f"Category: {s.category or 'N/A'}\nSpeakers: {', '.join([sp.get('name') for sp in s.speakers_list])}"  # noqa: E501
            cal.events.add(e)
        return str(cal)

    elif format == "md":
        lines = [
            f"# {metadata['Event Name']}",
            "",
            f"**Type:** {metadata['Event Type']}",
            f"**Route:** [{metadata['Event Route']}]({metadata['Event Route']})",
            f"**Location:** {metadata['Location']}",
        ]
        if metadata["Map Link"]:
            lines.append(f"**Map Link:** [{metadata['Map Link']}]({metadata['Map Link']})")
        lines += ["", "## Description", metadata["Description"], "", "## Schedule"]
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            lines += [
                f"### {s.title}",
                f"- **Date:** {s.scheduled_date}",
                f"- **Time:** {s.start_time_str} - {s.end_time_str}",
                f"- **Hall:** {s.hall}",
                f"- **Category:** {s.category}",
                f"- **CFP:** {s.get('cfp_route') or 'N/A'}",
                f"- **Speakers:** {speakers}",
                "",
                "---",
                "",
            ]
        return "\n".join(lines)

    elif format == "org":
        lines = [
            f"* {metadata['Event Name']}",
            ":PROPERTIES:",
            f":Type: {metadata['Event Type']}",
            f":Route: {metadata['Event Route']}",
            f":Location: {metadata['Location']}",
        ]
        if metadata["Map Link"]:
            lines.append(f":Map_Link: {metadata['Map Link']}")
        lines += [
            ":END:",
            "",
            "* Description",
            metadata["Description"],
            "",
            "* Schedule",
        ]
        for s in sessions:
            speakers = ", ".join([sp.get("name") for sp in s.speakers_list]) or "N/A"
            dt_str = f"<{s.scheduled_date} {str(s.start_time)[:5]}-{str(s.end_time)[:5]}>"
            lines += [
                f"** {s.title}",
                f"SCHEDULED: {dt_str}",
                ":PROPERTIES:",
                f":Hall: {s.hall}",
                f":Category: {s.category}",
                f":CFP: {s.get('cfp_route') or 'N/A'}",
                f":Speakers: {speakers}",
                ":END:",
                "",
            ]
        return "\n".join(lines)

    else:
        supported = ["ics", "csv", "txt", "md", "org", "json", "pdf"]
        frappe.throw(
            _("Unsupported format: {0}. Supported formats: {1}").format(
                format, ", ".join(supported)
            )
        )


def build_response(format, content, filename, empty=False, event_metadata=None):
    """
    Build response for the API call to download.
    Adds mimetype to file.
    """

    if format in ["txt", "md", "org"]:
        frappe.response["type"] = "download"
        frappe.response["filename"] = f"{filename}.{format}"
        frappe.response["filecontent"] = content
        frappe.response["headers"] = {
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Disposition": f"attachment; filename={filename}.{format}",
        }
        return

    if format == "pdf":
        frappe.response["type"] = "download"
        frappe.response["filename"] = f"{filename}.pdf"
        frappe.response["filecontent"] = content
        return as_pdf()

    if format == "ics":
        frappe.response["type"] = "download"
        frappe.response["filename"] = f"{filename}.ics"
        frappe.response["filecontent"] = content
        frappe.response["headers"] = {
            "Content-Type": "text/calendar; charset=utf-8",
            "Content-Disposition": f"attachment; filename={filename}.ics",
        }
        return

    if format == "csv":
        frappe.response["doctype"] = filename
        frappe.response["result"] = content
        return as_csv()

    if format == "json":
        frappe.response["doctype"] = filename
        frappe.response["result"] = {
            "event_metadata": event_metadata or {},
            "sessions": content if not empty else [],
        }
        return as_json()

    # fallback
    frappe.response["result"] = content
