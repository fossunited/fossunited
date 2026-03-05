"""Seed development data for a fresh fossunited site.

Populates chapters, events, RSVPs, CFPs, and a hackathon so developers
can explore the application immediately after install.

Usage::

    bench --site <your-site> execute fossunited.seed.seed

Default credentials
-------------------
========== ============================================ ===========
Role       Email                                        Password
========== ============================================ ===========
Admin      Administrator                                (bench pwd)
Attendee   attendee-{1,2}@example.com                   password
Speaker    speaker-{1,2}@example.com                    password
Lead       {bangalore,mumbai,kochi,campus}-lead@...      password
========== ============================================ ===========

Idempotent — safe to run repeatedly on the same database.
"""

from datetime import datetime, timedelta

import frappe
import frappe.utils.password

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_CFP,
    EVENT_RSVP,
    HACKATHON,
    HACKATHON_PROJECT,
    STUDENT_CLUB,
    USER_PROFILE,
)
from fossunited.id.roles import CHAPTER_MEMBER as CHAPTER_TEAM_MEMBER_ROLE
from fossunited.tests.utils import (
    insert_cfp_form,
    insert_cfp_submission,
    insert_rsvp_form,
    insert_rsvp_submission,
    insert_test_chapter,
    insert_test_event,
    insert_test_hackathon,
    insert_test_hackathon_localhost,
    insert_test_hackathon_team,
    insert_user_profile,
)

logger = frappe.logger("seed", allow_site=True)

DEFAULT_PASSWORD = "password"

# String label used in the ``chapter_members`` child table to denote a core
# team member.  This is *not* a Frappe Role — it is a plain-text value stored
# in the ``role`` field of the child row.
CHAPTER_MEMBER_CHILD_TABLE_ROLE = "Core Team Member"


# ---------------------------------------------------------------------------
# Data declarations
# ---------------------------------------------------------------------------

SEED_USERS = [
    {
        "email": "attendee-1@example.com",
        "first_name": "Test",
        "last_name": "Attendee 1",
        "kind": "normal",
    },
    {
        "email": "attendee-2@example.com",
        "first_name": "Test",
        "last_name": "Attendee 2",
        "kind": "normal",
    },
    {
        "email": "speaker-1@example.com",
        "first_name": "Test",
        "last_name": "Speaker 1",
        "kind": "normal",
    },
    {
        "email": "speaker-2@example.com",
        "first_name": "Test",
        "last_name": "Speaker 2",
        "kind": "normal",
    },
    {
        "email": "bangalore-lead@example.com",
        "first_name": "Bangalore",
        "last_name": "Chapter Lead",
        "kind": "chapter",
        "chapter_slug": "foss-bangalore",
    },
    {
        "email": "mumbai-lead@example.com",
        "first_name": "Mumbai",
        "last_name": "Chapter Lead",
        "kind": "chapter",
        "chapter_slug": "foss-mumbai",
    },
    {
        "email": "kochi-lead@example.com",
        "first_name": "Kochi",
        "last_name": "Chapter Lead",
        "kind": "chapter",
        "chapter_slug": "foss-kochi",
    },
    {
        "email": "campus-lead@example.com",
        "first_name": "Campus",
        "last_name": "Chapter Lead",
        "kind": "chapter",
        "chapter_slug": "campus-chapter",
    },
]

# City Communities receive standard events (meetups, conferences, etc.).
# Student Clubs host hackathons only — they are excluded from event generation
# to prevent slug collisions when a club shares a city with a community
# (e.g. "FOSS Kochi" and "Campus Chapter" both in Kochi).
CHAPTER_DATA = [
    {
        "chapter_name": "FOSS Bangalore",
        "chapter_type": CITY_COMMUNITY,
        "city": "Bangalore",
        "state": "Karnataka",
        "email": "bangalore@fossunited.org",
        "slug": "foss-bangalore",
    },
    {
        "chapter_name": "FOSS Mumbai",
        "chapter_type": CITY_COMMUNITY,
        "city": "Mumbai",
        "state": "Maharashtra",
        "email": "mumbai@fossunited.org",
        "slug": "foss-mumbai",
    },
    {
        "chapter_name": "FOSS Kochi",
        "chapter_type": CITY_COMMUNITY,
        "city": "Kochi",
        "state": "Kerala",
        "email": "kochi@fossunited.org",
        "slug": "foss-kochi",
    },
    {
        "chapter_name": "Campus Chapter",
        "chapter_type": STUDENT_CLUB,
        "city": "Kochi",
        "state": "Kerala",
        "email": "campus@example.com",
        "slug": "campus-chapter",
    },
]

# Each template is expanded per city-community chapter.  Permalinks are
# derived from the chapter *slug* (not city name) to guarantee uniqueness
# even when multiple chapters share a city.
EVENT_TEMPLATES = [
    {
        "name": "{city} FOSS Meetup 2026",
        "permalink": "{slug}-foss-meetup-2026",
        "event_type": "Meet Up",
        "status": "Live",
        "is_published": 1,
        "day_offset": 30,
        "duration_hours": 6,
        "description": (
            "<p>Join us for the {city} FOSS Meetup 2026! A day of talks, "
            "demos, and networking with the local open-source community.</p>"
        ),
        "location": "Tech Hub, {city}",
        "bucket": "live",
    },
    {
        "name": "{city} FOSS Conference 2025",
        "permalink": "{slug}-foss-conf-2025",
        "event_type": "Conference",
        "status": "Concluded",
        "is_published": 1,
        "day_offset": -60,
        "duration_hours": 24,
        "description": (
            "<p>The {city} FOSS Conference 2025 brought together developers, "
            "designers, and advocates of free and open-source software.</p>"
        ),
        "location": "Convention Centre, {city}",
        "bucket": "concluded",
    },
    {
        "name": "{city} FOSS Workshop 2026 (Draft)",
        "permalink": "{slug}-foss-workshop-2026-draft",
        "event_type": "Workshop",
        "status": "Draft",
        "is_published": 0,
        "day_offset": 60,
        "duration_hours": 4,
        "description": (
            "<p>A hands-on workshop in {city} — still being planned. "
            "This event is not yet published.</p>"
        ),
        "location": "Co-working Space, {city}",
        "bucket": "draft",
    },
    {
        "name": "{city} Mini FOSS Hackathon",
        "permalink": "{slug}-mini-foss-hackathon",
        "event_type": "Hackathon",
        "status": "Live",
        "is_published": 1,
        "day_offset": 45,
        "duration_hours": 48,
        "description": (
            "<p>Build something cool over three days in {city} with "
            "guidance from mentors and peers. Work solo or in a team, "
            "start something new, or contribute to a FOSS project.</p>"
        ),
        "location": "Online",
        "bucket": "live",
    },
]

HACKATHON_CFG = {
    "name": "FOSSIT Hackathon",
    "permalink": "fossit-hackathon",
    "chapter_slug": "campus-chapter",
    "teams": ["Team Phoenix", "Team Aurora", "Team Nebula", "Team Comet"],
    "localhost": "Kochi LocalHost",
    "projects": [
        {
            "title": "OpenTrack — GPS Activity Tracker",
            "team_index": 0,
            "repo_link": "https://github.com/example/opentrack",
            "short_description": "A privacy-first GPS tracker for runners and cyclists.",
            "description": (
                "<p>OpenTrack is an open-source alternative to Strava. It records "
                "GPS routes, tracks pace and distance, and stores all data locally "
                "on the device.</p>"
            ),
        },
        {
            "title": "TermNote — Markdown Notes in the Terminal",
            "team_index": 1,
            "repo_link": "https://github.com/example/termnote",
            "short_description": "A TUI note-taking app with vim keybindings.",
            "description": (
                "<p>TermNote lets you create, search, and organise markdown notes "
                "entirely from the terminal. Built with Python and Textual.</p>"
            ),
        },
        {
            "title": "FarmSense — IoT Soil Monitor",
            "team_index": 2,
            "repo_link": "https://github.com/example/farmsense",
            "short_description": "Low-cost soil moisture and pH monitoring.",
            "description": (
                "<p>FarmSense uses Arduino sensors to monitor soil conditions and "
                "sends alerts to farmers via SMS. All hardware designs and firmware "
                "are open-source.</p>"
            ),
            "is_contribution_project": 1,
        },
        {
            "title": "LangBridge — Indic Language Translation API",
            "team_index": 3,
            "repo_link": "https://github.com/example/langbridge",
            "short_description": "ML-powered translation for Indian languages.",
            "description": (
                "<p>LangBridge provides a REST API for translating text between "
                "Hindi, Tamil, Kannada, Malayalam, and English using fine-tuned "
                "transformer models.</p>"
            ),
        },
    ],
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def seed():
    """Create all seed data in dependency order.

    Safe to call repeatedly — existing records are detected and skipped.
    All inserts run inside ``frappe.flags.ignore_permissions``; the flag
    is restored on exit regardless of success or failure.
    """
    if not frappe.conf.get("developer_mode"):
        frappe.throw("Seed script can only be run in developer mode.")

    prev_ignore_permissions = frappe.flags.get("ignore_permissions", False)
    frappe.flags.ignore_permissions = True
    try:
        logger.info("Seeding development data")

        users = _create_users()
        chapters = _create_chapters()
        _link_chapter_members(chapters)

        city_chapters = [
            ch
            for ch, data in zip(chapters, CHAPTER_DATA)
            if data["chapter_type"] == CITY_COMMUNITY
        ]
        events = _create_events(city_chapters)
        _create_rsvps(events["live"], users)
        _create_cfps(events["live"])
        _create_hackathon(chapters)

        # nosemgrep: frappe-db-commit; one-off data initialization with manual transaction control
        frappe.db.commit()
        frappe.clear_cache()
        logger.info("Seed data created successfully")
    except Exception:
        frappe.db.rollback()
        logger.exception("Seed script failed — transaction rolled back")
        raise
    finally:
        frappe.flags.ignore_permissions = prev_ignore_permissions


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def _create_users():
    """Ensure every entry in ``SEED_USERS`` has a User doc, profile, and password.

    Returns:
        dict: ``{"normal": [email, ...], "chapter": [user_cfg, ...]}``
    """
    result = {"normal": [], "chapter": []}

    for user_cfg in SEED_USERS:
        email = user_cfg["email"]

        insert_user_profile(
            email=email,
            first_name=user_cfg["first_name"],
            last_name=user_cfg["last_name"],
        )
        frappe.utils.password.update_password(email, DEFAULT_PASSWORD)

        if user_cfg["kind"] == "chapter":
            user_doc = frappe.get_doc("User", email)
            user_doc.add_roles(CHAPTER_TEAM_MEMBER_ROLE)
            user_doc.save()
            result["chapter"].append(user_cfg)
        else:
            result["normal"].append(email)

    logger.info("Ensured %d users (password: '%s')", len(SEED_USERS), DEFAULT_PASSWORD)
    return result


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------


def _chapter_id(data):
    """Return the deterministic primary key for a FOSS Chapter.

    Mirrors the doctype autoname ``format:{chapter_name}-{chapter_type}``.
    """
    return f"{data['chapter_name']}-{data['chapter_type']}"


def _create_chapters():
    """Insert chapters from ``CHAPTER_DATA``, skipping duplicates.

    Returns:
        list: Ordered list of chapter docs matching ``CHAPTER_DATA``.
    """
    chapters = []

    for data in CHAPTER_DATA:
        cid = _chapter_id(data)
        if frappe.db.exists(CHAPTER, cid):
            chapters.append(frappe.get_doc(CHAPTER, cid))
            logger.info("Skipped chapter '%s' (already exists)", data["chapter_name"])
        else:
            chapter = insert_test_chapter(**data)
            chapters.append(chapter)
            logger.info("Created chapter: %s", data["chapter_name"])

    return chapters


def _link_chapter_members(chapters):
    """Add chapter-lead users as Core Team Members in their chapter doc.

    Matches each ``SEED_USERS`` entry whose ``kind`` is ``"chapter"`` to the
    chapter identified by ``chapter_slug``.  Skips if the member is already
    linked.
    """
    slug_map = {ch.slug: ch for ch in chapters}

    for user_cfg in SEED_USERS:
        if user_cfg["kind"] != "chapter":
            continue

        chapter = slug_map.get(user_cfg["chapter_slug"])
        if chapter is None:
            logger.warning(
                "No chapter with slug '%s' for %s",
                user_cfg["chapter_slug"],
                user_cfg["email"],
            )
            continue

        profile_name = frappe.db.get_value(USER_PROFILE, {"user": user_cfg["email"]}, "name")
        if not profile_name:
            continue

        existing = [m.chapter_member for m in chapter.get("chapter_members", [])]
        if profile_name in existing:
            continue

        chapter.append(
            "chapter_members",
            {
                "chapter_member": profile_name,
                "role": CHAPTER_MEMBER_CHILD_TABLE_ROLE,
            },
        )
        chapter.save()
        chapter.reload()
        logger.info("Linked %s to %s", user_cfg["email"], chapter.chapter_name)


# ---------------------------------------------------------------------------
# Events (City Community chapters only)
# ---------------------------------------------------------------------------


def _create_events(city_chapters):
    """Generate events from ``EVENT_TEMPLATES`` for each city-community chapter.

    Only ``CITY_COMMUNITY`` chapters are passed in.  Permalinks are derived
    from the chapter **slug** (not city name), preventing collisions when
    multiple chapters share a city (e.g. Kochi).

    Returns:
        dict: ``{"live": [...], "concluded": [...], "draft": [...]}``
    """
    now = datetime.now()
    buckets = {"live": [], "concluded": [], "draft": []}

    for chapter in city_chapters:
        fmt = {"city": chapter.city, "slug": chapter.slug}

        for tpl in EVENT_TEMPLATES:
            permalink = tpl["permalink"].format(**fmt)
            event_name = tpl["name"].format(**fmt)

            if frappe.db.exists(EVENT, {"event_permalink": permalink}):
                doc_name = frappe.db.get_value(EVENT, {"event_permalink": permalink})
                buckets[tpl["bucket"]].append(frappe.get_doc(EVENT, doc_name))
                logger.info("Skipped event '%s' (already exists)", event_name)
                continue

            extra = {}
            if tpl["bucket"] == "live":
                extra.update(show_rsvp=1, show_cfp=1)

            event = insert_test_event(
                chapter,
                event_name=event_name,
                event_permalink=permalink,
                event_type=tpl["event_type"],
                status=tpl["status"],
                is_published=tpl["is_published"],
                event_start_date=now + timedelta(days=tpl["day_offset"]),
                event_end_date=now
                + timedelta(days=tpl["day_offset"], hours=tpl["duration_hours"]),
                description=tpl["description"].format(**fmt),
                event_location=tpl["location"].format(**fmt),
                **extra,
            )
            buckets[tpl["bucket"]].append(event)
            logger.info("Created event: %s", event_name)

    return buckets


# ---------------------------------------------------------------------------
# RSVPs
# ---------------------------------------------------------------------------


def _create_rsvps(live_events, users):
    """Attach an RSVP form with two sample submissions to each live event.

    Requires at least two ``normal`` users in *users*.
    """
    attendees = users["normal"]
    if len(attendees) < 2:
        logger.warning("Fewer than 2 attendee users; skipping RSVP submissions")
        return

    for event in live_events:
        if frappe.db.exists(EVENT_RSVP, {"event": event.name}):
            logger.info("Skipped RSVP for '%s' (already exists)", event.event_name)
            continue

        rsvp = insert_rsvp_form(
            event.name,
            max_rsvp_count=100,
            rsvp_description=(
                "<p>Please RSVP to confirm your attendance. We look forward to seeing you!</p>"
            ),
            custom_questions=[
                {"question": "What topics interest you the most?", "type": "Long Text"},
            ],
        )

        insert_rsvp_submission(
            rsvp.name,
            submitted_by=attendees[0],
            name="Test Attendee 1",
            email=attendees[0],
            im_a="Professional",
        )
        insert_rsvp_submission(
            rsvp.name,
            submitted_by=attendees[1],
            name="Test Attendee 2",
            email=attendees[1],
            im_a="Student",
        )

        logger.info("Created RSVP + 2 submissions for: %s", event.event_name)


# ---------------------------------------------------------------------------
# CFPs (Call for Proposals)
# ---------------------------------------------------------------------------


def _create_cfps(live_events):
    """Attach a CFP form with two sample talk submissions to each live event.

    Speaker emails are resolved by name from ``SEED_USERS`` rather than by
    list index, so reordering ``SEED_USERS`` cannot silently break this.
    """
    now = datetime.now()

    # Build a lookup from email → user config for deterministic resolution.
    user_by_email = {u["email"]: u for u in SEED_USERS}
    speaker_1_email = "speaker-1@example.com"
    speaker_2_email = "speaker-2@example.com"

    if speaker_1_email not in user_by_email or speaker_2_email not in user_by_email:
        logger.warning("Speaker users not found in SEED_USERS; skipping CFP submissions")
        return

    for event in live_events:
        if frappe.db.exists(EVENT_CFP, {"event": event.name}):
            logger.info("Skipped CFP for '%s' (already exists)", event.event_name)
            continue

        cfp = insert_cfp_form(
            event.name,
            status="Live",
            deadline=now + timedelta(days=20),
            cfp_form_description=(
                "<p>We invite proposals for talks, workshops, and demos. "
                "Share your knowledge with the community!</p>"
            ),
        )

        insert_cfp_submission(
            cfp.name,
            event.name,
            submitted_by=speaker_1_email,
            talk_title="Getting Started with Contributing to Open Source",
            session_type="Talk",
            talk_description=(
                "A beginner-friendly talk on how to find projects, make "
                "your first PR, and become a regular contributor."
            ),
            speakers=[
                {
                    "full_name": "Test Speaker 1",
                    "email": speaker_1_email,
                    "designation": "Software Engineer",
                    "organization": "Open Tech Co",
                    "bio": "Test speaker and open-source contributor.",
                }
            ],
        )
        insert_cfp_submission(
            cfp.name,
            event.name,
            submitted_by=speaker_2_email,
            talk_title="Building CLI Tools with Python",
            session_type="Talk",
            talk_description=(
                "Learn how to build powerful command-line tools using "
                "Python's argparse, click, and rich libraries."
            ),
            speakers=[
                {
                    "full_name": "Test Speaker 2",
                    "email": speaker_2_email,
                    "designation": "Developer Advocate",
                    "organization": "DevTools Inc",
                    "bio": "Test speaker who builds developer tools.",
                }
            ],
        )

        logger.info("Created CFP + 2 submissions for: %s", event.event_name)


# ---------------------------------------------------------------------------
# Hackathon (Student Club chapter)
# ---------------------------------------------------------------------------


def _create_hackathon(chapters):
    """Create the FOSSIT Hackathon with teams, a localhost, and projects.

    The hackathon is linked to the chapter matching
    ``HACKATHON_CFG["chapter_slug"]``.  Falls back to the first available
    chapter if the target slug is missing.
    """
    cfg = HACKATHON_CFG
    now = datetime.now()

    if frappe.db.exists(HACKATHON, {"hackathon_name": cfg["name"]}):
        logger.info("Skipped hackathon '%s' (already exists)", cfg["name"])
        return

    slug_map = {d["slug"]: ch for ch, d in zip(chapters, CHAPTER_DATA)}
    chapter = slug_map.get(cfg["chapter_slug"])
    if chapter is None:
        logger.warning(
            "Chapter '%s' not found; using '%s'",
            cfg["chapter_slug"],
            chapters[0].chapter_name,
        )
        chapter = chapters[0]

    hackathon = insert_test_hackathon(
        chapter.name,
        hackathon_name=cfg["name"],
        permalink=cfg["permalink"],
        hackathon_type="Hybrid",
        start_date=now + timedelta(days=45),
        end_date=now + timedelta(days=47),
        hackathon_description=(
            "<p>FOSSIT Hackathon is a 3-day hybrid hackathon organised by the "
            "Campus Chapter. Build something cool with guidance from mentors "
            "and peers. Work solo or in a team, start something new, or "
            "contribute to a FOSS project.</p>"
        ),
        is_published=1,
        is_registration_live=1,
    )
    logger.info("Created hackathon: %s", cfg["name"])

    teams = []
    for team_name in cfg["teams"]:
        teams.append(insert_test_hackathon_team(hackathon.as_dict(), team_name=team_name))
    logger.info("Created %d hackathon teams", len(teams))

    insert_test_hackathon_localhost(hackathon.name, localhost_name=cfg["localhost"])
    logger.info("Created hackathon localhost: %s", cfg["localhost"])

    created = 0
    for proj in cfg["projects"]:
        if frappe.db.exists(
            HACKATHON_PROJECT,
            {"title": proj["title"], "hackathon": hackathon.name},
        ):
            continue

        frappe.get_doc(
            {
                "doctype": HACKATHON_PROJECT,
                "hackathon": hackathon.name,
                "team": teams[proj["team_index"]].name,
                "title": proj["title"],
                "repo_link": proj.get("repo_link", ""),
                "short_description": proj.get("short_description", ""),
                "description": proj["description"],
                "is_published": 1,
                "is_contribution_project": proj.get("is_contribution_project", 0),
            }
        ).insert(ignore_if_duplicate=True)
        created += 1

    logger.info("Created %d hackathon projects", created)
