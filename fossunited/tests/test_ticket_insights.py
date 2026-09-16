import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, now_datetime

from fossunited.api.tickets import get_tickets_insights, get_tickets_sold_over_time
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventTicketFactory,
)


class TestTicketInsightsAPI(FrappeTestCase):
    """Test cases for ticket purchase trends and insights API."""

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
            tiers=[
                {"enabled": 1, "title": "Early Bird", "price": 100, "maximum_tickets": 100},
                {"enabled": 1, "title": "Regular", "price": 200, "maximum_tickets": 100},
                {"enabled": 1, "title": "VIP", "price": 500, "maximum_tickets": 50},
            ],
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        for ticket in frappe.get_all(EVENT_TICKET, {"event": self.event.name}):
            frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.rollback()

    def _create_ticket(self, tier="Regular", days_ago=0, event_name=None):
        """Helper to create a ticket and optionally set its creation timestamp."""
        event_id = event_name or self.event.name
        ticket = FOSSEventTicketFactory.create(event=event_id, tier=tier)
        if days_ago != 0:
            creation_time = add_days(now_datetime(), -days_ago)
            frappe.db.set_value(
                EVENT_TICKET,
                ticket.name,
                "creation",
                creation_time,
                update_modified=False,
            )
        return ticket

    def test_empty_event_returns_empty_series_and_data(self):
        """Events without ticket sales should return empty data and series."""
        result = get_tickets_sold_over_time(self.event.name)
        self.assertEqual(result, {"data": [], "series": []})

    def test_single_ticket_single_day(self):
        """Single ticket sold on one day should produce one series and one data point."""
        ticket = self._create_ticket(tier="Regular", days_ago=2)
        ticket_date = getdate(
            frappe.db.get_value(EVENT_TICKET, ticket.name, "creation")
        ).isoformat()

        result = get_tickets_sold_over_time(self.event.name)

        self.assertEqual(len(result["series"]), 1)
        self.assertEqual(result["series"][0], {"key": "ticket_type_0", "label": "Regular"})

        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["date"], ticket_date)
        self.assertEqual(result["data"][0]["ticket_type_0"], 1)
        self.assertEqual(result["data"][0]["tickets_sold"], 1)

    def test_cumulative_sales_across_consecutive_days(self):
        """Daily ticket sales should accumulate monotonically across consecutive days."""
        # 2 tickets 2 days ago, 3 tickets 1 day ago
        self._create_ticket(tier="Regular", days_ago=2)
        self._create_ticket(tier="Regular", days_ago=2)

        self._create_ticket(tier="Regular", days_ago=1)
        self._create_ticket(tier="Regular", days_ago=1)
        self._create_ticket(tier="Regular", days_ago=1)

        result = get_tickets_sold_over_time(self.event.name)

        self.assertEqual(len(result["data"]), 2)

        # Day 1: 2 tickets
        self.assertEqual(result["data"][0]["ticket_type_0"], 2)
        self.assertEqual(result["data"][0]["tickets_sold"], 2)

        # Day 2: 2 + 3 = 5 tickets
        self.assertEqual(result["data"][1]["ticket_type_0"], 5)
        self.assertEqual(result["data"][1]["tickets_sold"], 5)

    def test_date_gaps_are_filled_with_cumulative_counts(self):
        """Days without ticket purchases between first and last sale should be filled with previous totals."""
        # 2 tickets 4 days ago, 1 ticket 1 day ago (days 3 and 2 have no sales)
        self._create_ticket(tier="Regular", days_ago=4)
        self._create_ticket(tier="Regular", days_ago=4)

        self._create_ticket(tier="Regular", days_ago=1)

        result = get_tickets_sold_over_time(self.event.name)

        # There should be 4 days in total: day -4, day -3, day -2, day -1
        self.assertEqual(len(result["data"]), 4)

        # Day -4
        self.assertEqual(result["data"][0]["ticket_type_0"], 2)
        self.assertEqual(result["data"][0]["tickets_sold"], 2)

        # Day -3 (filled gap: count remains 2)
        self.assertEqual(result["data"][1]["ticket_type_0"], 2)
        self.assertEqual(result["data"][1]["tickets_sold"], 2)

        # Day -2 (filled gap: count remains 2)
        self.assertEqual(result["data"][2]["ticket_type_0"], 2)
        self.assertEqual(result["data"][2]["tickets_sold"], 2)

        # Day -1 (new sale: count becomes 3)
        self.assertEqual(result["data"][3]["ticket_type_0"], 3)
        self.assertEqual(result["data"][3]["tickets_sold"], 3)

    def test_multiple_tiers_breakdown_and_casefold_sort(self):
        """Multiple tiers should be sorted case-insensitively and tracked independently."""
        # VIP and Early Bird tickets
        self._create_ticket(tier="VIP", days_ago=2)
        self._create_ticket(tier="early bird", days_ago=2)
        self._create_ticket(tier="VIP", days_ago=1)

        result = get_tickets_sold_over_time(self.event.name)

        # Series should be sorted case-insensitively: "early bird" before "VIP"
        expected_series = [
            {"key": "ticket_type_0", "label": "early bird"},
            {"key": "ticket_type_1", "label": "VIP"},
        ]
        self.assertEqual(result["series"], expected_series)

        self.assertEqual(len(result["data"]), 2)

        # Day 1: 1 early bird, 1 VIP -> total 2
        day_1 = result["data"][0]
        self.assertEqual(day_1["ticket_type_0"], 1)
        self.assertEqual(day_1["ticket_type_1"], 1)
        self.assertEqual(day_1["tickets_sold"], 2)

        # Day 2: 1 early bird (carried), 2 VIP -> total 3
        day_2 = result["data"][1]
        self.assertEqual(day_2["ticket_type_0"], 1)
        self.assertEqual(day_2["ticket_type_1"], 2)
        self.assertEqual(day_2["tickets_sold"], 3)

    def test_uncategorized_tier_handling(self):
        """Tickets without a tier should be grouped under 'Uncategorized'."""
        self._create_ticket(tier="", days_ago=1)

        result = get_tickets_sold_over_time(self.event.name)

        self.assertEqual(len(result["series"]), 1)
        self.assertEqual(result["series"][0]["label"], "Uncategorized")
        self.assertEqual(result["data"][0][result["series"][0]["key"]], 1)
        self.assertEqual(result["data"][0]["tickets_sold"], 1)

    def test_event_data_isolation(self):
        """Tickets from other events should not bleed into this event's statistics."""
        other_event = FOSSChapterEventFactory.create(
            "with_paid_tickets",
            chapter=self.chapter.name,
        )
        try:
            # 2 tickets for self.event, 5 tickets for other_event
            self._create_ticket(tier="Regular", days_ago=1, event_name=self.event.name)
            self._create_ticket(tier="Regular", days_ago=1, event_name=self.event.name)

            self._create_ticket(tier="VIP", days_ago=1, event_name=other_event.name)
            self._create_ticket(tier="VIP", days_ago=1, event_name=other_event.name)
            self._create_ticket(tier="VIP", days_ago=1, event_name=other_event.name)

            result = get_tickets_sold_over_time(self.event.name)
            self.assertEqual(result["data"][0]["tickets_sold"], 2)
            self.assertEqual(len(result["series"]), 1)
            self.assertEqual(result["series"][0]["label"], "Regular")
        finally:
            for ticket in frappe.get_all(EVENT_TICKET, {"event": other_event.name}):
                frappe.delete_doc(EVENT_TICKET, ticket.name, force=True)
            frappe.delete_doc(EVENT, other_event.name, force=True)

    def test_get_tickets_insights_includes_trend_data(self):
        """get_tickets_insights should include tickets_sold_over_time and ticket_sales_series."""
        self._create_ticket(tier="Regular", days_ago=1)

        insights = get_tickets_insights(self.event.name)
        expected_trends = get_tickets_sold_over_time(self.event.name)

        self.assertIn("tickets_sold_over_time", insights)
        self.assertIn("ticket_sales_series", insights)
        self.assertEqual(insights["tickets_sold_over_time"], expected_trends["data"])
        self.assertEqual(insights["ticket_sales_series"], expected_trends["series"])
