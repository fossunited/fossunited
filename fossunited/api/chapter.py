import ast
from zoneinfo import ZoneInfo

import frappe
from ics import Calendar, Event

from fossunited.doctype_ids import (
    CHAPTER,
    CHAPTER_MEMBER,
    EVENT,
    EVENT_VOLUNTEER,
    RSVP_CUSTOM_FIELD,
    RSVP_RESPONSE,
    USER_PROFILE,
)


@frappe.whitelist(allow_guest=True)
def check_if_chapter_member(chapter: str, user: str) -> bool:
    """
    Check if the user is a member of the chapter.

    Args:
        chapter (str): Chapter id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": user}, ["name"])

    if not profile:
        return False

    is_member = bool(
        frappe.db.exists(
            CHAPTER_MEMBER,
            {
                "parent": chapter,
                "parenttype": CHAPTER,
                "chapter_member": profile,
                "parentfield": "chapter_members",
            },
        )
    )

    return is_member


@frappe.whitelist(allow_guest=True)
def check_if_event_lead(event: str) -> bool:
    """
    Check if the user is an event lead

    Args:
        event (str): Event id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": frappe.session.user}, ["name"])

    is_lead = bool(
        frappe.db.exists(
            EVENT_VOLUNTEER,
            {
                "parent": event,
                "parenttype": EVENT,
                "member": profile,
                "parentfield": "event_members",
                "role": "Core Team Member",
            },
        )
    )

    return is_lead


@frappe.whitelist(allow_guest=True)
def check_if_chapter_or_event_core_member(event: str) -> bool:
    """
    A common function to check if user is either chapter or event member to give some access.
    This API function is intended to only apply for cases where every time event is created
    they would not add themselves to event_members table
    """
    event_doc = frappe.get_doc(EVENT, event, ["name"])
    chapter_id = event_doc.chapter
    is_team = bool(
        check_if_event_lead(event) or check_if_chapter_member(chapter_id, frappe.session.user)
    )
    return is_team


@frappe.whitelist(allow_guest=True)
def generate_ics(event_ids):
    """
    Return ICS event for the event ids provided

    Args:
        event_ids (list): list of event ids (doc.name)

    Returns:
        str: ICS data
    """

    c = Calendar()
    ids = ast.literal_eval(event_ids)

    events = frappe.db.get_all(
        EVENT,
        filters=[["name", "IN", ids]],
        fields=[
            "event_name",
            "event_location",
            "chapter_name",
            "event_description",
            "route",
            "event_start_date",
            "event_end_date",
        ],
    )
    for event in events:
        tz_name = frappe.db.get_single_value("System Settings", "time_zone") or "Asia/Kolkata"
        tz = ZoneInfo(tz_name)
        start_dt = frappe.utils.get_datetime(event.event_start_date)
        end_dt = frappe.utils.get_datetime(event.event_end_date)
        # If naive, treat as local time in site TZ; if aware, convert
        start = start_dt.replace(tzinfo=tz) if start_dt.tzinfo is None else start_dt.astimezone(tz)
        end = end_dt.replace(tzinfo=tz) if end_dt.tzinfo is None else end_dt.astimezone(tz)

        # Skip if end is before start
        if end < start:
            continue

        e = Event()
        e.name = event.event_name
        e.location = event.event_location
        e.organizer = event.chapter_name + " Community"
        # Optional hardening (keep if desired):
        e.description = frappe.utils.strip_html(event.event_description or "") or None
        if event.route:
            e.url = f"https://fossunited.org/{str(event.route).lstrip('/')}"
        e.begin = start
        e.end = end
        c.events.add(e)

    return c.serialize()


@frappe.whitelist()
def get_submissions_with_answers(
    event_id: str,
    full_answers: bool = False,
) -> list[dict]:
    """
    Provide RSVP submission with answers for EventInsights.

    Args:
        event_id (str): Event ID
        full_answers (bool): If True, return full question labels and responses;
                     otherwise truncate for UI display. Applicable for csv export/download.
    Returns:
        List of submission dicts with custom field answers for core team members.
    """
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)

    # Get basic submission fields
    submissions = frappe.get_all(
        RSVP_RESPONSE,
        filters={"event": event_id},
        fields=["name", "confirm_attendance", "name1", "email", "im_a"],
        order_by="creation asc",
        limit_page_length=9999,
    )

    if not check_if_chapter_or_event_core_member(event_id):
        for s in submissions:
            s["email"] = mask_email(s.get("email"))
            s.pop("name", None)
        return submissions

    # Event lead: fetch full answers
    submission_ids = [s["name"] for s in submissions]
    if not submission_ids:
        return submissions

    answers_rows = frappe.get_all(
        RSVP_CUSTOM_FIELD,
        filters={
            "parent": ["in", submission_ids],
            "parenttype": RSVP_RESPONSE,
            "parentfield": "custom_answers",
        },
        fields=["parent", "question", "response", "idx"],
        order_by="parent asc, idx asc",
        limit_page_length=0,
    )

    answers_by_parent = {}
    for a in answers_rows:
        answers_by_parent.setdefault(a["parent"], []).append(a)

    for s in submissions:
        for a in answers_by_parent.get(s["name"], []):
            key = _safe_column_key(a["question"])  # always max 50 chars

            # Truncate the answer if not full
            response = a.get("response")
            if response is None:
                response = ""
            if not full_answers:
                response = _truncate_label(str(response), 30)

            s[f"{key}"] = response

            # Truncate label if not full
            raw_label = a.get("question")
            label = "" if raw_label is None else str(raw_label)
            if not full_answers:
                label = _truncate_label(label, 30)

        s.pop("name", None)

    return submissions


def _safe_column_key(label: str) -> str:
    """
    Sanitize and shorten a label to create a safe dictionary/column key.
    This function:
    - Ensures the label is a string; otherwise returns 'custom_field'.
    - Normalizes whitespace and strips leading/trailing spaces.
    - Removes all characters except alphanumerics, underscores, spaces, and hyphens.
    - Replaces spaces with underscores.
    - Converts the label to lowercase.
    - Prefixes the key with an underscore if it starts with a dangerous character
      (i.e., '=', '+', '-', '@') to prevent CSV injection.
    - Truncates the key to a maximum of 50 characters.

    Args:
        label (str): The original label to sanitize.

    Returns:
        str: A sanitized, safe key string suitable for use in CSV headers or dict keys.

    """
    import re

    if not isinstance(label, str):
        return "custom_field"

    key = re.sub(r"\s+", " ", label).strip()  # Normalize spaces
    key = re.sub(r"[^\w\s-]", "", key)  # Remove special chars
    key = re.sub(r"\s+", "_", key).lower()  # Convert to snake_case

    if not key or key[0] in "=+-@":
        key = f"_{key}"

    return key[:50]  # Limit to 50 characters


def _truncate_label(label: str, max_length: int = 50) -> str:
    s = "" if label is None else str(label)
    s = " ".join(s.split())  # collapse whitespace/newlines
    return s if len(s) <= max_length else s[:max_length].rstrip() + "…"


def mask_email(email: str) -> str:
    """
    Mask email to reduce PII exposure:
    - Keep first 2 characters of local-part (or fewer if not available).
    - For local-part length <= 2: keep first char, mask rest
    - For 3 <= length <= 8: show first 3, mask the middle, show last
    - For length > 8: show first 2, one middle char, show last
    - Keep domain intact.
    """
    if not email or "@" not in email:
        return "***"

    local, domain = email.split("@", 1)
    local_len = len(local)

    if local_len <= 2:
        visible = local[0] + "*" * (local_len - 1)
    elif local_len <= 8:
        visible = local[:3] + "*" * (local_len - 3)
    else:
        mid_index = local_len // 2
        visible = (
            local[:2]
            + "*" * (mid_index - 2)
            + local[mid_index]
            + "*" * (local_len - mid_index - 2)
            + local[-1]
        )

    return f"{visible}@{domain}"


@frappe.whitelist()
def download_attendee_list_csv(event_id: str) -> str:
    """
    Generates and returns a CSV string of RSVP submissions with custom field answers.
    Accessible only by core team / event leads.
    """
    import csv
    import io
    import re

    # Get full submission data (each is a dict)
    submissions = get_submissions_with_answers(event_id, full_answers=True)

    if not submissions:
        return ""

    # Start with keys from the first row to preserve order
    columns = list(submissions[0].keys())
    seen = set(columns)

    # Add any new keys from other rows (if any), in the order they appear
    for row in submissions[1:]:
        for key in row.keys():
            if key not in seen:
                columns.append(key)
                seen.add(key)

    headers = columns

    # Escape helper (like toCSVCell)
    def cleanse_csv_cell(value):
        s = "" if value is None else str(value)
        if s.startswith(("=", "+", "-", "@")):
            s = "'" + s
        return s

    # Prepare CSV content
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\r\n")

    writer.writerow([cleanse_csv_cell(h) for h in headers])

    for row in submissions:
        writer.writerow([cleanse_csv_cell(row.get(col, "")) for col in columns])

    csv_data = "\ufeff" + output.getvalue()  # BOM for Excel

    # Create safe filename
    event_name = frappe.db.get_value(EVENT, event_id, "event_name", cache=True) or "event"
    safe_event_name = re.sub(r"[^A-Za-z0-9._-]+", "_", event_name)
    filename = f"Attendee_List_-_{safe_event_name}.csv"

    # Set file response
    frappe.response["filename"] = filename
    frappe.response["filecontent"] = csv_data
    frappe.response["content_type"] = "text/csv; charset=utf-8"
    frappe.response["type"] = "download"

    return csv_data
