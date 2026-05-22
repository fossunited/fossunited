import datetime
import json

import frappe

from fossunited.doctype_ids import COMMUNITY_PARTNER, EVENT, EVENT_CFP
from fossunited.fossunited.user_utils import fetch_user_profiles
from fossunited.fossunited.utils import get_event_sponsors

INDIAFOSS_2026_EVENT = "IndiaFOSS 2026"
TIER1 = {"Maintainer", "Patrons", "Platinum", "Gold"}

# Devroom banner colors keyed by slug
# Light: high-L low-C pastel from Figma SVGs
# Dark: L=0.30 (just above card bg 0.2788), C boosted to hold color identity under screen blend
_DEVROOM_DEFAULT = {"light": "oklch(0.97 0.047 147)", "dark": "oklch(0.30 0.10 147)"}
DEVROOM_COLORS = {
    "aosp": {"light": "oklch(0.9581 0.0369 144.37)", "dark": "oklch(0.30 0.10 144.37)"},
    "devops": {
        "light": "oklch(0.9372 0.024 238.73)",
        "dark": "oklch(0.30 0.09 238.73)",
    },
    "compilers": {
        "light": "oklch(0.9496 0.0189 17.49)",
        "dark": "oklch(0.30 0.10 17.49)",
    },
    "docs": {
        "light": "oklch(0.9371 0.035 312.73)",
        "dark": "oklch(0.30 0.11 312.73)",
    },
    "design": {
        "light": "oklch(0.9383 0.0304 356.53)",
        "dark": "oklch(0.30 0.09 356.53)",
    },
    "hardware": {
        "light": "oklch(0.954 0.0245 67.53)",
        "dark": "oklch(0.30 0.10 67.53)",
    },
    "rtos": {"light": "oklch(0.9658 0.0372 108.64)", "dark": "oklch(0.32 0.12 108.64)"},
    "security": {
        "light": "oklch(0.9613 0.0224 182.54)",
        "dark": "oklch(0.30 0.10 182.54)",
    },
}


# TODO: replace all short form url to /2026/ form
# we need to figure out to automate url redirection for /indiafoss to retain future proofing per year


def get_context(context):
    context.no_cache = 1
    context.hide_nav, context.hide_footer = True, True

    today = frappe.utils.getdate(frappe.utils.today())
    event_docname = frappe.db.get_value(EVENT, {"event_name": INDIAFOSS_2026_EVENT}, "name")
    if not event_docname:
        _empty_context(context)
        return

    event = frappe.get_doc(EVENT, event_docname)
    event_data = json.loads(event.get("event_data") or "{}")

    cfp_name = frappe.db.get_value(EVENT_CFP, {"event": event_docname}, "name")
    cfp = frappe.get_doc(EVENT_CFP, cfp_name) if cfp_name else frappe._dict()

    context.map_link = event.get("map_link") or event_data.get("map_link") or ""
    context.cta_buttons = _get_cta_buttons(event, cfp)
    context.countdown_days, context.countdown_state = _get_countdown(event)
    context.event_date_str = _get_date_str(event)
    context.event_location = event.event_location or ""

    # Sponsors — use shared util, split into tier1/tier2
    sponsors_dict = get_event_sponsors(event.sponsor_list)
    context.sponsors = [
        {"tier": t, "sponsor_list": sl, "is_tier1": t in TIER1} for t, sl in sponsors_dict.items()
    ]
    context.partners = frappe.db.get_all(
        COMMUNITY_PARTNER,
        {"parent": event_docname, "parenttype": EVENT},
        ["org_name", "link", "logo"],
        page_length=99,
    )

    devrooms = frappe.get_all(
        "Devroom Custom",
        {"event": event_docname},
        ["title", "slug", "logo"],
        order_by="title asc",
    )
    for dr in devrooms:
        c = DEVROOM_COLORS.get(dr.slug, _DEVROOM_DEFAULT)
        dr.color_light = c["light"]
        dr.color_dark = c["dark"]
    context.devrooms = devrooms

    # People — all via fetch_user_profiles (email or profile docname); sorted A-Z in template
    context.co_chairs = fetch_user_profiles(
        event_data.get("co_chairs", []), "Co-chair, IndiaFOSS 2026"
    )

    reviewer_links = [r.reviewer for r in (cfp.cfp_reviewers or []) if r.reviewer]
    context.reviewers = fetch_user_profiles(reviewer_links, "Reviewer, IndiaFOSS 2026")

    devroom_managers = []
    for room, members in event_data.get("devrooms", {}).items():
        devroom_managers.extend(
            fetch_user_profiles(members, f"{room} Devroom Manager", force_bio=True)
        )
    context.devroom_managers = devroom_managers

    context.volunteers = [
        {
            "full_name": v["full_name"],
            "profile_photo": v["profile_picture"],
            "bio": v["role"],
            "route": f"/{v['route']}" if v.get("route") else "#",
        }
        for v in event.get_volunteers()
    ]

    # Timeline + progress bar - merge manual items with auto CFP items
    manual_tl = event_data.get("timeline", [])
    cfp_tl = _get_cfp_timeline_items(cfp, today)
    merged_tl = sorted(manual_tl + cfp_tl, key=lambda x: x.get("date", "9999"))
    context.timeline = _enrich_timeline(merged_tl, today)
    context.progress_segments, context.progress_markers = _get_progress_bar(
        context.timeline, today
    )
    context.urgency_text = next(
        (
            {"label": m["label"], "days": m["days_away"]}
            for m in context.progress_markers
            if m.get("is_urgent")
        ),
        None,
    )
    context.action_cards = event_data.get("action_cards", [])
    faqs = event_data.get("faqs", [])
    for faq in faqs:
        faq["answer"] = frappe.utils.md_to_html(faq.get("answer") or "")
    context.faqs = faqs
    context.topics = event_data.get("topics", [])
    context.rewind = event_data.get("rewind_stats", {})

    # Footer links grouped by section
    grouped = {}
    for link in event_data.get("footer_links", []):
        grouped.setdefault(link["section"], []).append(link)
    context.footer_links = grouped

    context.today_str = today.isoformat()

    context.event_docname = event_docname
    context.years = _get_indiafoss_years()
    context.current_year = 2026
    context.deck_link = event.get("deck_link") or ""
    context.community_deck_link = (
        event_data.get("community_deck") or "https://fossunited.org/files/Community-deck-V2.pdf"
    )

    context.pagetitle = "IndiaFOSS 2026"
    context.description = (
        "The 6th edition of the Free and Open Source Software Festival "
        "by the FOSS United community."
    )
    context.image = "https://fossunited.org/files/indiafoss-2026-og.png"


def _empty_context(context):
    context.cta_buttons = [{"label": "Get Tickets", "url": "", "primary": True}]
    context.countdown_days, context.countdown_state = None, "upcoming"
    context.event_date_str = "2026"
    context.event_location = "Bengaluru"
    context.map_link = ""
    context.sponsors = []
    context.partners = []
    context.co_chairs = context.reviewers = context.devroom_managers = context.volunteers = []
    context.devrooms = []
    context.timeline = context.action_cards = context.faqs = context.topics = []
    context.progress_segments = []
    context.progress_markers = []
    context.urgency_text = None
    context.rewind = {}
    context.footer_links = {}
    context.today_str = frappe.utils.getdate(frappe.utils.today()).isoformat()
    context.event_docname = ""
    context.years = _get_indiafoss_years()
    context.current_year = 2026
    context.deck_link = ""
    context.community_deck_link = ""
    context.pagetitle = "IndiaFOSS 2026"
    context.description = (
        "The 6th edition of the Free and Open Source Software Festival "
        "by the FOSS United community."
    )


def _enrich_timeline(items, today):
    for item in items:
        try:
            d = frappe.utils.getdate(item["date"])
            item["day_num"] = d.strftime("%-d")
            item["month_str"] = d.strftime("%b")
        except Exception:
            item["day_num"] = item.get("date", "")[8:10].lstrip("0") or "?"
            item["month_str"] = ""
        item.setdefault("extended_date", "")

        manual = (item.get("status") or "").lower()
        if manual == "none":
            item["resolved_status"] = "none"
        elif manual in ("live", "extended", "closed"):
            item["resolved_status"] = manual
        else:
            # auto-derive from date range if end_date provided
            end_str = item.get("end_date") or ""
            if end_str:
                try:
                    start_d = frappe.utils.getdate(item["date"])
                    end_d = frappe.utils.getdate(end_str)
                    if today > end_d:
                        item["resolved_status"] = "closed"
                    elif today >= start_d:
                        item["resolved_status"] = "live"
                    else:
                        item["resolved_status"] = ""
                except Exception:
                    item["resolved_status"] = ""
            else:
                item["resolved_status"] = ""
    return items


def _get_progress_bar(timeline, today):
    """Week-based progress bar Apr 1 → Sep 26, 2026."""
    bar_start = datetime.date(2026, 4, 1)
    bar_end = datetime.date(2026, 9, 26)
    total_days = (bar_end - bar_start).days  # 178

    today_offset = (today - bar_start).days
    total_weeks = -(-total_days // 7)  # ceil

    segments = []
    for w in range(total_weeks):
        week_start = bar_start + datetime.timedelta(days=w * 7)
        week_end = min(bar_start + datetime.timedelta(days=w * 7 + 6), bar_end)
        if today_offset > w * 7 + 6:
            cls = "past"
        elif today_offset >= w * 7:
            cls = "current"
        else:
            cls = "future"
        segments.append(
            {
                "cls": cls,
                "label": f"{week_start.strftime('%-d %b')} - {week_end.strftime('%-d %b')}",
            }
        )

    next_idx = next(
        (
            i
            for i, item in enumerate(timeline)
            if frappe.utils.getdate(item.get("date", "1900-01-01")) > today
        ),
        None,
    )

    markers = []
    last_above_pct = -100.0
    last_below_pct = -100.0
    for idx, item in enumerate(timeline):
        try:
            d = frappe.utils.getdate(item["date"])
            pct = max(0.0, min(100.0, (d - bar_start).days * 100.0 / total_days))
            days_away = (d - today).days
            is_past = d < today
            is_urgent = idx == next_idx and 0 <= days_away <= 30
            above = (pct - last_above_pct) >= 15
            if above:
                last_above_pct = pct
            compact = False
            if not above:
                compact = (pct - last_below_pct) < 15
                if not compact:
                    last_below_pct = pct
            markers.append(
                {
                    "label": item["label"],
                    "description": item.get("description", ""),
                    "pct": round(pct, 1),
                    "is_past": is_past,
                    "is_urgent": is_urgent,
                    "above": above,
                    "compact": compact,
                    "days_away": days_away if is_urgent else None,
                }
            )
        except Exception:
            pass

    return segments, markers


def _get_cta_buttons(event, cfp):
    if event.status == "Concluded" and event.show_photos:
        return [
            {"label": "See Photos", "url": "#photos", "primary": True},
            {"label": "See Schedule", "url": "/indiafoss/schedule", "primary": False},
        ]
    if event.show_schedule:
        return [
            {"label": "See Schedule", "url": "/indiafoss/schedule", "primary": True},
            {
                "label": "Get Tickets",
                "url": "/indiafoss/tickets",
                "primary": False,
            },
        ]
    if cfp and cfp.status == "Closed":
        return [
            {
                "label": "View Proposals",
                "url": "/indiafoss/talks",
                "primary": True,
            },
            {
                "label": "Get Tickets",
                "url": "/indiafoss/tickets",
                "primary": False,
            },
        ]
    buttons = [
        {
            "label": "Get Tickets",
            "url": "/indiafoss/tickets",
            "primary": True,
        }
    ]
    if cfp and cfp.status == "Live":
        buttons.append(
            {
                "label": "Propose a Talk",
                "url": "/indiafoss/cfp",
                "primary": False,
            }
        )
    return buttons


def _get_countdown(event):
    if not event.event_start_date:
        return None, "upcoming"
    today = frappe.utils.getdate(frappe.utils.today())
    start = frappe.utils.getdate(event.event_start_date)
    end = frappe.utils.getdate(event.event_end_date or event.event_start_date)
    if today > end:
        return None, "concluded"
    if today >= start:
        return None, "live"
    return (start - today).days, "upcoming"


def _get_date_str(event):
    if not event.event_start_date:
        return ""
    s = frappe.utils.getdate(event.event_start_date)
    if event.event_end_date:
        e = frappe.utils.getdate(event.event_end_date)
        return f"{s.strftime('%-d')}-{e.strftime('%-d %B %Y')}"
    return s.strftime("%-d %B %Y")


def _get_cfp_timeline_items(cfp, today):
    """Auto-generate CFP timeline items from EVENT_CFP. Uses end_date for auto live/closed."""
    if not cfp:
        return []
    items = []
    deadline_iso = frappe.utils.getdate(cfp.deadline).isoformat() if cfp.deadline else ""

    if cfp.creation:
        items.append(
            {
                "label": "CFP Opens",
                "date": frappe.utils.getdate(cfp.creation).isoformat(),
                "end_date": deadline_iso,
                "status": "",
            }
        )

    if cfp.deadline:
        items.append(
            {
                "label": "CFP Deadline",
                "date": deadline_iso,
                "end_date": deadline_iso,  # live on deadline day, closed after
                "status": "",
            }
        )

    return items


def _get_indiafoss_years():
    return [
        {"year": "2026", "url": "/indiafoss/2026", "name": "IndiaFOSS 2026"},
        {"year": "2025", "url": "/indiafoss/2025", "name": "IndiaFOSS 2025"},
        {"year": "2024", "url": "/indiafoss/2024", "name": "IndiaFOSS 2024"},
        {"year": "2023", "url": "/indiafoss/2023", "name": "IndiaFOSS 3.0"},
        {"year": "2022", "url": "/indiafoss/2022", "name": "IndiaFOSS 2.0"},
        {"year": "2021", "url": "/indiafoss/2021", "name": "IndiaOS"},
    ]
