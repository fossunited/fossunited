# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, EVENT, FREE_TICKET_CODE
from fossunited.tests.utils import insert_test_chapter, insert_test_event


class TestEventFreeTicketCodeController(FrappeTestCase):
    def setUp(self):
        self.fake = Faker()
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(
            chapter=self.chapter,
            is_paid_event=True,
            tickets_status="Live",
            tiers=[
                {
                    "enabled": 1,
                    "title": "Test",
                    "price": 100,
                    "maximum_tickets": 5,
                }
            ],
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.delete(FREE_TICKET_CODE, {"event": self.event.name})
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.commit()

    def _make_coupon_doc(self, **kwargs):
        data = {
            "doctype": FREE_TICKET_CODE,
            "event": self.event.name,
            "tier": "Volunteer",
            "max_count": 10,
            "mapped_email": self.fake.email(),
        }
        data.update(kwargs)
        return frappe.get_doc(data)

    def test_create_coupon_with_required_fields(self):
        coupon = self._make_coupon_doc()
        coupon.insert(ignore_permissions=True)

        # Exists in DB and normalized defaults applied
        self.assertTrue(frappe.db.exists(FREE_TICKET_CODE, coupon.name))
        coupon.reload()
        self.assertEqual(int(coupon.max_count), 10)
        # Controller normalizes used_count to 0 on insert
        self.assertEqual(int(coupon.used_count or 0), 0)
        self.assertEqual(int(coupon.is_used or 0), 0)

    def test_defaults_and_normalization(self):
        # Create without passing used_count/is_used explicitly
        coupon = self._make_coupon_doc()
        coupon.insert(ignore_permissions=True)
        coupon.reload()
        # After insert the before_insert/validate hooks should normalize
        self.assertEqual(int(coupon.used_count), 0)
        self.assertEqual(int(coupon.is_used), 0)

    def test_invalid_mapped_email_throws_error(self):
        coupon = self._make_coupon_doc(mapped_email="not-an-email")
        with self.assertRaises(frappe.ValidationError):
            coupon.insert(ignore_permissions=True)
