# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# Copyright (c) 2025, FOSS United Organization
# License: MIT. See LICENSE

from datetime import datetime, time
from email.utils import format_datetime
from urllib.parse import urljoin

import frappe
from frappe.utils import escape_html, get_request_site_address, md_to_html

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

    for blog in blog_list:
        blog.link = urljoin(host, blog.route)
        blog.title = escape_html(
            getattr(blog, "title", None) or getattr(blog, "subject", "") or ""
        )
        blog.author = escape_html(getattr(blog, "blogger", None) or "")
        blog.published_date = format_datetime(
            datetime.combine(getattr(blog, "published_on", None) or blog.modified, time())
        )
        attr = {"Markdown": "content_md", "HTML": "content_html"}.get(blog.content_type, "content")
        value = getattr(blog, attr)
        if blog.content_type == "Markdown":
            blog_content = md_to_html(value)
        else:
            blog_content = value
        blog.content = f"<![CDATA[{blog_content}]]>"
        blog.guid = blog.link
        blog.category = ""

    all_items = blog_list
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
        "items": blog_list,
        "link": host + "/blog",
        "feed_url": host + "/rss.xml",
    }

    return context
