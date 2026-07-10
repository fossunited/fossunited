"""Shared helpers for Event Media pages (archive grid + speakers pages).

The core query/aggregation functions are event-agnostic: pass a `get_all`
scope (`or_filters`/`filters`) to choose which Event Media rows to operate on,
and an `edition_order` map for sorting. The IndiaFOSS layer at the bottom is a
thin wrapper that pins the IndiaFOSS scope + edition order and adds caching;
other events can add their own wrappers later without touching the core.
"""

import frappe
from frappe.utils.caching import redis_cache

from fossunited.doctype_ids import DEFAULT_USER_PHOTO, EVENT_MEDIA, PROPOSAL, SPEAKER, USER_PROFILE
from fossunited.fossunited.utils import get_youtube_id

# ---------------------------------------------------------------------------
# Generic core (event-agnostic): operate on any set of Event Media rows.
# ---------------------------------------------------------------------------


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


def fetch_speaker_rows(parents, parenttype, parentfield="speakers"):
    """{parent_name: [{name, photo, user, designation, organization, social_link}, ...]}
    from CFP Submission Speaker rows attached to the given parents."""
    if not parents:
        return {}
    rows = frappe.get_all(
        SPEAKER,
        filters={
            "parent": ["in", list(parents)],
            "parentfield": parentfield,
            "parenttype": parenttype,
        },
        fields=[
            "parent",
            "full_name",
            "photo",
            "linked_user",
            "designation",
            "organization",
            "social_link",
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
                    "social_link": r.social_link or "",
                }
            )
    return grouped


def get_event_media(or_filters=None, filters=None, edition_order=None):
    """Event Media rows that have somewhere to go (playable video or proposal link),
    enriched for rendering: youtube_id, duration_str, edition (+order), merged
    speakers, link/external.

    Scope the rows with `or_filters`/`filters` (passed straight to frappe.get_all).
    `edition_order` maps an edition label -> chronological sort index (default 99).
    Speakers are merged from the linked proposal when present, else from the
    media's own `speakers` child table -- two bulk queries, no per-row lookups.
    """
    edition_order = edition_order or {}
    media = frappe.get_all(
        EVENT_MEDIA,
        or_filters=or_filters,
        filters=filters,
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

    prop_speakers = fetch_speaker_rows({m.proposal for m in media if m.proposal}, PROPOSAL)
    own_speakers = fetch_speaker_rows({m.name for m in media if not m.proposal}, EVENT_MEDIA)

    for m in media:
        m.youtube_id = get_youtube_id(m.video_url)
        m.duration_str = duration_str(m.duration)
        m.edition = edition_label(m.event_name)
        m.edition_order = edition_order.get(m.edition, 99)
        # video_type is auto-populated from the proposal via fetch_from (set in Desk).
        m.speakers = (
            prop_speakers.get(m.proposal, []) if m.proposal else own_speakers.get(m.name, [])
        )
        m.speaker = ", ".join(s["name"] for s in m.speakers)  # single-line + search key
        # Card destination: proposal page if set (internal route or external URL),
        # else the video. External links open in a new tab.
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


def _speaker_key(row):
    # frappe.scrub: lowercase + non-alnum -> "_" (e.g. "Jane Doe" -> "jane_doe").
    # Speaker names are plain (no punctuation), so scrub is enough for a URL slug.
    return row["user"] or frappe.scrub(row["name"])


def _profiles(user_names):
    """{profile_name: {profile_photo, route, full_name, linkedin, x, instagram, github, website}}"""
    if not user_names:
        return {}
    rows = frappe.get_all(
        USER_PROFILE,
        filters={"name": ["in", list(user_names)]},
        fields=[
            "name",
            "profile_photo",
            "route",
            "full_name",
            "linkedin",
            "x",
            "instagram",
            "github",
            "website",
        ],
    )
    return {r.name: r for r in rows}


def _avatar(row, profile):
    return row["photo"] or (profile.get("profile_photo") if profile else "") or DEFAULT_USER_PHOTO


def build_speakers_index(media, edition_order=None):
    """Aggregate every speaker across a media set into
    `{"speakers": [rec, ...], "slugs": {slug: key}}`.

    Aggregation key = `linked_user` if set, else the name slug. The URL slug is
    always name-based, with `-2`/`-3` suffixes disambiguating distinct speakers
    whose names slugify identically. One bulk profile query; the rest is pure.
    """
    edition_order = edition_order or {}
    users = {s["user"] for m in media for s in m.speakers if s["user"]}
    profiles = _profiles(users)

    agg = {}
    for m in media:
        for s in m.speakers:
            key = _speaker_key(s)
            rec = agg.get(key)
            if not rec:
                profile = profiles.get(s["user"]) or {}
                rec = agg[key] = {
                    "key": key,
                    "slug": frappe.scrub(s["name"]),
                    "name": s["name"],
                    "designation": s["designation"],
                    "organization": s["organization"],
                    "avatar": _avatar(s, profile),
                    "profile_route": ("/" + profile["route"]) if profile.get("route") else "",
                    "_media": set(),
                    "editions": set(),
                    "types": set(),
                }
            rec["_media"].add(m.name)
            if m.edition:
                rec["editions"].add(m.edition)
            if m.video_type:
                rec["types"].add(m.video_type)

    slugs, taken = {}, {}
    speakers = []
    for rec in sorted(agg.values(), key=lambda r: r["name"].lower()):
        base = rec["slug"]
        n = taken.get(base, 0) + 1
        taken[base] = n
        slug = base if n == 1 else f"{base}-{n}"
        rec["slug"] = slug
        slugs[slug] = rec["key"]
        rec["talk_count"] = len(rec.pop("_media"))
        rec["editions"] = sorted(rec["editions"], key=lambda e: (edition_order.get(e, 99), e))
        rec["types"] = sorted(rec["types"])
        speakers.append(rec)

    return {"speakers": speakers, "slugs": slugs}


def build_speaker_talks(media, key):
    """Speaker meta + their talks (tiered content) for one aggregation key, drawn
    from `media`. None if the key appears in no media row."""
    talks = [m for m in media if any(_speaker_key(s) == key for s in m.speakers)]
    if not talks:
        return None

    # Speaker meta from the first row that carries this key.
    row = next(s for m in talks for s in m.speakers if _speaker_key(s) == key)
    profile = _profiles({row["user"]}).get(row["user"], {}) if row["user"] else {}
    socials = {}
    if profile:
        for f in ("linkedin", "x", "instagram", "github", "website"):
            if profile.get(f):
                socials[f] = profile[f]
    elif row["social_link"]:
        socials["website"] = row["social_link"]
    speaker = {
        "name": row["name"],
        "designation": row["designation"],
        "organization": row["organization"],
        "avatar": _avatar(row, profile),
        "profile_route": ("/" + profile["route"]) if profile.get("route") else "",
        "socials": socials,
    }

    # Proposal description for internal-proposal talks (one bulk query).
    prop_names = {m.proposal for m in talks if m.proposal}
    content = {}
    if prop_names:
        for p in frappe.get_all(
            PROPOSAL,
            filters={"name": ["in", list(prop_names)]},
            fields=["name", "talk_description"],
        ):
            content[p.name] = p
    refs = fetch_reference_links(prop_names)

    talks = sorted(talks, key=lambda m: (m.edition_order, m.title))
    for m in talks:
        if m.proposal:
            m.description = (content.get(m.proposal) or {}).get("talk_description") or ""
            m.references = refs.get(m.proposal, [])
            m.tier = "internal"
        elif m.proposal_route:  # external proposal (e.g. IF3)
            m.description = ""
            m.references = []
            m.tier = "external"
        else:  # video-only (e.g. IF1/2)
            m.description = ""
            m.references = []
            m.tier = "video"

    return {"speaker": speaker, "talks": talks}


def fetch_reference_links(proposals):
    """{proposal_name: [url, ...]} from the CFP Submission Reference child rows."""
    if not proposals:
        return {}
    rows = frappe.get_all(
        "CFP Submission Reference",
        filters={"parent": ["in", list(proposals)], "parenttype": PROPOSAL},
        fields=["parent", "link"],
        order_by="idx asc",
    )
    out = {}
    for r in rows:
        if r.link:
            out.setdefault(r.parent, []).append(r.link)
    return out


# ---------------------------------------------------------------------------
# IndiaFOSS layer: pins the scope + edition order and caches the index.
# Add a sibling layer per event in future; the core above stays untouched.
# ---------------------------------------------------------------------------

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

# Event Media rows belonging to IndiaFOSS (any edition, incl. "Workshops @ ..." and IndiaOS).
INDIAFOSS_MEDIA_SCOPE = [
    ["event_name", "like", "%IndiaFOSS%"],
    ["event_name", "like", "%IndiaOS%"],
]


def get_indiafoss_years():
    return [
        {"year": "2026", "url": "/indiafoss/2026", "name": "IndiaFOSS 2026"},
        {"year": "2025", "url": "/indiafoss/2025", "name": "IndiaFOSS 2025"},
        {"year": "2024", "url": "/indiafoss/2024", "name": "IndiaFOSS 2024"},
        {"year": "2023", "url": "/indiafoss/2023", "name": "IndiaFOSS 3.0"},
        {"year": "2021", "url": "/indiafoss/2022", "name": "IndiaFOSS 2.0"},
        {"year": "2020", "url": "/indiafoss/2021", "name": "IndiaOS"},
    ]


def get_indiafoss_media():
    """All IndiaFOSS Event Media, enriched (see get_event_media)."""
    return get_event_media(or_filters=INDIAFOSS_MEDIA_SCOPE, edition_order=EDITION_ORDER)


# Back-compat alias: the archive page imports get_archive_media. Same data now,
# including own-child speakers for pre-proposal editions (IF1/2/3).
get_archive_media = get_indiafoss_media


@redis_cache(ttl=86400)
def get_speakers_index():
    """IndiaFOSS speaker index, cached. Invalidated by clear_speakers_cache."""
    return build_speakers_index(get_indiafoss_media(), edition_order=EDITION_ORDER)


def get_speaker_talks(slug):
    """IndiaFOSS speaker + their talks by URL slug. None if the slug is unknown."""
    key = get_speakers_index()["slugs"].get(slug)
    if not key:
        return None
    return build_speaker_talks(get_indiafoss_media(), key)


def clear_speakers_cache(doc=None, method=None):
    get_speakers_index.clear_cache()
