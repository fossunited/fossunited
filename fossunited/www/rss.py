"""Atom feed of blog posts, served at rss.xml (template: templates/rss.xml)."""

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# Copyright (c) 2025, FOSS United Organization
# License: MIT. See LICENSE

import mimetypes
from urllib.parse import urlencode, urlparse

import frappe
from frappe.utils import md_to_html, today

from fossunited.utils.rss import feed_context, public_url

no_cache = 1
base_template_path = "www/rss.xml"


def get_context(context):
    """Generate the blog Atom feed."""
    posts = frappe.get_all(
        "Blog Post",
        fields=[
            "published_on",
            "modified",
            "title",
            "blog_intro",
            "route",
            "external_url",
            "content_md",
            "content",
            "content_html",
            "content_type",
            "blogger",
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

    entries = []
    for post in posts:
        # id stays our own URL so it survives edits to external_url; readers open the real post
        post_url = public_url(post.route)
        attr = {"Markdown": "content_md", "HTML": "content_html"}.get(post.content_type, "content")
        body = post.get(attr) or ""
        image = public_url(post.meta_image)
        entry = {
            "id": post_url,
            "title": post.title,
            "link": post.external_url or post_url,
            "published": post.published_on,
            "updated": post.modified,
            "author": post.author,
            "author_uri": public_url("/blog?" + urlencode({"blogger": post.blogger})),
            "category": public_url(post.category_route),
            "category_label": post.category_title,
            "summary": post.blog_intro,
            "content": md_to_html(body) if post.content_type == "Markdown" else body,
            "image": image,
            "image_type": mimetypes.guess_type(image or "")[0],
        }
        if post.external_url:
            origin = urlparse(post.external_url)
            entry["content"] = ""
            entry["source_title"] = origin.netloc
            entry["source_link"] = f"{origin.scheme}://{origin.netloc}/"
        entries.append(entry)

    return feed_context(
        settings.blog_title or "FOSS United Blog",
        settings.blog_introduction,
        "/blog",
        "/rss.xml",
        entries,
    )
