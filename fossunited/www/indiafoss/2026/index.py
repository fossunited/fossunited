import datetime
import json

import frappe

from fossunited.doctype_ids import COMMUNITY_PARTNER, EVENT, EVENT_CFP
from fossunited.fossunited.event_media import get_indiafoss_years
from fossunited.fossunited.user_utils import fetch_user_profiles
from fossunited.fossunited.utils import get_event_sponsors

INDIAFOSS_2026_EVENT = "IndiaFOSS 2026"
TIER1 = {"Maintainer", "Patrons", "Platinum", "Gold"}


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
    context.cta_buttons = _get_cta_buttons(event, cfp, event_data.get("cta_buttons"))
    context.countdown = _get_countdown(event)
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
        dr.svg_path = f"fossunited/public/images/indiafoss/if26-{dr.slug}.svg"
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
    # Manual label wins: drop auto-generated items whose label appears in JSON timeline
    manual_tl = event_data.get("timeline", [])
    cfp_tl = _get_cfp_timeline_items(cfp, today)
    manual_labels = {item.get("label") for item in manual_tl}
    cfp_tl = [item for item in cfp_tl if item.get("label") not in manual_labels]
    # Order by closing date (the actionable deadline); milestones with no end fall
    # back to their single start date.
    merged_tl = sorted(
        manual_tl + cfp_tl,
        key=lambda x: (
            _parse_date(x.get("end")) or _parse_date(x.get("start")) or datetime.date.max
        ),
    )
    context.timeline = _enrich_timeline(merged_tl, today)
    # Ticket availability is authoritative from the Event doctype (tickets_status),
    tickets_status = "live" if event.get("tickets_status") == "Live" else "closed"
    for item in context.timeline:
        if item.get("url") == "/indiafoss/tickets":
            item["resolved_status"] = tickets_status
    context.progress_segments, context.progress_markers = _get_progress_bar(
        context.timeline, today
    )
    context.progress_pct = round(
        max(0.0, min(100.0, (today - BAR_START).days * 100.0 / (BAR_END - BAR_START).days)), 1
    )
    context.action_cards = _enrich_action_cards(
        event_data.get("action_cards", []), context.timeline, today
    )
    # urgency banner: every deadline pin closing within 7 days (incl. today), soonest first
    context.urgency_items = sorted(
        (
            {"label": m["full_label"], "days": m["days_away"]}
            for m in context.progress_markers
            if m.get("is_end") and m["days_away"] is not None and 0 <= m["days_away"] <= 7
        ),
        key=lambda x: x["days"],
    )
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
    context.years = get_indiafoss_years()
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
    context.update(
        {
            k: []
            for k in (
                "sponsors",
                "partners",
                "co_chairs",
                "reviewers",
                "devroom_managers",
                "volunteers",
                "devrooms",
                "timeline",
                "action_cards",
                "faqs",
                "topics",
                "progress_segments",
                "progress_markers",
            )
        }
    )
    context.update(
        cta_buttons=[_btn("Get Tickets", "", primary=True)],
        countdown=frappe._dict(start="", end="", state="upcoming", days=None),
        event_date_str="2026",
        event_location="Bengaluru",
        map_link="",
        urgency_items=[],
        rewind={},
        footer_links={},
        today_str=frappe.utils.getdate(frappe.utils.today()).isoformat(),
        event_docname="",
        years=get_indiafoss_years(),
        current_year=2026,
        deck_link="",
        community_deck_link="",
        pagetitle="IndiaFOSS 2026",
        description="The 6th Edition of the FOSS and Digital Commons Festival by the FOSS United community",
    )


# Progress bar spans the run-up to the event.
BAR_START = datetime.date(2026, 4, 1)
BAR_END = datetime.date(2026, 9, 26)


def _enrich_timeline(items, today):
    """
    Add display fields to each item in place, all derived from its [start, end]
    window vs today. The only thing to hand-maintain is the two dates.

    day_num/month_str : the *context* date badge -- the opening date while the
                        item is still upcoming, then the closing date once open.
    range_info        : "Opens 12 Aug . Closes 1 Oct" for the per-row info tooltip
                        (form items with both dates); "" for a milestone.
    resolved_status   : "" (milestone / not yet open) | live | closing | closed.
    closing_days      : days until end when closing (<= 7), else None.
    extended          : cosmetic passthrough -> badge reads "Extended".

    An item with no `end` is a milestone (a single dated point): no status badge.
    To extend a deadline, just edit `end` -- there is no separate override.
    """
    for item in items:
        start_d = _parse_date(item.get("start"))
        end_d = _parse_date(item.get("end"))

        open_now = bool(end_d) and bool(start_d) and today >= start_d
        badge_d = end_d if open_now else start_d
        item["day_num"] = (
            badge_d.strftime("%-d")
            if badge_d
            else (item.get("start", "")[8:10].lstrip("0") or "?")
        )
        item["month_str"] = badge_d.strftime("%b") if badge_d else ""
        item["closing_days"] = None
        item["extended"] = bool(item.get("extended"))
        if start_d and end_d:
            o = "Opened" if today >= start_d else "Opens"
            c = "Closed" if today > end_d else "Closes"
            info = f"{o} {start_d.strftime('%-d %b')} · {c} {end_d.strftime('%-d %b')}"
            item["range_info"] = info + " (extended)" if item["extended"] else info
        else:
            item["range_info"] = ""

        if not start_d or not end_d or today < start_d:
            item["resolved_status"] = ""  # milestone, or window not yet open
        elif today > end_d:
            item["resolved_status"] = "closed"
        else:
            days_left = (end_d - today).days
            if days_left <= 7:
                item["resolved_status"] = "closing"
                item["closing_days"] = days_left
            else:
                item["resolved_status"] = "live"
    return items


def _get_progress_bar(timeline, today):
    """Week-based bar Apr-Sep 2026 + pins from marker:true items (start + deadline)."""
    total_days = (BAR_END - BAR_START).days
    today_offset = (today - BAR_START).days

    segments = []
    for w in range(-(-total_days // 7)):  # ceil weeks
        week_start = BAR_START + datetime.timedelta(days=w * 7)
        week_end = min(BAR_START + datetime.timedelta(days=w * 7 + 6), BAR_END)
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

    # an item shows on the bar when it has a `pin` chip label: a start pin, plus an
    # end pin (ti-ban rendered in template) when it has an `end` date.
    pins = []
    for item in timeline:
        pin_text = (item.get("pin") or "").strip()
        start_d = _parse_date(item.get("start")) if pin_text else None
        if not start_d:
            continue
        full_label = item.get("label", "")
        pins.append(
            {
                "date": start_d,
                "label": pin_text,
                "full_label": full_label,
                "tooltip": item.get("description") or full_label,
                "is_end": False,
            }
        )
        end_d = _parse_date(item.get("end"))
        if end_d:
            pins.append(
                {
                    "date": end_d,
                    "label": pin_text,
                    "full_label": full_label,
                    "tooltip": f"{full_label} Deadline",
                    "is_end": True,
                }
            )
    pins.sort(key=lambda p: p["date"])

    # urgent = next deadline pin (incl. today), else next pin, within 30 days
    next_idx = next(
        (i for i, p in enumerate(pins) if p["is_end"] and p["date"] >= today),
        next((i for i, p in enumerate(pins) if p["date"] >= today), None),
    )

    markers = []
    last_above_pct = last_below_pct = -100.0
    for idx, pin in enumerate(pins):
        pct = max(0.0, min(100.0, (pin["date"] - BAR_START).days * 100.0 / total_days))
        days_away = (pin["date"] - today).days
        # alternate crowded labels above/below the bar to avoid overlap
        above = (pct - last_above_pct) >= 15
        if above:
            last_above_pct = pct
        compact = not above and (pct - last_below_pct) < 15
        if not above and not compact:
            last_below_pct = pct
        is_urgent = idx == next_idx and 0 <= days_away <= 30
        markers.append(
            {
                "label": pin["label"],
                "is_end": pin["is_end"],
                "full_label": pin["full_label"],
                "description": pin["tooltip"],
                "pct": round(pct, 1),
                "is_past": pin["date"] < today,
                "is_urgent": is_urgent,
                "above": above,
                "compact": compact,
                "days_away": days_away,
            }
        )
    return segments, markers


def _btn(label, url, primary=False):
    return {"label": label, "url": url, "primary": primary}


def _get_cta_buttons(event, cfp, custom=None):
    if custom:
        return [_btn(b.get("label", ""), b.get("url", ""), bool(b.get("primary"))) for b in custom]

    # Get Tickets appears only while tickets_status is Live; when closed it drops
    # out and the next button in the cascade is promoted to primary.
    tickets = _btn("Get Tickets", "/indiafoss/tickets", primary=True)
    tickets_live = event.get("tickets_status") == "Live"

    if event.status == "Concluded" and event.show_photos:
        return [
            _btn("See Photos", "#photos", primary=True),
            _btn("See Schedule", "/indiafoss/schedule"),
        ]
    if event.show_schedule:
        base = [_btn("See Schedule", "/indiafoss/schedule", primary=True)]
        return [*base, {**tickets, "primary": False}] if tickets_live else base
    if cfp and cfp.status == "Closed":
        proposals = _btn("View Proposals", "/indiafoss/talks")
        return [tickets, proposals] if tickets_live else [{**proposals, "primary": True}]
    if cfp and cfp.status == "Live":
        propose = _btn("Propose a Talk", "/indiafoss/cfp")
        return [tickets, propose] if tickets_live else [{**propose, "primary": True}]
    return [tickets] if tickets_live else []


def _get_countdown(event):
    """Fixed start/end unix-ms for the JS clock, plus an SSR state/days fallback.

    The client owns the live ticking (D/H/M/S) and the state flip, so a cached page
    stays correct: it recomputes from these timestamps, not from render-time "today".
    """
    if not event.event_start_date:
        return frappe._dict(start="", end="", state="upcoming", days=None)
    now = frappe.utils.now_datetime()
    start = frappe.utils.get_datetime(event.event_start_date)
    end = frappe.utils.get_datetime(event.event_end_date or event.event_start_date)
    state = "concluded" if now > end else "live" if now >= start else "upcoming"
    # Append +05:30 offset (IST) client side
    return frappe._dict(
        start=start.isoformat(timespec="seconds"),
        end=end.isoformat(timespec="seconds"),
        state=state,
        days=(start.date() - now.date()).days if state == "upcoming" else None,
    )


def _get_date_str(event):
    if not event.event_start_date:
        return ""
    s = frappe.utils.getdate(event.event_start_date)
    if event.event_end_date:
        e = frappe.utils.getdate(event.event_end_date)
        return f"{s.strftime('%-d')}-{e.strftime('%-d %B %Y')}"
    return s.strftime("%-d %B %Y")


def _get_cfp_timeline_items(cfp, today):
    """Single CFP window (opens -> deadline) auto-derived from EVENT_CFP. The `pin`
    puts it on the bar (start pin + deadline pin); status auto-derives from dates.
    Override by adding a JSON timeline item labeled 'CFP' (same-label manual wins)."""
    if not cfp or not cfp.deadline:
        return []
    return [
        {
            "label": "CFP",
            "pin": "CFP",
            "start": frappe.utils.getdate(cfp.creation or cfp.deadline).isoformat(),
            "end": frappe.utils.getdate(cfp.deadline).isoformat(),
        }
    ]


def _enrich_action_cards(explicit_cards, timeline, today):
    """Explicit JSON cards + timeline items flagged card:true (deduped by label)."""
    cards = []
    for card in explicit_cards:
        card = dict(card)
        if card.get("deadline"):
            card["resolved_badge"], card["badge_state"], card["clickable"] = _deadline_badge(
                _parse_date(card["deadline"]), today
            )
        else:
            raw = card.get("badge") or ""
            card["resolved_badge"] = raw
            card["badge_state"] = "live" if raw.lower() == "live" else ""
            card["clickable"] = True
        cards.append(card)

    seen = {c["label"] for c in cards}
    for item in timeline:
        if not item.get("card") or item.get("label") in seen:
            continue
        deadline = item.get("end")
        badge, state, clickable = _deadline_badge(_parse_date(deadline), today)
        cards.append(
            {
                "label": item.get("label", ""),
                "url": item.get("url") or "",
                "icon": item.get("icon") or "",
                "description": item.get("description") or "",
                "resolved_badge": badge,
                "badge_state": state,
                "clickable": clickable if deadline else True,
            }
        )
    return cards


def _deadline_badge(deadline, today):
    """(badge_text, badge_state, clickable) for an effective deadline date."""
    if not deadline:
        return None, None, True
    days = (deadline - today).days
    if days < 0:
        return "Closed", "closed", False
    if days == 0:
        return "Closing today", "warning", True
    if days <= 7:
        unit = "day" if days == 1 else "days"
        return f"Closing in {days} {unit}", "warning", True
    return "Live", "live", True


def _parse_date(value):
    """frappe.utils.getdate() or None on empty/invalid input."""
    if not value:
        return None
    try:
        return frappe.utils.getdate(value)
    except Exception:
        return None
