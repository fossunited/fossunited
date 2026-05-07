import frappe
from frappe.utils import now_datetime

from fossunited.doctype_ids import EVENT


def get_context(context):
    context.no_cache = 1

    now = now_datetime()

    events = frappe.get_all(
        EVENT,
        filters={
            "event_name": ["like", "%Maintainers%"],
            "event_start_date": [">=", now],
        },
        or_filters={
            "is_published": 1,
            "is_external_event": 1,
        },
        fields=[
            "name",
            "route",
            "external_event_url",
            "is_external_event",
            "event_name",
            "event_start_date",
            "event_location",
            "banner_image",
            "chapter",
            "chapter.chapter_name as _chapter_name",
            "chapter.city as _chapter_city",
        ],
        order_by="event_start_date asc",
        page_length=5,
    )

    for e in events:
        if e.event_start_date:
            dt = e.event_start_date
            e.date_day = dt.strftime("%d")
            e.date_month = dt.strftime("%b").upper()
            e.date_str = dt.strftime("%-d %B %Y")
        else:
            e.date_day = "TBD"
            e.date_month = ""
            e.date_str = "Date TBD"

    context.events = events

    blogs = frappe.get_all(
        "Blog Post",
        filters={"blog_category": "maintainers", "published": 1},
        fields=[
            "name",
            "title",
            "blog_intro",
            "published_on",
            "route",
            "read_time",
            "blogger.full_name as blogger_name",
            "blogger.avatar as blogger_avatar",
        ],
        order_by="published_on desc",
        page_length=7,
    )

    for blog in blogs:
        blog.date_str = blog.published_on.strftime("%-d %b %Y") if blog.published_on else ""

    context.blogs = blogs[:6]
    context.blogs_has_more = len(blogs) > 6

    context.partners_tier1 = frappe.get_all(
        "Industry Partners",
        filters={"special_category": ["like", "%maintainers-1%"]},
        fields=["company", "website", "logo"],
    )
    context.partners_tier2 = frappe.get_all(
        "Industry Partners",
        filters={"special_category": ["like", "%maintainers-2%"]},
        fields=["company", "website", "logo"],
    )

    context.video_youtube_id = "nV_1WCU0XOM"
    context.video_title = "Maintainers Program"

    context.links = frappe._dict(
        meetups="#meetups",
        pack="/maintainers-program/thesis",
        thesis="/maintainers-program/thesis",
        view_deck="https://fossunited.org/files/MP-deck.pdf",
        forklore="https://forklore.in",
        events="/events/timeline?s=maintainers",
        infra_grants="/grants/projects",
        fellowships="/grants/projects",
        other_grants="/grants",
    )
