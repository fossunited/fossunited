import ast
from datetime import timedelta, timezone

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
        e = Event()
        e.name = event.event_name
        e.location = event.event_location
        e.organizer = event.chapter_name + " Community"
        e.description = event.event_description
        e.url = "https://fossunited.org/" + str(event.route)
        e.begin = event.event_start_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        e.end = event.event_end_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        c.events.add(e)

    return c.serialize()


@frappe.whitelist()
def get_submissions_with_answers(event_id: str, full: bool = False) -> list[dict]:
    """
    Provide RSVP submission with answers for EventInsights.

    Args:
        event_id (str): Event ID
        full (bool): If True, return full question labels and responses;
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
        fields=["name", "name1", "email", "im_a"],
        order_by="creation asc",
    )

    if not check_if_event_lead(event_id):
        # Mask email and return limited data
        for s in submissions:
            s["email"] = mask_email(s.get("email"))
        return submissions

    # Event lead: fetch full answers
    submission_ids = [s["name"] for s in submissions]

    answers = frappe.get_all(
        RSVP_CUSTOM_FIELD,
        filters={
            "parent": ["in", submission_ids],
            "parenttype": RSVP_RESPONSE,
            "parentfield": "custom_answers",
        },
        fields=["parent", "question", "response"],
    )

    answers_by_parent = {}
    for a in answers:
        answers_by_parent.setdefault(a["parent"], []).append(a)

    for s in submissions:
        for a in answers_by_parent.get(s["name"], []):
            key = _safe_column_key(a["question"])  # always max 50 chars

            # Truncate the answer if not full
            response = a.get("response")
            if response is None:
                response = ""
            if not full:
                response = _truncate_label(str(response), 50)

            s[f"cf_{key}"] = response

            # Truncate label if not full
            raw_label = a.get("question")
            label = "" if raw_label is None else str(raw_label)
            if not full:
                label = _truncate_label(label, 50)

            s.setdefault("_answers", {})[f"cf_{key}"] = label

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
    - Truncates the key to a maximum of 80 characters.

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

    # Get full submission data (labels and answers)
    submissions = get_submissions_with_answers(event_id, full=True)

    if not submissions:
        return ""

    # Determine all columns
    base_keys = ["name1", "email", "im_a"]
    label_map = {"name1": "Name", "email": "Email", "im_a": "I am a"}

    custom_keys = sorted({key for s in submissions for key in s.keys() if key.startswith("cf_")})

    # Union labels from all rows
    labels = {}
    for s in submissions:
        if "_answers" in s and isinstance(s["_answers"], dict):
            labels.update(s["_answers"])
    columns = base_keys + custom_keys
    headers = [label_map.get(k, labels.get(k, k)) for k in columns]

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
    event_name = frappe.db.get_value(EVENT, event_id, "event_name", cache=True) or "event"

    safe_event_name = re.sub(r"[^A-Za-z0-9._-]+", "_", event_name)
    filename = f"Attendee_List_-_{safe_event_name}.csv"

    frappe.response["filename"] = filename
    frappe.response["filecontent"] = csv_data
    frappe.response["content_type"] = "text/csv; charset=utf-8"
    frappe.response["type"] = "download"
