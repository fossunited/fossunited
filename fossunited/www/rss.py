# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# Copyright (c) 2025, FOSS United Organization
# License: MIT. See LICENSE

from datetime import datetime, time
from email.utils import format_datetime
from urllib.parse import urljoin

import frappe
from frappe.utils import escape_html, get_request_site_address, markdown

no_cache = 1
base_template_path = "www/rss.xml"


def get_context(context):
    """generate rss feed for both blogs & newsletters"""

    host = get_request_site_address()

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
        ],
        filters={"published": 1},
        order_by="published_on desc",
        limit=20,
    )

    news_list = frappe.get_all(
        "Newsletter",
        fields=[
            "name",
            "modified",
            "subject",
            "sender_name",
            "sender_email",
            "route",
            "message_md",
            "message",
            "message_html",
            "content_type",
        ],
        filters={"published": 1},
        order_by="modified desc",
        limit=20,
    )

    for blog in blog_list + news_list:
        blog.link = urljoin(host, blog.route)
        blog.title = escape_html(
            getattr(blog, "title", None) or getattr(blog, "subject", "") or ""
        )
        blog.author = escape_html(
            getattr(blog, "blogger", None)
            or (
                f"{blog.sender_name} <{blog.sender_email}>" if hasattr(blog, "sender_name") else ""
            )
        )
        blog.published_date = format_datetime(
            datetime.combine(getattr(blog, "published_on", None) or blog.modified, time())
        )
        prefix = "message_" if blog.route.startswith("newsletters/") else "content_"
        attr = {"Markdown": prefix + "md", "HTML": prefix + "html"}.get(
            blog.content_type, prefix.rstrip("_")
        )
        value = getattr(blog, attr)
        blog_content = markdown(value) if blog.content_type == "Markdown" else value
        blog.content = f"<![CDATA[{blog_content}]]>"

    all_items = blog_list + news_list
    if all_items:
        modified = format_datetime(max(blog["modified"] for blog in all_items))
    else:
        modified = format_datetime(datetime.now())

    try:
        blog_settings = frappe.get_doc("Blog Settings", "Blog Settings")
        title = blog_settings.blog_title or "Blog"
        description = blog_settings.blog_introduction or ""
    except frappe.DoesNotExistError:
        title = "FOSS United Blog"
        description = "Latest updates from FOSS United"

    context = {
        "title": title,
        "description": description,
        "modified": modified,
        "items": blog_list + news_list,
        "link": host + "/blog",
        "feed_url": host + "/rss.xml",
    }

    return context
