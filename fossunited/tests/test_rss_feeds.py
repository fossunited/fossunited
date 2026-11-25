from datetime import datetime
from unittest.mock import patch
from xml.etree import ElementTree as ET

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.www.c import rss as chapter_feed
from fossunited.www.events.timeline import rss as timeline_feed
from fossunited.www.grants.grantees import rss as grantees_feed
from fossunited.www.jobs import rss as jobs_feed

NS = {"a": "http://www.w3.org/2005/Atom"}
HOST = "https://feed.example.invalid"
FEEDS = ["/rss.xml", "/events/timeline/rss.xml", "/grants/grantees/rss.xml", "/jobs/rss.xml"]

EVENT = frappe._dict(
    name="evt-1",
    route="events/py-meetup",
    event_name="Python & Friends",
    event_location="Pune & Co",
    event_type="Meet Up",
    event_start_date=datetime(2030, 12, 1, 18, 0),
    event_end_date=datetime(2030, 12, 1, 20, 0),
    event_description="<p>Bring ]]> laptops</p>",
    modified=datetime(2030, 11, 20, 9, 30),
    is_published=1,
)


class TestAtomFeeds(FrappeTestCase):
    def render(self, feed, template, path):
        """Render a feed page and check what every feed must have."""
        with patch("fossunited.utils.rss.get_request_site_address", return_value=HOST):
            context = feed.get_context(frappe._dict())
        root = ET.fromstring(frappe.render_template(template, context))
        self.assertEqual(root.tag, "{http://www.w3.org/2005/Atom}feed")
        self.assertEqual(root.find("a:link[@rel='self']", NS).attrib["href"], HOST + path)
        for entry in root.findall("a:entry", NS):
            for field in ("id", "title", "published", "updated"):
                self.assertTrue(entry.findtext(f"a:{field}", namespaces=NS), field)
            published = datetime.fromisoformat(entry.findtext("a:published", namespaces=NS))
            self.assertIsNotNone(published.utcoffset())
        return root

    def test_chapter_feed(self):
        chapter = frappe._dict(
            chapter_name="Pune & Co",
            slug="pune",
            route="c/pune",
            get_upcoming_events=lambda: [EVENT],
        )
        with (
            patch.dict(frappe.form_dict, {"chapter": "pune"}),
            patch("fossunited.www.c.rss.frappe.get_doc", return_value=chapter),
        ):
            root = self.render(chapter_feed, "fossunited/www/c/rss.xml", "/c/pune/rss.xml")
        entry = root.find("a:entry", NS)
        self.assertEqual(entry.findtext("a:title", namespaces=NS), "Python & Friends | Pune & Co")
        self.assertEqual(entry.findtext("a:author/a:name", namespaces=NS), "Pune & Co")
        content = entry.findtext("a:content", namespaces=NS)
        self.assertIn("Pune &amp; Co", content)
        self.assertIn("Bring ]]> laptops", content)

    def test_timeline_feed(self):
        item = frappe._dict(EVENT, _chapter_name="Pune")
        with patch(
            "fossunited.www.events.timeline.rss.get_foss_timeline_items", return_value=[item]
        ):
            root = self.render(
                timeline_feed,
                "fossunited/www/events/timeline/rss.xml",
                "/events/timeline/rss.xml",
            )
        entry = root.find("a:entry", NS)
        self.assertEqual(entry.find("a:link", NS).attrib["href"], HOST + "/events/py-meetup")
        self.assertEqual(entry.find("a:category", NS).attrib["term"], "Meet Up")

    def test_grantees_feed(self):
        project = frappe._dict(
            project_name="Tool & Co",
            grant_type="Project",
            grant_amount=50000,
            date_of_provision=datetime(2030, 1, 5).date(),
            modified=datetime(2030, 1, 6, 10, 0),
            project_website="https://example.invalid/tool",
            about_project="About ]]> the tool",
        )
        event = frappe._dict(
            event_name="Conf",
            grant_amount=None,
            event_start_date=datetime(2030, 2, 1, 9, 0),
            modified=datetime(2030, 1, 8, 10, 0),
            event_website="javascript:alert(1)",
            event_description=None,
            event_organiser="Org",
        )
        base = "fossunited.www.grants.grantees.rss"
        with (
            patch(f"{base}.fetch_project_grants", return_value=[project]),
            patch(f"{base}.fetch_fellowship_grants", return_value=[]),
            patch(f"{base}.fetch_event_grants", return_value=[event]),
        ):
            root = self.render(
                grantees_feed,
                "fossunited/www/grants/grantees/rss.xml",
                "/grants/grantees/rss.xml",
            )
        titles = [e.findtext("a:title", namespaces=NS) for e in root.findall("a:entry", NS)]
        self.assertEqual(titles, ["Conf (Event Grant)", "Tool & Co (Project Grant)"])
        unsafe = root.find("a:entry", NS)
        self.assertEqual(unsafe.find("a:link", NS).attrib["href"], HOST + "/grants/grantees")
        self.assertIn("%26", root.findall("a:entry", NS)[1].findtext("a:id", namespaces=NS))

    def test_jobs_feed(self):
        job = frappe._dict(
            job_title="Engineer",
            company_name="Acme & Co",
            job_location="Remote",
            job_type="Full Time",
            job_description="**Apply** ]]> now",
            application_link="https://example.invalid/apply",
            route="jobs/engineer",
            creation=datetime(2030, 3, 1, 8, 0),
            modified=datetime(2030, 3, 2, 8, 0),
        )
        with patch("fossunited.www.jobs.rss.frappe.get_all", return_value=[job]):
            root = self.render(jobs_feed, "fossunited/www/jobs/rss.xml", "/jobs/rss.xml")
        entry = root.find("a:entry", NS)
        self.assertEqual(entry.findtext("a:title", namespaces=NS), "Engineer at Acme & Co")
        self.assertEqual(entry.findtext("a:author/a:name", namespaces=NS), "Acme & Co")
        self.assertIn("https://example.invalid/apply", entry.findtext("a:content", namespaces=NS))


class TestAtomFeedsHTTP(FrappeTestCase):
    def test_feed_routes_serve_atom(self):
        from frappe.tests.test_api import make_request
        from frappe.utils import get_test_client

        # Runs the real WSGI app on another connection, so only feed-level fields are checked.
        for path in FEEDS:
            with self.subTest(path=path):
                response = make_request(
                    target=get_test_client(use_cookies=False).get,
                    args=(),
                    kwargs={"path": path},
                    site=frappe.local.site,
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "application/atom+xml")
                root = ET.fromstring(response.get_data(as_text=True))
                self.assertEqual(root.tag, "{http://www.w3.org/2005/Atom}feed")
                self.assertTrue(root.findtext("a:id", namespaces=NS).endswith(path))
