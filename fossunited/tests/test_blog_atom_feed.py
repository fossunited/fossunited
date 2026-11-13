from datetime import date, datetime
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

import frappe
from blog.blog.doctype.blog_post.test_blog_post import make_test_blog
from frappe.tests.utils import FrappeTestCase

from fossunited.www.rss import get_context

NS = {"a": "http://www.w3.org/2005/Atom"}
HOST = "https://feed.example.invalid"


class TestBlogAtomFeed(FrappeTestCase):
    def setUp(self):
        self.blog = make_test_blog("Native Atom Category")
        self.blog.content_type = "HTML"
        self.blog.content_html = "<p>Native content</p>"
        self.blog.blog_intro = "Native summary"
        self.blog.published = 1
        self.blog.published_on = date(2020, 10, 1)
        self.blog.save()

    def tearDown(self):
        frappe.db.rollback()

    def render(self):
        with patch("fossunited.www.rss.get_request_site_address", return_value=HOST):
            context = get_context(frappe._dict())
            return ET.fromstring(frappe.render_template("fossunited/www/rss.xml", context))

    def entry(self, root):
        route = HOST + "/" + self.blog.route.lstrip("/")
        return next(
            e for e in root.findall("a:entry", NS) if e.findtext("a:id", namespaces=NS) == route
        )

    def test_xml_and_html_content(self):
        for kind, field, value in [
            ("Rich Text", "content", "<p>Native ]]> & नमस्ते</p>"),
            ("Markdown", "content_md", "**Native** ]]> & नमस्ते"),
        ]:
            with self.subTest(content_type=kind):
                frappe.db.set_value(
                    "Blog Post", self.blog.name, {"content_type": kind, field: value}
                )
                root = self.render()
                self.assertEqual(root.tag, "{http://www.w3.org/2005/Atom}feed")
                self.assertEqual(
                    root.attrib["{http://www.w3.org/XML/1998/namespace}base"], HOST + "/blog"
                )
                expected = frappe.utils.md_to_html(value) if kind == "Markdown" else value
                entry = self.entry(root)
                self.assertEqual(entry.findtext("a:content", namespaces=NS), expected)
                self.assertEqual(entry.find("a:content", NS).attrib["type"], "html")

    def test_author_and_category_use_real_linked_fields(self):
        entry = self.entry(self.render())
        self.assertEqual(
            entry.findtext("a:author/a:name", namespaces=NS),
            frappe.db.get_value("Blogger", self.blog.blogger, "full_name"),
        )
        category = entry.find("a:category", NS)
        self.assertEqual(
            category.attrib["label"],
            frappe.db.get_value("Blog Category", self.blog.blog_category, "title"),
        )
        category_route = frappe.db.get_value("Blog Category", self.blog.blog_category, "route")
        self.assertEqual(category.attrib["term"], HOST + "/" + category_route.lstrip("/"))

    def test_publication_is_date_only_midnight_site_timezone(self):
        entry = self.entry(self.render())
        published = datetime.fromisoformat(entry.findtext("a:published", namespaces=NS))
        self.assertEqual(published.date(), date(2020, 10, 1))
        self.assertEqual((published.hour, published.minute, published.second), (0, 0, 0))
        zone = ZoneInfo(frappe.utils.get_system_timezone())
        self.assertEqual(published.utcoffset(), datetime(2020, 10, 1, tzinfo=zone).utcoffset())
        updated = datetime.fromisoformat(entry.findtext("a:updated", namespaces=NS))
        self.assertIsNotNone(updated.utcoffset())

    def test_unpublished_and_future_posts_excluded(self):
        self.entry(self.render())  # Positive published entry control before hiding it.
        frappe.db.set_value("Blog Post", self.blog.name, "published_on", date(2099, 1, 1))
        root = self.render()
        self.assertNotIn(
            HOST + "/" + self.blog.route.lstrip("/"),
            [e.findtext("a:id", namespaces=NS) for e in root.findall("a:entry", NS)],
        )
        frappe.db.set_value(
            "Blog Post", self.blog.name, {"published_on": date(2020, 10, 1), "published": 0}
        )
        root = self.render()
        self.assertNotIn(
            HOST + "/" + self.blog.route.lstrip("/"),
            [e.findtext("a:id", namespaces=NS) for e in root.findall("a:entry", NS)],
        )
