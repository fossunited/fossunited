from typing import ClassVar

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from fossunited.api.cfp import get_cfp_from_route
from fossunited.doctype_ids import EVENT_CFP
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
)


class TestFOSSEventCFP(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        for name in frappe.get_all(EVENT_CFP, {"event": self.event.name}, pluck="name"):
            frappe.delete_doc(EVENT_CFP, name, force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

    def _route_param(self) -> str:
        # api looks up the event by {"route": f"c/{route}"}, so strip the leading "c/".
        return self.event.route.split("c/", 1)[1]

    def _make_cfp(self, deadline, status="Live"):
        return FOSSEventCFPFactory.create(
            event=self.event.name,
            deadline=deadline,
            status=status,
        )

    def test_read_flips_when_past_deadline(self):
        cfp = self._make_cfp(deadline=add_to_date(now_datetime(), days=-1))

        result = get_cfp_from_route(self._route_param())

        self.assertEqual(result.status, "Closed")
        self.assertEqual(frappe.db.get_value(EVENT_CFP, cfp.name, "status"), "Closed")

    def test_future_deadline_stays_live(self):
        cfp = self._make_cfp(deadline=add_to_date(now_datetime(), days=1))

        result = get_cfp_from_route(self._route_param())

        self.assertEqual(result.status, "Live")
        self.assertEqual(frappe.db.get_value(EVENT_CFP, cfp.name, "status"), "Live")

    def test_null_deadline_stays_live(self):
        cfp = self._make_cfp(deadline=None)

        result = get_cfp_from_route(self._route_param())

        self.assertEqual(result.status, "Live")
        self.assertEqual(frappe.db.get_value(EVENT_CFP, cfp.name, "status"), "Live")

    def test_already_closed_is_same(self):
        cfp = self._make_cfp(deadline=add_to_date(now_datetime(), days=-1), status="Closed")

        self.assertFalse(cfp.close_if_past_deadline())
        self.assertEqual(frappe.db.get_value(EVENT_CFP, cfp.name, "status"), "Closed")


class TestFOSSEventCFPEditWindow(FrappeTestCase):
    """can_edit_proposal(): allow_cfp_edit is a standalone master switch (True
    always wins); when off, falls back to status == Live and not past deadline."""

    def tearDown(self):
        frappe.set_user("Administrator")

    # (allow_cfp_edit, status, deadline_days_from_now_or_None, expected)
    CASES: ClassVar = [
        (0, "Live", 3, True),  # off, live, before deadline -> open window
        (0, "Closed", 3, False),  # off, closed -> blocked
        (0, "Live", -1, False),  # off, past deadline -> blocked
        (0, "Live", None, True),  # off, no deadline set -> open window
        (1, "Live", -1, True),  # on overrides past deadline
        (1, "Closed", 3, True),  # on overrides closed status
    ]

    def test_can_edit_proposal_matrix(self):
        for allow_cfp_edit, status, deadline_days, expected in self.CASES:
            deadline = (
                add_to_date(now_datetime(), days=deadline_days)
                if deadline_days is not None
                else None
            )
            with self.subTest(
                allow_cfp_edit=allow_cfp_edit, status=status, deadline_days=deadline_days
            ):
                cfp = FOSSEventCFPFactory.create(
                    allow_cfp_edit=allow_cfp_edit, status=status, deadline=deadline
                )
                self.assertEqual(cfp.can_edit_proposal(), expected)
