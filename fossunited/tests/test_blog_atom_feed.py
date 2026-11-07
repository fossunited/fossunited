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

    def test_atom_valid_xml_full_content_summary_and_identity(self):
        self.blog.content_html = "<p>Native ]]> XML & non-ASCII: नमस्ते</p>"
        frappe.db.set_value("Blog Post", self.blog.name, "content_html", self.blog.content_html)
        root = self.render()
        self.assertEqual(root.tag, "{http://www.w3.org/2005/Atom}feed")
        entry = self.entry(root)
        self.assertEqual(entry.findtext("a:content", namespaces=NS), self.blog.content_html)
        self.assertEqual(entry.find("a:content", NS).attrib["type"], "html")
        self.assertEqual(entry.findtext("a:summary", namespaces=NS), self.blog.blog_intro)
        self.assertEqual(
            entry.findtext("a:id", namespaces=NS), HOST + "/" + self.blog.route.lstrip("/")
        )
        self.assertEqual(root.find("a:link[@rel='self']", NS).attrib["href"], HOST + "/rss.xml")
        self.assertEqual(root.find("a:link[@rel='alternate']", NS).attrib["href"], HOST + "/blog")

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

    def test_empty_feed_has_required_fields(self):
        frappe.db.sql("UPDATE `tabBlog Post` SET published=0")
        root = self.render()
        self.assertFalse(root.findall("a:entry", NS))
        self.assertTrue(root.findtext("a:title", namespaces=NS))
        self.assertTrue(root.findtext("a:id", namespaces=NS))
        updated = datetime.fromisoformat(root.findtext("a:updated", namespaces=NS))
        self.assertIsNotNone(updated.utcoffset())

    def test_markdown_and_text_editor_content(self):
        for kind, field, value, expected in [
            ("Markdown", "content_md", "**Native** & ]]> text", "<strong>Native</strong>"),
            ("Rich Text", "content", "<p>Rich & ]]> text</p>", "<p>Rich & ]]> text</p>"),
        ]:
            frappe.db.set_value("Blog Post", self.blog.name, {"content_type": kind, field: value})
            entry = self.entry(self.render())
            self.assertIn(expected, entry.findtext("a:content", namespaces=NS))

    def test_enclosure_no_invented_length_or_type(self):
        frappe.db.set_value("Blog Post", self.blog.name, "meta_image", "/files/native%20image.png")
        entry = self.entry(self.render())
        enclosure = entry.find("a:link[@rel='enclosure']", NS)
        self.assertEqual(
            enclosure.attrib, {"rel": "enclosure", "href": HOST + "/files/native%20image.png"}
        )

    def test_feed_settings_title_subtitle_escaped_once(self):
        settings = frappe.get_single("Blog Settings")
        settings.blog_title = "Native & <Blog>"
        settings.blog_introduction = "Intro & <subtitle>"
        settings.save()
        root = self.render()
        self.assertEqual(root.findtext("a:title", namespaces=NS), settings.blog_title)
        self.assertEqual(root.findtext("a:subtitle", namespaces=NS), settings.blog_introduction)

    def test_author_profile_uri_from_real_user_mapping(self):
        from fossunited.tests.factories import UserFactory

        user = UserFactory.create("with_foss_website_user_role")
        frappe.db.set_value("FOSS User Profile", {"user": user.name}, "is_published", 1)
        frappe.db.set_value("Blogger", self.blog.blogger, "user", user.name)
        route = frappe.db.get_value("FOSS User Profile", {"user": user.name}, "route")
        entry = self.entry(self.render())
        self.assertEqual(
            entry.findtext("a:author/a:uri", namespaces=NS), HOST + "/" + route.lstrip("/")
        )

    def test_unsafe_image_url_is_not_enclosed(self):
        for image in ("javascript:alert(1)", "data:image/png;base64,AAAA"):
            frappe.db.set_value("Blog Post", self.blog.name, "meta_image", image)
            self.assertIsNone(self.entry(self.render()).find("a:link[@rel='enclosure']", NS))

    def test_unpublished_author_profile_uri_not_exposed(self):
        from fossunited.tests.factories import UserFactory

        user = UserFactory.create("with_foss_website_user_role")
        frappe.db.set_value("Blogger", self.blog.blogger, "user", user.name)
        frappe.db.set_value("FOSS User Profile", {"user": user.name}, "is_published", 0)
        self.assertIsNone(self.entry(self.render()).find("a:author/a:uri", NS))

    def test_base_ordinary_content_author_field_control(self):
        with patch("fossunited.www.rss.get_request_site_address", return_value=HOST):
            context = get_context(frappe._dict())
        item = next(item for item in context["items"] if item.name == self.blog.name)
        self.assertEqual(
            item.author, frappe.db.get_value("Blogger", self.blog.blogger, "full_name")
        )

    def test_base_ordinary_content_category_field_control(self):
        with patch("fossunited.www.rss.get_request_site_address", return_value=HOST):
            context = get_context(frappe._dict())
        item = next(item for item in context["items"] if item.name == self.blog.name)
        self.assertEqual(
            item.category,
            HOST
            + "/"
            + frappe.db.get_value("Blog Category", self.blog.blog_category, "route").lstrip("/"),
        )

    def test_context_future_filter_not_vacuous(self):
        with patch("fossunited.www.rss.get_request_site_address", return_value=HOST):
            self.assertIn(
                self.blog.name, [item.name for item in get_context(frappe._dict())["items"]]
            )
            frappe.db.set_value("Blog Post", self.blog.name, "published_on", date(2099, 1, 1))
            self.assertNotIn(
                self.blog.name, [item.name for item in get_context(frappe._dict())["items"]]
            )

    def test_site_dst_offsets_and_actual_modified_time(self):
        frappe.db.set_value(
            "Blog Post",
            self.blog.name,
            {"published_on": date(2020, 7, 1), "modified": datetime(2020, 12, 1, 15, 45, 30)},
            update_modified=False,
        )
        with patch("fossunited.www.rss.get_system_timezone", return_value="America/New_York"):
            entry = self.entry(self.render())
        published = datetime.fromisoformat(entry.findtext("a:published", namespaces=NS))
        updated = datetime.fromisoformat(entry.findtext("a:updated", namespaces=NS))
        self.assertEqual(published.isoformat(), "2020-07-01T00:00:00-04:00")
        self.assertEqual(updated.isoformat(), "2020-12-01T15:45:30-05:00")

    def test_missing_links_and_optional_metadata(self):
        frappe.db.set_value(
            "Blog Post",
            self.blog.name,
            {"blogger": None, "blog_category": None, "meta_image": None, "blog_intro": None},
        )
        entry = self.entry(self.render())
        self.assertTrue(entry.findtext("a:author/a:name", namespaces=NS))
        self.assertIsNone(entry.find("a:author/a:uri", NS))
        self.assertIsNone(entry.find("a:category", NS))
        self.assertIsNone(entry.find("a:link[@rel='enclosure']", NS))
        self.assertNotIn("None", ET.tostring(entry, encoding="unicode"))

    def test_missing_route_uses_stable_non_url_id_not_none(self):
        frappe.db.set_value("Blog Post", self.blog.name, "route", None)
        root = self.render()
        entry = next(
            e
            for e in root.findall("a:entry", NS)
            if e.findtext("a:title", namespaces=NS) == self.blog.title
        )
        identifier = entry.findtext("a:id", namespaces=NS)
        self.assertTrue(identifier.startswith("urn:sha256:"))
        self.assertIsNone(entry.find("a:link[@rel='alternate']", NS))
        root_again = self.render()
        self.assertIn(
            identifier,
            [e.findtext("a:id", namespaces=NS) for e in root_again.findall("a:entry", NS)],
        )

    def test_empty_settings_use_nonempty_feed_title(self):
        frappe.db.set_single_value("Blog Settings", {"blog_title": "", "blog_introduction": ""})
        root = self.render()
        self.assertEqual(root.findtext("a:title", namespaces=NS), "FOSS United Blog")
        self.assertNotIn("None", ET.tostring(root, encoding="unicode"))

    def test_missing_route_identifier_is_site_namespaced(self):
        frappe.db.set_value("Blog Post", self.blog.name, "route", None)
        ids = []
        for host in ("https://first.example.invalid", "https://second.example.invalid"):
            with patch("fossunited.www.rss.get_request_site_address", return_value=host):
                context = get_context(frappe._dict())
            ids.append(next(item.guid for item in context["items"] if item.name == self.blog.name))
        self.assertNotEqual(*ids)


class TestBlogAtomHTTP(FrappeTestCase):
    def test_rss_route_uses_foss_atom_template_and_mime(self):
        from frappe.tests.test_api import make_request
        from frappe.utils import get_test_client

        # The framework helper runs the actual WSGI app in another thread/connection.
        # No uncommitted fixture needs to be visible to this request.
        response = make_request(
            target=get_test_client(use_cookies=False).get,
            args=(),
            kwargs={"path": "/rss.xml"},
            site=frappe.local.site,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/atom+xml")
        root = ET.fromstring(response.get_data(as_text=True))
        self.assertEqual(root.tag, "{http://www.w3.org/2005/Atom}feed")
        self.assertTrue(root.findtext("a:id", namespaces=NS).endswith("/rss.xml"))
