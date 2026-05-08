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
            "chapter.chapter_name as chapter_name",
            "chapter.city as chapter_city",
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
            "blogger.user as blogger_user",
        ],
        order_by="published_on desc",
    )

    for blog in blogs:
        blog.date_str = blog.published_on.strftime("%-d %b %Y") if blog.published_on else ""
        if not blog.blogger_avatar and blog.blogger_user:
            blog.blogger_avatar = frappe.db.get_value("User", blog.blogger_user, "user_image")

    context.blogs = blogs

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

    context.videos = [
        {"youtube_id": "nV_1WCU0XOM", "title": "Maintainers Program"},
    ]

    context.links = frappe._dict(
        meetups="#meetups",
        pack="",
        thesis="/maintainers/thesis",
        view_deck="https://fossunited.org/files/MP-deck.pdf",
        forklore="https://forklore.in",
        events="/events/timeline?s=maintainers",
        infra_grants="/grants/projects",
        fellowships="/grants/fellowships",
        other_grants="/grants",
    )
