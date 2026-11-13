# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# Copyright (c) 2025, FOSS United Organization
# License: MIT. See LICENSE

from datetime import datetime, time
from urllib.parse import urlencode, urljoin
from zoneinfo import ZoneInfo

import frappe
from frappe.utils import (
    get_datetime,
    get_request_site_address,
    get_system_timezone,
    md_to_html,
    now_datetime,
    today,
)

no_cache = 1
base_template_path = "www/rss.xml"


def _public_url(host, route):
    return urljoin(host.rstrip("/") + "/", route) if route else None


def _atom_date(value, zone):
    value = get_datetime(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=zone)
    return value.isoformat(timespec="seconds")


def get_context(context):
    """Generate the blog Atom feed. Other RSS feeds use their existing templates."""
    host = get_request_site_address()
    zone = ZoneInfo(get_system_timezone())
    blog_list = frappe.get_all(
        "Blog Post",
        fields=[
            "name",
            "published_on",
            "modified",
            "title",
            "blog_intro",
            "route",
            "content_md",
            "content",
            "content_html",
            "content_type",
            "blogger",
            "blog_category",
            "blogger.full_name as author",
            "blog_category.title as category_title",
            "blog_category.route as category_route",
            "meta_image",
        ],
        filters={"published": 1, "published_on": ["<=", today()]},
        order_by="published_on desc",
        limit=20,
    )
    settings = frappe.get_single("Blog Settings")
    title = settings.blog_title or "FOSS United Blog"
    description = settings.blog_introduction or ""

    for blog in blog_list:
        blog.link = _public_url(host, blog.route)
        blog.guid = blog.link
        blog.author = blog.author or title
        blog.author_uri = _public_url(host, "/blog?" + urlencode({"blogger": blog.blogger}))
        blog.category = _public_url(host, blog.category_route)
        # published_on has Date precision; serialize it at midnight in the site timezone.
        blog.published_date = datetime.combine(blog.published_on, time(), zone).isoformat()
        blog.updated = _atom_date(blog.modified, zone)
        attr = {"Markdown": "content_md", "HTML": "content_html"}.get(blog.content_type, "content")
        value = blog.get(attr) or ""
        blog.content = md_to_html(value) if blog.content_type == "Markdown" else value
        blog.enclosure = _public_url(host, blog.meta_image)

    modified = max((get_datetime(blog.modified) for blog in blog_list), default=now_datetime())
    # TemplatePage's XML MIME default is overridden only for this response.
    frappe.local.response_headers.set("Content-Type", "application/atom+xml; charset=utf-8")
    return {
        "title": title,
        "description": description,
        "modified": _atom_date(modified, zone),
        "items": blog_list,
        "link": _public_url(host, "/blog"),
        "feed_url": _public_url(host, "/rss.xml"),
    }
