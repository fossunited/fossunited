import csv
import io
import re
from collections import defaultdict
from datetime import datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

import frappe
from frappe import _, local
from frappe.utils.response import as_csv, as_json
from ics import Calendar, Event
from ics.grammar.parse import ContentLine

from fossunited.doctype_ids import EVENT, EVENT_SCHEDULE, PROPOSAL, SPEAKER


def to_time(val):
    """Convert None / datetime.time / timedelta / "HH:MM[:SS]" to datetime.time."""
    if val is None:
        return None
    if isinstance(val, time):
        return val
    if isinstance(val, timedelta):
        return (datetime.min + val).time()
    if isinstance(val, str):
        fmt = "%H:%M:%S" if val.count(":") == 2 else "%H:%M"
        return datetime.strptime(val.strip(), fmt).time()
    raise TypeError(f"Unsupported time type: {type(val)}")


def _csv_safe(value):
    s = "" if value is None else str(value)
    return "'" + s if s.startswith(("=", "+", "-", "@")) else s


def _speaker_name(sp):
    if isinstance(sp, dict):
        return (sp.get("name") or sp.get("full_name") or "").strip()
    return str(sp or "").strip()


# Only published event data is returned. No sensitive fields exposed.
# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def get_event_schedule(event_id: str, doctype: str = EVENT) -> dict:
    """
    Returns event schedule grouped by ISO date (YYYY-MM-DD) and hall.
    Format: {"YYYY-MM-DD": {"Hall Name": [sessions...]}}
    """
    sessions = frappe.db.get_all(
        EVENT_SCHEDULE,
        {"parent": event_id, "parenttype": doctype},
        ["*"],
        order_by="scheduled_date asc, start_time asc",
    )

    unique_dates = sorted({s["scheduled_date"] for s in sessions})
    date_to_day = {d.strftime("%Y-%m-%d"): i + 1 for i, d in enumerate(unique_dates)}

    linked_cfps = list({s["linked_cfp"] for s in sessions if s.get("linked_cfp")})

    route_lookup, speakers_lookup = {}, {}
    if linked_cfps:
        for row in frappe.db.get_all(PROPOSAL, {"name": ("in", linked_cfps)}, ["name", "route"]):
            route_lookup[row["name"]] = row["route"]
        for sp in frappe.db.get_all(
            SPEAKER,
            {"parent": ("in", linked_cfps)},
            [
                "parent",
                "full_name",
                "designation",
                "organization",
                "bio",
                "photo",
                "social_link",
            ],
        ):
            speakers_lookup.setdefault(sp.pop("parent"), []).append(sp)

    grouped = defaultdict(lambda: defaultdict(list))
    for s in sessions:
        date_str = s["scheduled_date"].strftime("%Y-%m-%d")
        s["day"] = date_to_day[date_str]
        cfp = s.get("linked_cfp")
        s["cfp_route"] = route_lookup.get(cfp) if cfp else None
        s["cfp_speakers"] = speakers_lookup.get(cfp, []) if cfp else []
        grouped[date_str][s.get("hall") or "General"].append(s)

    return {date: dict(halls) for date, halls in sorted(grouped.items())}


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
def download_schedule(
    event: str,
    format: Literal["ics", "csv", "txt", "md", "org", "json", "markdown", "orgmode"] = "ics",
    days: str | None = None,
    halls: str | None = None,
):
    """Download Event Schedule (ics/csv/txt/md/org/json) for given days and halls."""
    days_list = (
        local.request.args.getlist("days") if local.request else (days.split(",") if days else [])
    )
    halls_list = (
        local.request.args.getlist("halls")
        if local.request
        else (halls.split(",") if halls else [])
    )

    days_dates = []
    for d in days_list:
        try:
            days_dates.append(datetime.strptime(d.strip(), "%Y-%m-%d").date())
        except ValueError as e:
            frappe.log_error(f"Invalid date: {d}. {e}", "Download Schedule")

    doc = frappe.get_doc(EVENT, event)
    sessions = _filtered_sessions(doc, days_dates, halls_list)

    metadata = {
        "Event Name": doc.event_name,
        "Event Type": doc.event_type,
        "Event Route": f"https://fossunited.org/{str(doc.route).lstrip('/')}" if doc.route else "",
        "Location": doc.event_location or "Online",
        "Map Link": doc.map_link or "",
        "Description": frappe.utils.strip_html(doc.event_description or "") or "N/A",
    }

    fname = re.sub(r"[^A-Za-z0-9._-]+", "_", doc.event_name)
    if days_dates:
        fname += "-Days-" + "-".join(d.strftime("%Y-%m-%d") for d in days_dates)
    if halls_list:
        fname += "-Halls-" + "-".join(re.sub(r"[^A-Za-z0-9._-]+", "_", h) for h in halls_list)

    fmt = {"orgmode": "org", "markdown": "md"}.get(str(format).lower(), format)

    if not sessions:
        return _build_response(fmt, None, fname, empty=True, metadata=metadata)

    content = _format_content(fmt, doc, sessions, metadata)
    return _build_response(fmt, content, fname, metadata=metadata)


def _filtered_sessions(doc, days_dates, halls_list):
    sessions, linked_cfps = [], set()

    for s in doc.event_schedule:
        sd = s.scheduled_date.date() if hasattr(s.scheduled_date, "date") else s.scheduled_date
        if days_dates and sd not in days_dates:
            continue
        if halls_list and s.hall not in halls_list:
            continue
        if s.get("linked_cfp"):
            linked_cfps.add(s.linked_cfp)
        sessions.append(s)

    route_lookup, cfp_speakers = {}, {}
    if linked_cfps:
        for row in frappe.db.get_all(
            PROPOSAL, {"name": ("in", list(linked_cfps))}, ["name", "route"]
        ):
            route_lookup[row["name"]] = row["route"]
        for sp in frappe.db.get_all(
            SPEAKER, {"parent": ("in", list(linked_cfps))}, ["parent", "full_name"]
        ):
            cfp_speakers.setdefault(sp["parent"], []).append(sp)

    for s in sessions:
        s.start_time_str = to_time(s.start_time).strftime("%H:%M") if s.start_time else ""
        s.end_time_str = to_time(s.end_time).strftime("%H:%M") if s.end_time else ""
        cfp = s.get("linked_cfp")
        s.cfp_route = (
            f"https://fossunited.org/{route_lookup[cfp]}" if cfp and cfp in route_lookup else ""
        )
        s.speakers_list = [
            sp["full_name"] for sp in cfp_speakers.get(cfp, []) if sp.get("full_name")
        ]

    return sessions


def _format_content(fmt, doc, sessions, meta):
    if fmt == "json":
        return [
            {
                "title": s.title,
                "date": str(s.scheduled_date),
                "start_time": s.start_time_str,
                "end_time": s.end_time_str,
                "hall": s.hall,
                "category": s.category,
                "cfp_route": getattr(s, "cfp_route", ""),
                "speakers": s.speakers_list,
            }
            for s in sessions
        ]

    if fmt == "csv":
        out = io.StringIO()
        w = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
        w.writerow(
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
            spk = ", ".join(_speaker_name(sp) for sp in s.speakers_list if _speaker_name(sp))
            w.writerow(
                [
                    _csv_safe(v)
                    for v in [
                        s.title,
                        s.scheduled_date,
                        s.start_time_str,
                        s.end_time_str,
                        s.hall,
                        s.category,
                        getattr(s, "cfp_route", ""),
                        spk,
                    ]
                ]
            )
        return "\ufeff" + out.getvalue()

    if fmt == "txt":
        lines = [f"{k}: {v}" for k, v in meta.items()] + ["-" * 40, ""]
        for s in sessions:
            spk = ", ".join(_speaker_name(sp) for sp in s.speakers_list if _speaker_name(sp)) or ""
            lines.append(
                f"Title: {s.title}\nDate: {s.scheduled_date}, {s.start_time_str} - {s.end_time_str}\n"  # noqa: E501
                f"Hall: {s.hall}\nCategory: {s.category}\nCFP: {getattr(s, 'cfp_route', '')}\n"
                f"Speakers: {spk}\n{'-' * 40}"
            )
        return "\n".join(lines)

    if fmt == "md":
        lines = [
            f"# {meta['Event Name']}",
            "",
            f"**Type:** {meta['Event Type']}",
            f"**Location:** {meta['Location']}",
            "",
            "## Schedule",
        ]
        for s in sessions:
            spk = ", ".join(_speaker_name(sp) for sp in s.speakers_list if _speaker_name(sp)) or ""
            lines += [
                f"### {s.title}",
                f"- **Date:** {s.scheduled_date}",
                f"- **Time:** {s.start_time_str} - {s.end_time_str}",
                f"- **Hall:** {s.hall}",
                f"- **Category:** {s.category}",
                f"- **Speakers:** {spk}",
                "",
                "---",
                "",
            ]
        return "\n".join(lines)

    if fmt == "org":
        lines = [
            f"* {meta['Event Name']}",
            ":PROPERTIES:",
            f":Location: {meta['Location']}",
            ":END:",
            "",
            "* Schedule",
        ]
        for s in sessions:
            spk = ", ".join(_speaker_name(sp) for sp in s.speakers_list if _speaker_name(sp)) or ""
            t0, t1 = to_time(s.start_time), to_time(s.end_time)
            dt = (
                f"<{s.scheduled_date} {t0.strftime('%H:%M')}-{t1.strftime('%H:%M')}>"
                if t0 and t1
                else f"<{s.scheduled_date}>"
            )
            lines += [
                f"** {s.title}",
                f"SCHEDULED: {dt}",
                ":PROPERTIES:",
                f":Hall: {s.hall}",
                f":Category: {s.category}",
                f":CFP: {getattr(s, 'cfp_route', '')}",
                f":Speakers: {spk}",
                ":END:",
                "",
            ]
        return "\n".join(lines)

    if fmt == "ics":
        cal = Calendar()
        cal.extra.append(
            ContentLine(
                name="X-WR-CALDESC",
                value="\n".join(f"{k}: {v}" for k, v in meta.items()),
            )
        )
        tz = ZoneInfo(frappe.db.get_single_value("System Settings", "time_zone") or "Asia/Kolkata")
        for s in sessions:
            if not (s.scheduled_date and s.start_time and s.end_time):
                continue
            t0, t1 = to_time(s.start_time), to_time(s.end_time)
            if not t0 or not t1:
                continue
            start = datetime.combine(s.scheduled_date, t0, tzinfo=tz)
            end = datetime.combine(s.scheduled_date, t1, tzinfo=tz)
            if end <= start:
                continue
            e = Event()
            e.name = f"{s.title} - {doc.event_name}"
            e.begin, e.end = start, end
            e.location = f"{s.hall}, {meta['Location']}"
            spk = ", ".join(_speaker_name(sp) for sp in s.speakers_list if _speaker_name(sp))
            e.description = f"Category: {s.category or ''}\nSpeakers: {spk}"
            cal.events.add(e)
        return cal.serialize()

    frappe.throw(_("Unsupported format: {0}").format(fmt))


def _send_file(fname, ext, content, content_type):
    frappe.response.update(
        {"type": "download", "filename": f"{fname}.{ext}", "filecontent": content}
    )
    if content_type:
        frappe.response["headers"] = {
            "Content-Type": content_type,
            "Content-Disposition": f"attachment; filename={fname}.{ext}",
        }


def _build_response(fmt, content, fname, empty=False, metadata=None):
    if empty:
        if fmt == "json":
            frappe.response.update(
                {
                    "doctype": fname,
                    "result": {"metadata": metadata or {}, "sessions": []},
                }
            )
            return as_json()
        if fmt == "csv":
            out = io.StringIO()
            csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\r\n").writerow(
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
            frappe.response.update({"doctype": fname, "result": "\ufeff" + out.getvalue()})
            return as_csv()
        if fmt == "ics":
            _send_file(fname, "ics", Calendar().serialize(), "text/calendar; charset=utf-8")
            return
        content = "No matching sessions found."

    if fmt in ("txt", "md", "org"):
        ct = "text/markdown; charset=utf-8" if fmt == "md" else "text/plain; charset=utf-8"
        _send_file(fname, fmt, content, ct)
        return
    if fmt == "ics":
        _send_file(fname, "ics", content, "text/calendar; charset=utf-8")
        return
    if fmt == "csv":
        frappe.response.update({"doctype": fname, "filename": f"{fname}.csv", "result": content})
        return as_csv()
    if fmt == "json":
        frappe.response.update(
            {
                "doctype": fname,
                "result": {"metadata": metadata or {}, "sessions": content},
            }
        )
        return as_json()
    frappe.response["result"] = content
