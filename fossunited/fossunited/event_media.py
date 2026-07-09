"""Shared helpers for IndiaFOSS Event Media pages (/archive grid + /speakers page).

Keep query/format logic here so `www/indiafoss/archive/index.py` and a later
`www/indiafoss/speakers/index.py` build their contexts from the same functions.
"""

import frappe

from fossunited.doctype_ids import EVENT_MEDIA, PROPOSAL, SPEAKER
from fossunited.fossunited.utils import get_youtube_id

# Chronological order + canonical label per edition. Mirrors _get_indiafoss_years() in
# www/indiafoss/2026/index.py (cannot import it: the module path contains "2026").
EDITION_ORDER = {
    "IndiaOS": 1,
    "IndiaFOSS 2020": 1,
    "IndiaFOSS 2.0": 2,
    "IndiaFOSS 3.0": 3,
    "IndiaFOSS 2024": 4,
    "IndiaFOSS 2025": 5,
    "IndiaFOSS 2026": 6,
}


def get_indiafoss_years():
    return [
        {"year": "2026", "url": "/indiafoss/2026", "name": "IndiaFOSS 2026"},
        {"year": "2025", "url": "/indiafoss/2025", "name": "IndiaFOSS 2025"},
        {"year": "2024", "url": "/indiafoss/2024", "name": "IndiaFOSS 2024"},
        {"year": "2023", "url": "/indiafoss/2023", "name": "IndiaFOSS 3.0"},
        {"year": "2021", "url": "/indiafoss/2022", "name": "IndiaFOSS 2.0"},
        {"year": "2020", "url": "/indiafoss/2021", "name": "IndiaOS"},
    ]


def edition_label(event_name):
    """Strip a 'Workshops @ ' prefix so workshop videos fold into their edition."""
    return (event_name or "").removeprefix("Workshops @ ").strip()


def duration_str(seconds):
    seconds = int(seconds or 0)
    if not seconds:
        return ""
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def speaker_map(proposals):
    """{proposal_name: [{name, photo, user, designation, organization}, ...]} from the linked
    CFP submissions' speaker rows.
    """
    if not proposals:
        return {}
    rows = frappe.get_all(
        SPEAKER,
        filters={
            "parent": ["in", list(proposals)],
            "parentfield": "speakers",
            "parenttype": PROPOSAL,
        },
        fields=[
            "parent",
            "full_name",
            "photo",
            "linked_user",
            "designation",
            "organization",
        ],
        order_by="idx asc",
    )
    grouped = {}
    for r in rows:
        if r.full_name:
            grouped.setdefault(r.parent, []).append(
                {
                    "name": r.full_name,
                    "photo": r.photo or "",
                    "user": r.linked_user or "",
                    "designation": r.designation or "",
                    "organization": r.organization or "",
                }
            )
    return grouped


def get_archive_media():
    """All Event Media rows that have somewhere to go (playable video or proposal link),
    enriched for rendering: youtube_id, duration_str, edition (+order), speakers list, link."""
    media = frappe.get_all(
        EVENT_MEDIA,
        # Scope to IndiaFOSS (this is the IndiaFOSS archive; Event Media is a generic doctype
        # that will also hold other events' media). Covers "IndiaFOSS 2.0/3.0/2024/2025",
        # "Workshops @ IndiaFOSS 2025", and "IndiaOS" (2020).
        or_filters=[
            ["event_name", "like", "%IndiaFOSS%"],
            ["event_name", "like", "%IndiaOS%"],
        ],
        fields=[
            "name",
            "title",
            "video_url",
            "event_name",
            "proposal",
            "proposal_route",
            "video_type",
            "duration",
        ],
        order_by="title asc",
    )

    smap = speaker_map({m.proposal for m in media if m.proposal})

    for m in media:
        m.youtube_id = get_youtube_id(m.video_url)
        m.duration_str = duration_str(m.duration)
        m.edition = edition_label(m.event_name)
        m.edition_order = EDITION_ORDER.get(m.edition, 99)
        m.speakers = smap.get(m.proposal, [])
        m.speaker = ", ".join(s["name"] for s in m.speakers)  # single-line + search key
        # video_type is auto-populated from the proposal via fetch_from (set in Desk);
        # rendered directly, no fallback needed.
        # Card destination: proposal page if set (internal route or external IF3 URL),
        # else the YouTube video. External links open in a new tab.
        if m.proposal_route:
            m.external = m.proposal_route.startswith("http")
            m.link = m.proposal_route if m.external else "/" + m.proposal_route
        else:
            m.link = m.video_url
            m.external = True

    return [m for m in media if m.youtube_id or m.proposal_route]


def get_editions(media):
    """Distinct edition labels present, ordered chronologically."""
    seen = {m.edition: m.edition_order for m in media if m.edition}
    return sorted(seen, key=lambda e: (seen[e], e))


def get_session_types(media):
    """Full canonical session-type Select list (so the filter offers the complete variety,
    not just types present in data). Stray values (e.g. proposal-only types like BoF /
    Invited Talk not yet in the Event Media Select) are appended, never dropped."""
    present = {m.video_type for m in media if m.video_type}
    field = frappe.get_meta(EVENT_MEDIA).get_field("video_type")
    canonical = (
        [t.strip() for t in (field.options or "").splitlines() if t.strip()] if field else []
    )
    return canonical + sorted(t for t in present if t not in canonical)
