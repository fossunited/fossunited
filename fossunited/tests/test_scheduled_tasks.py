from datetime import datetime, timedelta
from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from fossunited.scheduled_tasks import conclude_events
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.foss_event_cfp_submission_factory import FOSSEventCFPFactory
from fossunited.tests.factories.foss_event_rsvp_factory import FOSSEventRSVPFactory


class TestScheduledTasks(FrappeTestCase):
    def setUp(self):
        today = datetime.today()
        self.chapter = FOSSChapterFactory.create()

        self.event1 = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            status="Live",
            event_start_date=today.replace(hour=9, minute=00),
            event_end_date=today.replace(hour=15, minute=30),
        )
        self.event1_cfp = FOSSEventCFPFactory.create(event=self.event1.name, status="Live")
        self.event1_rsvp = FOSSEventRSVPFactory.create(event=self.event1.name, is_published=1)

        self.event2 = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            status="Cancelled",
            event_start_date=today.replace(hour=9, minute=00),
            event_end_date=today.replace(hour=15, minute=30),
        )
        self.event2_cfp = FOSSEventCFPFactory.create(event=self.event2.name, status="Live")
        self.event2_rsvp = FOSSEventRSVPFactory.create(event=self.event2.name, is_published=1)

        self.event3 = FOSSChapterEventFactory.create(
            chapter=self.chapter.name,
            event_start_date=today.replace(hour=9, minute=00) + timedelta(days=1),
            event_end_date=today.replace(hour=14, minute=00) + timedelta(days=2),
        )
        self.event3_cfp = FOSSEventCFPFactory.create(event=self.event3.name, status="Live")
        self.event3_rsvp = FOSSEventRSVPFactory.create(event=self.event3.name, is_published=1)

    @patch("fossunited.scheduled_tasks.now_datetime")
    def test_concluded_events(self, mock_now_datetime):
        mock_now_datetime.return_value = datetime.today().replace(hour=0, minute=1) + timedelta(
            days=1
        )
        conclude_events()

        self.event1.reload()
        self.event1_cfp.reload()
        self.event1_rsvp.reload()
        self.event2.reload()
        self.event2_cfp.reload()
        self.event2_rsvp.reload()
        self.event3.reload()
        self.event3_cfp.reload()
        self.event3_rsvp.reload()

        self.assertEqual(self.event1.status, "Concluded")
        self.assertEqual(self.event1_cfp.status, "Closed")
        self.assertEqual(self.event1_rsvp.is_published, 0)

        self.assertEqual(self.event2.status, "Cancelled")
        self.assertEqual(self.event2_cfp.status, "Live")
        self.assertEqual(self.event2_rsvp.is_published, 1)

        self.assertEqual(self.event3.status, "Live")
        self.assertEqual(self.event3_cfp.status, "Live")
        self.assertEqual(self.event3_rsvp.is_published, 1)
