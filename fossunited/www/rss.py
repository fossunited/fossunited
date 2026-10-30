# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# Copyright (c) 2025, FOSS United Organization
# License: MIT. See LICENSE

from datetime import datetime, time
from hashlib import sha256
from urllib.parse import urljoin, urlsplit
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

from fossunited.doctype_ids import USER_PROFILE

no_cache = 1
base_template_path = "www/rss.xml"


def _public_url(host, route):
    if not route:
        return None
    url = urljoin(host.rstrip("/") + "/", route)
    parts = urlsplit(url)
    return url if parts.scheme in ("http", "https") and parts.netloc else None


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
            "meta_image",
        ],
        filters={"published": 1, "published_on": ["<=", today()]},
        order_by="published_on desc",
        limit=20,
    )
    blogger_names = list({blog.blogger for blog in blog_list if blog.blogger})
    category_names = list({blog.blog_category for blog in blog_list if blog.blog_category})
    bloggers = (
        {
            row.name: row
            for row in frappe.get_all(
                "Blogger",
                filters={"name": ["in", blogger_names]},
                fields=["name", "full_name", "user"],
            )
        }
        if blogger_names
        else {}
    )
    categories = (
        {
            row.name: row
            for row in frappe.get_all(
                "Blog Category",
                filters={"name": ["in", category_names]},
                fields=["name", "title", "route"],
            )
        }
        if category_names
        else {}
    )
    users = list({row.user for row in bloggers.values() if row.user})
    profiles = (
        {
            row.user: row
            for row in frappe.get_all(
                USER_PROFILE,
                filters={"user": ["in", users], "is_published": 1},
                fields=["user", "route"],
            )
        }
        if users
        else {}
    )
    settings = frappe.get_single("Blog Settings")
    title = settings.blog_title or "FOSS United Blog"
    description = settings.blog_introduction or ""

    for blog in blog_list:
        blog.link = _public_url(host, blog.route)
        blog.guid = (
            blog.link
            or "urn:sha256:" + sha256(f"{host.rstrip('/')}:{blog.name}".encode()).hexdigest()
        )
        blog.title = blog.title or blog.name
        blogger = bloggers.get(blog.blogger)
        blog.author = (blogger.full_name if blogger else None) or title
        profile = profiles.get(blogger.user) if blogger else None
        blog.author_uri = _public_url(host, profile.route) if profile else None
        category = categories.get(blog.blog_category)
        blog.category = _public_url(host, category.route) if category else None
        blog.category_title = category.title if category else None
        # published_on has Date precision only. Midnight in the site timezone is
        # an explicit serialization convention, not a known publication time.
        blog.published_date = _atom_date(
            datetime.combine(get_datetime(blog.published_on).date(), time()), zone
        )
        blog.updated = _atom_date(blog.modified, zone)
        attr = {"Markdown": "content_md", "HTML": "content_html"}.get(blog.content_type, "content")
        value = blog.get(attr) or ""
        blog.content = md_to_html(value) if blog.content_type == "Markdown" else value
        blog.enclosure = _public_url(host, blog.meta_image)

    modified = max((get_datetime(blog.modified) for blog in blog_list), default=now_datetime())
    # TemplatePage's XML MIME default is overridden only for this response.
    if not getattr(frappe.local, "response_headers", None):
        frappe.local.response_headers = {}
    frappe.local.response_headers["Content-Type"] = "application/atom+xml; charset=utf-8"
    return {
        "title": title,
        "description": description,
        "modified": _atom_date(modified, zone),
        "items": blog_list,
        "link": _public_url(host, "/blog"),
        "feed_url": _public_url(host, "/rss.xml"),
    }
