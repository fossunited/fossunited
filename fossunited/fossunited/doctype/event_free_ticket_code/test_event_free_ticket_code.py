# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import CHAPTER, EVENT, FREE_TICKET_CODE
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FreeTicketCodeFactory,
)

fake = Faker()


class TestEventFreeTicketCodeController(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.delete(FREE_TICKET_CODE, {"event": self.event.name})
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.commit()  # nosemgrep: frappe-manual-commit — tearDown needs commit to flush deletes before next test

    def test_create_coupon_with_required_fields(self):
        coupon = FreeTicketCodeFactory.create(event=self.event.name)

        # Exists in DB and normalized defaults applied
        self.assertTrue(frappe.db.exists(FREE_TICKET_CODE, coupon.name))
        coupon.reload()
        self.assertEqual(int(coupon.max_count), 10)
        # Controller normalizes used_count to 0 on insert
        self.assertEqual(int(coupon.used_count or 0), 0)
        self.assertEqual(int(coupon.is_used or 0), 0)

    def test_defaults_and_normalization(self):
        # Create without passing used_count/is_used explicitly
        coupon = FreeTicketCodeFactory.create(event=self.event.name)
        coupon.reload()
        # After insert the before_insert/validate hooks should normalize
        self.assertEqual(int(coupon.used_count), 0)
        self.assertEqual(int(coupon.is_used), 0)

    def test_invalid_mapped_email_throws_error(self):
        with self.assertRaises(frappe.ValidationError):
            FreeTicketCodeFactory.create(event=self.event.name, mapped_email="not-an-email")
