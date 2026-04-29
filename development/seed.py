"""Seed development data for a fresh fossunited site.

Populates chapters, events, RSVPs, CFPs, and a hackathon so developers
can explore the application immediately after install.

Usage::

    bench --site foss.localhost execute fossunited.dev.seed.seed

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

import random
from datetime import datetime, timedelta

import frappe
import frappe.utils.password
from faker import Faker
from frappe import _

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_CFP,
    EVENT_CHECKIN,
    EVENT_RSVP,
    EVENT_TICKET,
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PROJECT,
    HACKATHON_TEAM,
    PROPOSAL,
    RSVP_CUSTOM_FIELD,
    RSVP_RESPONSE,
    SPEAKER,
    STUDENT_CLUB,
    TICKET_TIER,
    TICKET_TRANSFER,
    USER_PROFILE,
    GLOBAL_CFP_SETTINGS,
    CFP_REVIEW_PHASE,
    CFP_SCORE_CATEGORY,
    CFP_REVIEW_TEMPLATE,
    CFP_REVIEWER_ASSIGNMENT,
)
from fossunited.id.roles import CHAPTER_MEMBER as CHAPTER_TEAM_MEMBER_ROLE, REVIEWER as REVIEWER_ROLE
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
    insert_test_ticket,
    insert_user_profile,
)

logger = frappe.logger("seed", allow_site=True)

DEFAULT_PASSWORD = "password"
CHAPTER_MEMBER_CHILD_TABLE_ROLE = "Core Team Member"
MOCK_PREFIX = "MOCK-"
GENERATION_STRATEGY_NATIVE = "native"
GENERATION_STRATEGY_CLONE = "clone"
FREE_EVENT_RSVP_MAX_COUNT = 500
PAID_TEST_EVENT_NAME = "MOCK-Test Conference 2026"
PAID_TEST_EVENT_PERMALINK = "mock-test-conference-2026"
PAID_TEST_EVENT_TIER_TITLE = "MOCK-Standard"
PAID_TEST_EVENT_TIER_PRICE = 1000

fake = Faker()

# ===========================================================================
# ZONE 2: CONFIGURATION
# Everything below is seed data. Edit these dictionaries to change what
# records are injected into the database during the seed pass.
# ===========================================================================

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
    {
        "email": "reviewer@example.com",
        "first_name": "Demo",
        "last_name": "Reviewer",
        "kind": "reviewer",
    },
]

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
            "<p>Build something cool over three days in {city} with guidance from "
            "mentors and peers. Work solo or in a team, start something new, "
            "or contribute to a FOSS project.</p>"
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
                "GPS routes, tracks pace and distance, "
                "and stores all data locally on the device.</p>"
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
                "sends alerts to farmers via SMS. "
                "All hardware designs and firmware are open-source.</p>"
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


# ===========================================================================
# ZONE 3: UNIVERSAL HELPERS
# ===========================================================================


def ensure_record(doctype, filters, insert_fn, *args, **kwargs):
    """
    Check if a record exists using `filters`. If it does, return the existing doc.
    Otherwise, run the provided `insert_fn` function and return the new record.
    This creates an idempotent abstraction and cleanly manages the duplicate
    checking logs across the script.
    """
    if frappe.db.exists(doctype, filters):
        doc_name = frappe.db.get_value(doctype, filters)
        logger.info("Skipped %s '%s' (already exists)", doctype, doc_name)
        return frappe.get_doc(doctype, doc_name)

    doc = insert_fn(*args, **kwargs)
    logger.info("Created %s '%s'", doctype, doc.name)
    return doc


def _mock_prefixed(value):
    text = (value or "").strip()
    if not text:
        return MOCK_PREFIX.rstrip("-")
    if text.startswith(MOCK_PREFIX):
        return text
    return f"{MOCK_PREFIX}{text}"


def _mock_permalink(value):
    text = (value or "").strip().lower()
    if not text:
        return "mock-record"
    if text.startswith("mock-"):
        return text
    return f"mock-{text}"


def _mock_email(email):
    raw = (email or "").strip().lower()
    if not raw or "@" not in raw:
        token = frappe.generate_hash(length=8).lower()
        return f"mock-{token}@example.com"

    local_part, domain = raw.split("@", 1)
    if local_part.startswith("mock-"):
        return raw
    return f"mock-{local_part}@{domain}"


def _mock_seed_user(user_cfg):
    cfg = dict(user_cfg)
    cfg["email"] = _mock_email(cfg["email"])
    cfg["first_name"] = _mock_prefixed(cfg["first_name"])
    return cfg


# ===========================================================================
# ZONE 4: MAIN RUNNER & LOGIC
# ===========================================================================


def seed():
    """Create all seed data in dependency order. Safe to run repeatedly."""
    if not frappe.conf.get("developer_mode"):
        frappe.throw(_("Seed script can only be run in developer mode."))

    prev_ignore_permissions = frappe.flags.get("ignore_permissions", False)
    frappe.flags.ignore_permissions = True

    try:
        logger.info("Seeding development data")

        users = _create_users()
        chapters = _create_chapters()
        _link_chapter_members(chapters)

        # Generate events for city communities only to avoid location clashes
        city_chapters = _get_city_community_chapters(chapters)
        events = _create_events(city_chapters)
        _ensure_paid_test_conference(city_chapters)

        _create_rsvps(events["live"], users)
        _create_cfps(events["live"])
        _create_hackathon(chapters)
        _setup_reviewer_workflow(users)

        frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit
        try:
            frappe.clear_cache()
            logger.info("Seed data created successfully")
        except Exception:
            logger.warning("Seed data committed, but cache clear failed", exc_info=True)

    except Exception:
        frappe.db.rollback()
        logger.exception("Seed script failed before commit — transaction rolled back")
        raise
    finally:
        frappe.flags.ignore_permissions = prev_ignore_permissions


def _create_users():
    """Ensure every entry in SEED_USERS has a User doc, profile, and password."""
    result = {"normal": [], "chapter": [], "reviewer": []}

    for raw_user_cfg in SEED_USERS:
        user_cfg = _mock_seed_user(raw_user_cfg)
        email = user_cfg["email"]
        is_new_user = not frappe.db.exists("User", email)

        insert_user_profile(
            email=email, first_name=user_cfg["first_name"], last_name=user_cfg["last_name"]
        )

        if is_new_user:
            frappe.utils.password.update_password(email, DEFAULT_PASSWORD)
            logger.info("Set default password for new user: %s", email)

        if user_cfg["kind"] == "chapter":
            user_roles = frappe.get_roles(email)
            if CHAPTER_TEAM_MEMBER_ROLE not in user_roles:
                user_doc = frappe.get_doc("User", email)
                user_doc.append("roles", {"role": CHAPTER_TEAM_MEMBER_ROLE})
                user_doc.save()
            result["chapter"].append(user_cfg)
        elif user_cfg["kind"] == "reviewer":
            user_roles = frappe.get_roles(email)
            if REVIEWER_ROLE not in user_roles:
                user_doc = frappe.get_doc("User", email)
                user_doc.append("roles", {"role": REVIEWER_ROLE})
                user_doc.save()
            result["reviewer"].append(email)
        else:
            result["normal"].append(email)

    logger.info("Ensured %d users from SEED_USERS", len(SEED_USERS))
    return result


def _setup_reviewer_workflow(users):
    """Set up the Pretalx-inspired reviewer workflow data."""
    logger.info("Setting up Reviewer Workflow V2")

    # Get all live CFPs
    live_cfps = frappe.get_all(EVENT_CFP, filters={"status": "Live"}, pluck="name")

    # 1. Create Review Score Categories for each live CFP
    score_categories = ["Content", "Relevance", "Speaker Experience"]
    for cfp_name in live_cfps:
        for cat in score_categories:
            ensure_record(
                CFP_SCORE_CATEGORY,
                {"category_name": cat, "event_cfp": cfp_name},
                frappe.get_doc(
                    {
                        "doctype": CFP_SCORE_CATEGORY,
                        "category_name": cat,
                        "weight": 1.0,
                        "event_cfp": cfp_name,
                    }
                ).insert,
                ignore_permissions=True,
            )

    # 2. Setup Global CFP Settings for Reviewers
    global_settings = frappe.get_single(GLOBAL_CFP_SETTINGS)
    
    for reviewer_email in users["reviewer"]:
        reviewer_profile = frappe.db.get_value(USER_PROFILE, {"user": reviewer_email}, "name")
        if reviewer_profile and not any(m.profile == reviewer_profile for m in global_settings.members):
            global_settings.append("members", {
                "profile": reviewer_profile,
                "full_name": "Demo Reviewer",
                "email": reviewer_email
            })
    
    global_settings.save(ignore_permissions=True)
    logger.info("Added reviewers to Global CFP Settings")


def _create_chapters():
    """Insert chapters from CHAPTER_DATA."""
    chapters = []
    for chapter_data in CHAPTER_DATA:
        data = dict(chapter_data)
        data["chapter_name"] = _mock_prefixed(data["chapter_name"])
        data["email"] = _mock_email(data["email"])

        cid = f"{data['chapter_name']}-{data['chapter_type']}"
        chapters.append(ensure_record(CHAPTER, cid, insert_test_chapter, **data))
    return chapters


def _get_city_community_chapters(chapters):
    return [
        chapter
        for chapter, chapter_data in zip(chapters, CHAPTER_DATA)
        if chapter_data["chapter_type"] == CITY_COMMUNITY
    ]


def _link_chapter_members(chapters):
    """Add chapter-lead users as Core Team Members in their respective chapter doc."""
    slug_map = {ch.slug: ch for ch in chapters}

    for raw_user_cfg in SEED_USERS:
        user_cfg = _mock_seed_user(raw_user_cfg)
        if user_cfg["kind"] != "chapter":
            continue

        chapter = slug_map.get(user_cfg["chapter_slug"])
        if not chapter:
            logger.warning(
                "No chapter with slug '%s' for %s", user_cfg["chapter_slug"], user_cfg["email"]
            )
            continue

        profile_name = frappe.db.get_value(USER_PROFILE, {"user": user_cfg["email"]}, "name")
        if not profile_name:
            continue

        existing = [m.chapter_member for m in chapter.get("chapter_members", [])]
        if profile_name not in existing:
            chapter.append(
                "chapter_members",
                {"chapter_member": profile_name, "role": CHAPTER_MEMBER_CHILD_TABLE_ROLE},
            )
            chapter.save()
            chapter.reload()
            logger.info("Linked %s to %s", user_cfg["email"], chapter.chapter_name)


def _create_events(city_chapters):
    """Generate events from EVENT_TEMPLATES for each city-community chapter."""
    now = datetime.now()
    buckets = {"live": [], "concluded": [], "draft": []}

    for chapter in city_chapters:
        fmt = {"city": chapter.city, "slug": chapter.slug}

        for tpl in EVENT_TEMPLATES:
            permalink = _mock_permalink(tpl["permalink"].format(**fmt))
            event_name = _mock_prefixed(tpl["name"].format(**fmt))

            kwargs = {
                "event_name": event_name,
                "event_permalink": permalink,
                "event_type": tpl["event_type"],
                "status": tpl["status"],
                "is_published": tpl["is_published"],
                "event_start_date": now + timedelta(days=tpl["day_offset"]),
                "event_end_date": now
                + timedelta(days=tpl["day_offset"], hours=tpl["duration_hours"]),
                "description": tpl["description"].format(**fmt),
                "event_location": tpl["location"].format(**fmt),
            }
            if tpl["bucket"] == "live":
                kwargs.update(show_rsvp=1, show_cfp=1, tickets_status="Live", is_paid_event=0)

            event = ensure_record(
                EVENT, {"event_permalink": permalink}, insert_test_event, chapter, **kwargs
            )

            if tpl["bucket"] == "live":
                _ensure_free_event_rsvp_glue(event)

            buckets[tpl["bucket"]].append(event)

    return buckets


def _ensure_free_event_rsvp_glue(event):
    """Ensure free live events have published RSVP glue docs and required event flags."""
    event_changed = False

    if event.is_paid_event:
        event.is_paid_event = 0
        event_changed = True

    if not event.show_rsvp:
        event.show_rsvp = 1
        event_changed = True

    if event_changed:
        event.save(ignore_permissions=True)
        event.reload()

    rsvp_name = frappe.db.get_value(EVENT_RSVP, {"event": event.name}, "name")
    if rsvp_name:
        rsvp_doc = frappe.get_doc(EVENT_RSVP, rsvp_name)
        rsvp_changed = False

        if not rsvp_doc.is_published:
            rsvp_doc.is_published = 1
            rsvp_changed = True

        max_rsvp_count = int(rsvp_doc.max_rsvp_count or 0)
        if max_rsvp_count < FREE_EVENT_RSVP_MAX_COUNT:
            rsvp_doc.max_rsvp_count = FREE_EVENT_RSVP_MAX_COUNT
            rsvp_changed = True

        if rsvp_changed:
            rsvp_doc.save(ignore_permissions=True)

        return rsvp_doc

    return insert_rsvp_form(
        event.name,
        is_published=1,
        max_rsvp_count=FREE_EVENT_RSVP_MAX_COUNT,
        rsvp_description="<p>RSVP to confirm your attendance.</p>",
    )


def _ensure_paid_test_conference(city_chapters=None):
    """Create/update a stable paid event target used by ticket mock generation."""
    if city_chapters is None:
        chapters = _create_chapters()
        city_chapters = _get_city_community_chapters(chapters)

    if not city_chapters:
        frappe.throw(_("Unable to bootstrap city community chapter for paid test event."))

    anchor_chapter = next(
        (ch for ch in city_chapters if ch.slug == "foss-kochi"), city_chapters[0]
    )
    event_name = frappe.db.get_value(EVENT, {"event_permalink": PAID_TEST_EVENT_PERMALINK}, "name")

    if event_name:
        event = frappe.get_doc(EVENT, event_name)
    else:
        event = insert_test_event(
            anchor_chapter,
            event_name=PAID_TEST_EVENT_NAME,
            event_permalink=PAID_TEST_EVENT_PERMALINK,
            event_type="Conference",
            status="Live",
            is_published=1,
            event_start_date=datetime.now() + timedelta(days=20),
            event_end_date=datetime.now() + timedelta(days=20, hours=10),
            description=(
                "<p>Dedicated paid test conference for local mock ticket generation.</p>"
            ),
            event_location="Mock Convention Center",
            is_paid_event=1,
            tickets_status="Live",
            show_rsvp=0,
            tiers=[
                {
                    "enabled": 1,
                    "title": PAID_TEST_EVENT_TIER_TITLE,
                    "price": PAID_TEST_EVENT_TIER_PRICE,
                    "maximum_tickets": 500,
                }
            ],
        )

    event_changed = False

    if event.status != "Live":
        event.status = "Live"
        event_changed = True

    if not event.is_published:
        event.is_published = 1
        event_changed = True

    if not event.is_paid_event:
        event.is_paid_event = 1
        event_changed = True

    if event.tickets_status != "Live":
        event.tickets_status = "Live"
        event_changed = True

    if event.show_rsvp:
        event.show_rsvp = 0
        event_changed = True

    tier = next(
        (row for row in event.get("tiers", []) if row.title == PAID_TEST_EVENT_TIER_TITLE), None
    )
    if not tier:
        event.append(
            "tiers",
            {
                "enabled": 1,
                "title": PAID_TEST_EVENT_TIER_TITLE,
                "price": PAID_TEST_EVENT_TIER_PRICE,
                "maximum_tickets": 500,
            },
        )
        event_changed = True
    else:
        if not tier.enabled:
            tier.enabled = 1
            event_changed = True
        if tier.price != PAID_TEST_EVENT_TIER_PRICE:
            tier.price = PAID_TEST_EVENT_TIER_PRICE
            event_changed = True

    if event_changed:
        event.save(ignore_permissions=True)
        event.reload()

    return event


def _create_rsvps(live_events, users):
    """Attach an RSVP form with two sample submissions to each live event."""
    attendees = users["normal"]
    if len(attendees) < 2:
        logger.warning("Fewer than 2 attendee users; skipping RSVP submissions")
        return

    for event in live_events:
        rsvp_name = frappe.db.get_value(EVENT_RSVP, {"event": event.name}, "name")

        if rsvp_name:
            rsvp = frappe.get_doc(EVENT_RSVP, rsvp_name)
            rsvp_changed = False

            if not rsvp.is_published:
                rsvp.is_published = 1
                rsvp_changed = True

            max_rsvp_count = int(rsvp.max_rsvp_count or 0)
            if max_rsvp_count < FREE_EVENT_RSVP_MAX_COUNT:
                rsvp.max_rsvp_count = FREE_EVENT_RSVP_MAX_COUNT
                rsvp_changed = True

            if rsvp_changed:
                rsvp.save(ignore_permissions=True)
        else:
            rsvp = insert_rsvp_form(
                event.name,
                is_published=1,
                max_rsvp_count=FREE_EVENT_RSVP_MAX_COUNT,
                rsvp_description=(
                    "<p>Please RSVP to confirm your attendance. We look forward to seeing you!</p>"
                ),
                custom_questions=[
                    {"question": "What topics interest you the most?", "type": "Long Text"}
                ],
            )

        created_submissions = 0

        if not frappe.db.exists(
            RSVP_RESPONSE,
            {"linked_rsvp": rsvp.name, "email": attendees[0]},
        ):
            insert_rsvp_submission(
                rsvp.name,
                submitted_by=attendees[0],
                name=_mock_prefixed("Test Attendee 1"),
                email=attendees[0],
                im_a="Professional",
            )
            created_submissions += 1

        if not frappe.db.exists(
            RSVP_RESPONSE,
            {"linked_rsvp": rsvp.name, "email": attendees[1]},
        ):
            insert_rsvp_submission(
                rsvp.name,
                submitted_by=attendees[1],
                name=_mock_prefixed("Test Attendee 2"),
                email=attendees[1],
                im_a="Student",
            )
            created_submissions += 1

        if created_submissions:
            logger.info(
                "Created RSVP submissions (%d) for: %s", created_submissions, event.event_name
            )
        else:
            logger.info("RSVP already has sample submissions for: %s", event.event_name)


def _create_cfps(live_events):
    """Attach a CFP form with two sample talk submissions to each live event."""
    now = datetime.now()
    user_emails = [_mock_email(u["email"]) for u in SEED_USERS]
    speaker1, speaker2 = _mock_email("speaker-1@example.com"), _mock_email("speaker-2@example.com")

    if speaker1 not in user_emails or speaker2 not in user_emails:
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

        submissions = [
            (
                speaker1,
                _mock_prefixed("Test Speaker 1"),
                _mock_prefixed("Getting Started with Contributing to Open Source"),
                "A beginner-friendly talk on how to find projects, make your "
                "first PR, and become a regular contributor.",
            ),
            (
                speaker2,
                _mock_prefixed("Test Speaker 2"),
                _mock_prefixed("Building CLI Tools with Python"),
                "Learn how to build powerful command-line tools using Python's "
                "argparse, click, and rich libraries.",
            ),
        ]

        for s_email, s_name, title, desc in submissions:
            insert_cfp_submission(
                cfp.name,
                event.name,
                submitted_by=s_email,
                talk_title=title,
                session_type="Talk",
                talk_description=desc,
                speakers=[
                    {
                        "full_name": s_name,
                        "email": s_email,
                        "designation": "Speaker",
                        "organization": "Open Tech",
                        "bio": "Test speaker.",
                    }
                ],
            )

        logger.info("Created CFP + 2 submissions for: %s", event.event_name)


def _create_hackathon(chapters):
    """Create the initial Hackathon with teams, localhosts, and projects."""
    cfg, now = HACKATHON_CFG, datetime.now()
    hackathon_name = _mock_prefixed(cfg["name"])

    if frappe.db.exists(HACKATHON, {"hackathon_name": hackathon_name}):
        logger.info("Skipped hackathon '%s' (already exists)", hackathon_name)
        return

    chapter = next((ch for ch in chapters if ch.slug == cfg["chapter_slug"]), chapters[0])

    hackathon = insert_test_hackathon(
        chapter.name,
        hackathon_name=hackathon_name,
        permalink=_mock_permalink(cfg["permalink"]),
        hackathon_type="Hybrid",
        start_date=now + timedelta(days=45),
        end_date=now + timedelta(days=47),
        hackathon_description=(
            "<p>FOSSIT Hackathon is a 3-day hybrid hackathon organised by the Campus Chapter. "
            "Build something cool with guidance from mentors and peers. Work solo or in a "
            "team, start something new, or contribute to a FOSS project.</p>"
        ),
        is_published=1,
        is_registration_live=1,
    )
    logger.info("Created hackathon: %s", hackathon_name)

    teams = [
        insert_test_hackathon_team(hackathon.as_dict(), team_name=_mock_prefixed(team_name))
        for team_name in cfg["teams"]
    ]
    logger.info("Created %d hackathon teams", len(teams))

    localhost_name = _mock_prefixed(cfg["localhost"])
    insert_test_hackathon_localhost(hackathon.name, localhost_name=localhost_name)
    logger.info("Created hackathon localhost: %s", localhost_name)

    created_projects = 0
    for proj in cfg["projects"]:
        project_title = _mock_prefixed(proj["title"])
        if not frappe.db.exists(
            HACKATHON_PROJECT, {"title": project_title, "hackathon": hackathon.name}
        ):
            frappe.get_doc(
                {
                    "doctype": HACKATHON_PROJECT,
                    "hackathon": hackathon.name,
                    "team": teams[proj["team_index"]].name,
                    "title": project_title,
                    "repo_link": proj.get("repo_link", ""),
                    "short_description": proj.get("short_description", ""),
                    "description": proj["description"],
                    "is_published": 1,
                    "is_contribution_project": proj.get("is_contribution_project", 0),
                }
            ).insert(ignore_if_duplicate=True)
            created_projects += 1

    logger.info("Created %d hackathon projects", created_projects)


# ===========================================================================
# ZONE 5: STANDALONE MOCK GENERATOR & TEARDOWN
# ===========================================================================


def _require_developer_mode(feature_name):
    if not frappe.conf.get("developer_mode"):
        frappe.throw(_("{0} can only be run in developer mode.").format(feature_name))


def _normalize_username(raw):
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_.")
    username = "".join(ch for ch in raw.lower().replace("-", "_") if ch in allowed)
    if len(username) < 3:
        username = username.ljust(3, "_")
    return username[:30]


def _make_unique_username(seed):
    base = _normalize_username(seed)
    candidate = base
    while frappe.db.exists(USER_PROFILE, {"username": candidate}):
        suffix = frappe.generate_hash(length=4).lower()
        candidate = f"{base[: 30 - len(suffix) - 1]}_{suffix}"
    return candidate


def _find_ticket_prototype():
    paid_event_name = frappe.db.get_value(
        EVENT, {"event_permalink": PAID_TEST_EVENT_PERMALINK}, "name"
    )
    if not paid_event_name:
        return None

    candidates = frappe.get_all(
        EVENT_TICKET,
        fields=["name"],
        filters={"event": paid_event_name},
        order_by="creation desc",
        page_length=200,
    )

    if candidates:
        return frappe.get_doc(EVENT_TICKET, candidates[0].name)

    return None


def _ensure_paid_event_for_ticket_generation():
    paid_event = _ensure_paid_test_conference()
    if not paid_event:
        frappe.throw(_("Unable to bootstrap paid test conference for mock ticket generation."))
    return paid_event


def _bootstrap_ticket_prototype():
    prototype = _find_ticket_prototype()
    if prototype:
        return prototype

    paid_event = _ensure_paid_event_for_ticket_generation()
    insert_test_ticket(
        paid_event.name,
        full_name=_mock_prefixed("Seed Ticket Prototype"),
        email=f"seed-ticket-{frappe.generate_hash(length=8).lower()}@example.com",
        tier=_get_ticket_tier_for_event(paid_event.name),
        subscribe_chapter_mailing=0,
        ignore_permissions=True,
    )

    prototype = _find_ticket_prototype()
    if prototype:
        return prototype

    frappe.throw(_("Unable to bootstrap a prototype for {0}.").format(EVENT_TICKET))


def _get_ticket_tier_for_event(event_name):
    tier = frappe.db.get_value(
        "FOSS Ticket Tier",
        {"parent": event_name, "enabled": 1},
        "title",
    )
    if tier:
        return tier

    return frappe.db.get_value("FOSS Ticket Tier", {"parent": event_name}, "title") or ""


def _create_mock_identity(index):
    token = frappe.generate_hash(length=8).lower()
    first_name = f"{MOCK_PREFIX}{fake.first_name()}"
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    email = f"mock.user.{token}@example.com"
    username = _make_unique_username(f"mock_{fake.user_name()}_{index}_{token[:4]}")

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "username": username,
    }


def _update_mock_profile_metadata(profile, identity):
    """Update the hook-created profile with mock metadata.

    The profile is created by the native User insert hooks. We only mutate
    business fields here, keeping the User/Profile creation lifecycle intact.
    """
    profile.email = identity["email"]
    profile.full_name = identity["full_name"]
    profile.username = identity["username"]
    profile.is_private = 0
    profile.is_published = 1
    profile.save(ignore_permissions=True)
    profile.reload()


def _generate_mock_profile(index):
    """Generate one mock profile using native helper + hook-driven profile creation."""
    identity = _create_mock_identity(index)
    helper_profile_name = None

    try:
        # Create User + Profile using the project helper so user hooks run natively.
        helper_profile_name = insert_user_profile(
            email=identity["email"],
            first_name=identity["first_name"],
            last_name=identity["last_name"],
        )
        frappe.utils.password.update_password(identity["email"], DEFAULT_PASSWORD)

        profile_name = helper_profile_name or frappe.db.get_value(
            USER_PROFILE, {"user": identity["email"]}, "name"
        )
        if not profile_name:
            frappe.throw(
                _("Unable to locate auto-created profile for {0}").format(identity["email"])
            )

        profile = frappe.get_doc(USER_PROFILE, profile_name)
        _update_mock_profile_metadata(profile, identity)
        return profile

    except Exception:
        # Avoid leaving detached records on partial failures.
        if helper_profile_name and frappe.db.exists(USER_PROFILE, helper_profile_name):
            _safe_delete(USER_PROFILE, helper_profile_name)
        if frappe.db.exists("User", identity["email"]):
            _safe_delete("User", identity["email"])
        raise


def _get_mock_ticket_attendee_pool():
    pool_rows = frappe.get_all(
        USER_PROFILE,
        filters={"full_name": ["like", f"{MOCK_PREFIX}%"]},
        fields=["email", "full_name"],
        page_length=100000,
    )

    pool = []
    seen_emails = set()

    for row in pool_rows:
        email = (row.get("email") or "").strip().lower()
        full_name = (row.get("full_name") or "").strip()

        if not email or not full_name or email in seen_emails:
            continue

        pool.append({"email": email, "full_name": full_name})
        seen_emails.add(email)

    random.shuffle(pool)
    return pool


def _pop_or_generate_ticket_attendee(context):
    mock_user_pool = context.get("mock_user_pool") or []

    if mock_user_pool:
        return mock_user_pool.pop()

    token = frappe.generate_hash(length=8).lower()
    return {
        "email": f"mock.guest.{token}@example.com",
        "full_name": f"{MOCK_PREFIX}{fake.name()}",
    }


def _mutate_ticket_clone(clone, _index, context=None):
    event_doc = _ensure_paid_event_for_ticket_generation()
    context = context or {}
    attendee = _pop_or_generate_ticket_attendee(context)

    clone.event = event_doc.name
    clone.full_name = attendee["full_name"]
    clone.email = attendee["email"]
    clone.tier = _get_ticket_tier_for_event(event_doc.name)
    clone.subscribe_chapter_mailing = 0
    clone.is_transfer_ticket = 0
    clone.razorpay_payment = None
    clone.custom_fields = []
    clone.check_ins = []


def _generate_one_by_strategy(cfg, index, prototype=None, context=None):
    """Run one generation iteration according to registry strategy."""
    strategy = cfg["strategy"]

    if strategy == GENERATION_STRATEGY_NATIVE:
        cfg["generate_one"](index)
        return

    clone = frappe.copy_doc(prototype)
    clone.name = None
    clone.docstatus = 0
    cfg["mutate"](clone, index, context=context or {})
    clone.insert(ignore_permissions=True)
    if cfg.get("post_insert"):
        cfg["post_insert"](clone)


def _safe_delete(doctype, name):
    try:
        frappe.delete_doc(doctype, name, ignore_permissions=True, force=1)
        return True
    except Exception:
        logger.exception("Failed deleting %s '%s' during mock teardown", doctype, name)
        return False


def _teardown_mock_profiles():
    profiles = frappe.get_all(
        USER_PROFILE,
        filters={"full_name": ["like", f"{MOCK_PREFIX}%"]},
        fields=["name", "user"],
        page_length=100000,
    )

    users_to_delete = {
        row.user for row in profiles if row.user and row.user not in {"Administrator", "Guest"}
    }
    users_to_delete.update(
        user
        for user in frappe.get_all(
            "User",
            filters={"first_name": ["like", f"{MOCK_PREFIX}%"]},
            pluck="name",
            page_length=100000,
        )
        if user not in {"Administrator", "Guest"}
    )

    deleted_profiles = 0
    for row in profiles:
        deleted_profiles += int(_safe_delete(USER_PROFILE, row.name))

    deleted_users = 0
    for user in users_to_delete:
        deleted_users += int(_safe_delete("User", user))

    return {"profiles": deleted_profiles, "users": deleted_users}


def _teardown_mock_tickets():
    tickets = frappe.get_all(
        EVENT_TICKET,
        filters={"full_name": ["like", f"{MOCK_PREFIX}%"]},
        pluck="name",
        page_length=100000,
    )

    deleted_transfers = 0
    if tickets:
        transfer_names = frappe.get_all(
            TICKET_TRANSFER,
            filters={"ticket": ["in", tickets]},
            pluck="name",
            page_length=100000,
        )
        for name in transfer_names:
            deleted_transfers += int(_safe_delete(TICKET_TRANSFER, name))

    deleted_tickets = 0
    for name in tickets:
        deleted_tickets += int(_safe_delete(EVENT_TICKET, name))

    return {"tickets": deleted_tickets, "ticket_transfers": deleted_transfers}


def _mock_generator_registry():
    return {
        USER_PROFILE: {
            "strategy": GENERATION_STRATEGY_NATIVE,
            "generate_one": _generate_mock_profile,
            "teardown": _teardown_mock_profiles,
        },
        EVENT_TICKET: {
            "strategy": GENERATION_STRATEGY_CLONE,
            "find_prototype": _find_ticket_prototype,
            "bootstrap_prototype": _bootstrap_ticket_prototype,
            "mutate": _mutate_ticket_clone,
            "teardown": _teardown_mock_tickets,
        },
    }


def _get_mock_config(doctype):
    registry = _mock_generator_registry()
    if doctype not in registry:
        supported = ", ".join(sorted(registry))
        frappe.throw(
            _("Unsupported DocType '{0}' for mock generation. Supported: {1}").format(
                doctype, supported
            )
        )

    cfg = registry[doctype]
    strategy = cfg.get("strategy")

    if strategy not in {GENERATION_STRATEGY_NATIVE, GENERATION_STRATEGY_CLONE}:
        frappe.throw(_("Invalid generation strategy configured for {0}").format(doctype))

    if strategy == GENERATION_STRATEGY_NATIVE and not cfg.get("generate_one"):
        frappe.throw(
            _("Native generation config is missing 'generate_one' for {0}").format(doctype)
        )

    if strategy == GENERATION_STRATEGY_CLONE and (
        not cfg.get("find_prototype")
        or not cfg.get("bootstrap_prototype")
        or not cfg.get("mutate")
    ):
        frappe.throw(_("Clone generation config is incomplete for {0}").format(doctype))

    return cfg


def _get_or_bootstrap_prototype(doctype, cfg):
    prototype = cfg["find_prototype"]()
    if prototype:
        return prototype

    logger.info("No prototype found for %s, running JIT bootstrap", doctype)
    prototype = cfg["bootstrap_prototype"]()
    if prototype:
        return prototype

    frappe.throw(_("Unable to find or bootstrap a prototype for {0}").format(doctype))


def generate_mock_data(doctype, count=10):
    """Generate high-volume mock records for supported custom DocTypes."""
    _require_developer_mode("Mock generator")

    try:
        count = int(count)
    except (TypeError, ValueError):
        frappe.throw(_("count must be an integer"))

    if count <= 0:
        frappe.throw(_("count must be greater than 0"))

    cfg = _get_mock_config(doctype)
    strategy = cfg["strategy"]
    prev_ignore_permissions = frappe.flags.get("ignore_permissions", False)
    frappe.flags.ignore_permissions = True

    created, failed = 0, 0

    try:
        generation_context = {}
        prototype = None
        if strategy == GENERATION_STRATEGY_CLONE:
            prototype = _get_or_bootstrap_prototype(doctype, cfg)
            if doctype == EVENT_TICKET:
                generation_context["mock_user_pool"] = _get_mock_ticket_attendee_pool()
                logger.info(
                    "Loaded %d mock users for ticket 1:1 assignment",
                    len(generation_context["mock_user_pool"]),
                )

        for idx in range(count):
            try:
                _generate_one_by_strategy(
                    cfg,
                    idx,
                    prototype=prototype,
                    context=generation_context,
                )
                created += 1
            except Exception:
                failed += 1
                logger.exception("Failed creating mock %s (%d/%d)", doctype, idx + 1, count)

        frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit
        try:
            frappe.clear_cache()
        except Exception:
            logger.warning("Mock data committed, but cache clear failed", exc_info=True)

        summary = {
            "doctype": doctype,
            "requested": count,
            "created": created,
            "failed": failed,
            "prefix": MOCK_PREFIX,
        }
        logger.info("Mock generation summary: %s", summary)
        return summary

    except Exception:
        frappe.db.rollback()
        logger.exception("Mock generation failed before commit — transaction rolled back")
        raise
    finally:
        frappe.flags.ignore_permissions = prev_ignore_permissions


def teardown_mock_data(doctype=None):
    """Delete only mock records tagged by the MOCK prefix."""
    _require_developer_mode("Mock teardown")

    registry = _mock_generator_registry()
    if doctype:
        selected = {doctype: _get_mock_config(doctype)}
    else:
        selected = registry

    prev_ignore_permissions = frappe.flags.get("ignore_permissions", False)
    frappe.flags.ignore_permissions = True

    try:
        summary = {}
        for dt, cfg in selected.items():
            summary[dt] = cfg["teardown"]()

        frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit
        try:
            frappe.clear_cache()
        except Exception:
            logger.warning("Mock teardown committed, but cache clear failed", exc_info=True)

        logger.info("Mock teardown summary: %s", summary)
        return summary

    except Exception:
        frappe.db.rollback()
        logger.exception("Mock teardown failed before commit — transaction rolled back")
        raise
    finally:
        frappe.flags.ignore_permissions = prev_ignore_permissions


def teardown_all():
    """Delete all MOCK-prefixed seed records in reverse dependency order."""
    _require_developer_mode("Seed teardown")

    prev_ignore_permissions = frappe.flags.get("ignore_permissions", False)
    frappe.flags.ignore_permissions = True

    def _delete_many(doctype, names):
        deleted = 0
        for name in names:
            deleted += int(_safe_delete(doctype, name))
        return deleted

    try:
        mock_event_names = set(
            frappe.get_all(
                EVENT,
                filters={"event_name": ["like", f"{MOCK_PREFIX}%"]},
                pluck="name",
                page_length=100000,
            )
        )
        mock_hackathon_names = set(
            frappe.get_all(
                HACKATHON,
                filters={"hackathon_name": ["like", f"{MOCK_PREFIX}%"]},
                pluck="name",
                page_length=100000,
            )
        )

        mock_ticket_names = set(
            frappe.get_all(
                EVENT_TICKET,
                filters={"full_name": ["like", f"{MOCK_PREFIX}%"]},
                pluck="name",
                page_length=100000,
            )
        )
        if mock_event_names:
            mock_ticket_names.update(
                frappe.get_all(
                    EVENT_TICKET,
                    filters={"event": ["in", list(mock_event_names)]},
                    pluck="name",
                    page_length=100000,
                )
            )

        mock_rsvp_submission_names = set()
        if mock_event_names:
            mock_rsvp_submission_names.update(
                frappe.get_all(
                    RSVP_RESPONSE,
                    filters={"event": ["in", list(mock_event_names)]},
                    pluck="name",
                    page_length=100000,
                )
            )

        mock_proposal_names = set()
        if mock_event_names:
            mock_proposal_names.update(
                frappe.get_all(
                    PROPOSAL,
                    filters={"event": ["in", list(mock_event_names)]},
                    pluck="name",
                    page_length=100000,
                )
            )

        mock_profile_rows = frappe.get_all(
            USER_PROFILE,
            filters={"full_name": ["like", f"{MOCK_PREFIX}%"]},
            fields=["name", "user"],
            page_length=100000,
        )
        mock_profile_names = [row.name for row in mock_profile_rows]
        mock_user_names = {
            row.user
            for row in mock_profile_rows
            if row.user and row.user not in {"Guest", "Administrator"}
        }
        mock_user_names.update(
            user
            for user in frappe.get_all(
                "User",
                filters={"name": ["like", "mock-%@%"]},
                pluck="name",
                page_length=100000,
            )
            if user not in {"Guest", "Administrator"}
        )
        mock_user_names.update(
            user
            for user in frappe.get_all(
                "User",
                filters={"first_name": ["like", f"{MOCK_PREFIX}%"]},
                pluck="name",
                page_length=100000,
            )
            if user not in {"Guest", "Administrator"}
        )

        summary = {}

        checkin_names = []
        ticket_custom_field_names = []
        transfer_names = []
        if mock_ticket_names:
            ticket_list = list(mock_ticket_names)
            checkin_names = frappe.get_all(
                EVENT_CHECKIN,
                filters={
                    "parent": ["in", ticket_list],
                    "parenttype": EVENT_TICKET,
                    "parentfield": "check_ins",
                },
                pluck="name",
                page_length=100000,
            )
            ticket_custom_field_names = frappe.get_all(
                "FOSS Ticket Custom Field",
                filters={
                    "parent": ["in", ticket_list],
                    "parenttype": EVENT_TICKET,
                    "parentfield": "custom_fields",
                },
                pluck="name",
                page_length=100000,
            )
            transfer_names = frappe.get_all(
                TICKET_TRANSFER,
                filters={"ticket": ["in", ticket_list]},
                pluck="name",
                page_length=100000,
            )

        summary[EVENT_CHECKIN] = _delete_many(EVENT_CHECKIN, checkin_names)
        summary["FOSS Ticket Custom Field"] = _delete_many(
            "FOSS Ticket Custom Field", ticket_custom_field_names
        )
        summary[TICKET_TRANSFER] = _delete_many(TICKET_TRANSFER, transfer_names)
        summary[EVENT_TICKET] = _delete_many(EVENT_TICKET, list(mock_ticket_names))

        tier_names = []
        rsvp_names = []
        cfp_names = []
        if mock_event_names:
            event_list = list(mock_event_names)
            tier_names = frappe.get_all(
                TICKET_TIER,
                filters={"parent": ["in", event_list]},
                pluck="name",
                page_length=100000,
            )
            rsvp_names = frappe.get_all(
                EVENT_RSVP,
                filters={"event": ["in", event_list]},
                pluck="name",
                page_length=100000,
            )
            cfp_names = frappe.get_all(
                EVENT_CFP,
                filters={"event": ["in", event_list]},
                pluck="name",
                page_length=100000,
            )

        rsvp_custom_answer_names = []
        if mock_rsvp_submission_names:
            rsvp_custom_answer_names = frappe.get_all(
                RSVP_CUSTOM_FIELD,
                filters={
                    "parent": ["in", list(mock_rsvp_submission_names)],
                    "parenttype": RSVP_RESPONSE,
                    "parentfield": "custom_answers",
                },
                pluck="name",
                page_length=100000,
            )

        speaker_names = []
        if mock_proposal_names:
            speaker_names = frappe.get_all(
                SPEAKER,
                filters={
                    "parent": ["in", list(mock_proposal_names)],
                    "parenttype": PROPOSAL,
                    "parentfield": "speakers",
                },
                pluck="name",
                page_length=100000,
            )

        summary[RSVP_CUSTOM_FIELD] = _delete_many(RSVP_CUSTOM_FIELD, rsvp_custom_answer_names)
        summary[RSVP_RESPONSE] = _delete_many(RSVP_RESPONSE, list(mock_rsvp_submission_names))
        summary[SPEAKER] = _delete_many(SPEAKER, speaker_names)
        summary[PROPOSAL] = _delete_many(PROPOSAL, list(mock_proposal_names))
        summary[EVENT_CFP] = _delete_many(EVENT_CFP, cfp_names)
        summary[EVENT_RSVP] = _delete_many(EVENT_RSVP, rsvp_names)
        summary[TICKET_TIER] = _delete_many(TICKET_TIER, tier_names)

        hackathon_project_names = []
        hackathon_localhost_names = []
        hackathon_team_names = []
        if mock_hackathon_names:
            hackathon_list = list(mock_hackathon_names)
            hackathon_project_names = frappe.get_all(
                HACKATHON_PROJECT,
                filters={"hackathon": ["in", hackathon_list]},
                pluck="name",
                page_length=100000,
            )
            hackathon_localhost_names = frappe.get_all(
                HACKATHON_LOCALHOST,
                filters={"parent_hackathon": ["in", hackathon_list]},
                pluck="name",
                page_length=100000,
            )
            hackathon_team_names = frappe.get_all(
                HACKATHON_TEAM,
                filters={"hackathon": ["in", hackathon_list]},
                pluck="name",
                page_length=100000,
            )

        summary[HACKATHON_PROJECT] = _delete_many(HACKATHON_PROJECT, hackathon_project_names)
        summary[HACKATHON_LOCALHOST] = _delete_many(HACKATHON_LOCALHOST, hackathon_localhost_names)
        summary[HACKATHON_TEAM] = _delete_many(HACKATHON_TEAM, hackathon_team_names)
        summary[HACKATHON] = _delete_many(HACKATHON, list(mock_hackathon_names))

        # Cleanup Reviewer Workflow V2
        _delete_many(CFP_SCORE_CATEGORY, frappe.get_all(CFP_SCORE_CATEGORY, pluck="name"))
        _delete_many(CFP_REVIEW_PHASE, frappe.get_all(CFP_REVIEW_PHASE, pluck="name"))
        _delete_many(CFP_REVIEW_TEMPLATE, frappe.get_all(CFP_REVIEW_TEMPLATE, pluck="name"))
        _delete_many(CFP_REVIEWER_ASSIGNMENT, frappe.get_all(CFP_REVIEWER_ASSIGNMENT, pluck="name"))

        summary[EVENT] = _delete_many(EVENT, list(mock_event_names))

        mock_chapter_names = frappe.get_all(
            CHAPTER,
            filters={"chapter_name": ["like", f"{MOCK_PREFIX}%"]},
            pluck="name",
            page_length=100000,
        )
        summary[CHAPTER] = _delete_many(CHAPTER, mock_chapter_names)

        summary[USER_PROFILE] = _delete_many(USER_PROFILE, mock_profile_names)
        summary["User"] = _delete_many("User", list(mock_user_names))

        frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit
        try:
            frappe.clear_cache()
        except Exception:
            logger.warning("Seed teardown committed, but cache clear failed", exc_info=True)

        logger.info("Seed teardown summary: %s", summary)
        return summary

    except Exception:
        frappe.db.rollback()
        logger.exception("Seed teardown failed before commit — transaction rolled back")
        raise
    finally:
        frappe.flags.ignore_permissions = prev_ignore_permissions

if __name__ == "__main__":
    seed()

