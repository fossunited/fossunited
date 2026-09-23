import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.tickets import (
    get_ticket_qr,
    search_tickets,
)
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET, FREE_TICKET_CODE
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_coupon,
    insert_test_coupon_application,
    insert_test_event,
    insert_test_ticket,
    insert_user_profile,
)


class TestTicketAPI(FrappeTestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(self.chapter, is_paid_event=1, tickets_status="Live")
        self.ticket = insert_test_ticket(self.event.name)
        self.coupon = insert_test_coupon(self.event.name)

    def tearDown(self):
        """Clean up test data after each test"""
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT_TICKET, self.ticket.name, force=True)
        frappe.delete_doc(FREE_TICKET_CODE, self.coupon.name, force=True)
        frappe.db.rollback()

    def test_search_tickets_with_empty_term(self):
        """Should throw error for empty search term"""
        with self.assertRaises(frappe.exceptions.ValidationError):
            search_tickets("")

    def test_search_tickets_with_none_term(self):
        """Should throw error for None search term"""
        with self.assertRaises(frappe.exceptions.ValidationError):
            search_tickets(None)

    def test_search_tickets_by_ticket_id(self):
        """Should return ticket when searching by valid ticket_id"""
        result = search_tickets(self.ticket.name)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], self.ticket.name)

    def test_search_tickets_by_invalid_ticket_id(self):
        """Should return empty list for non-existent ticket_id"""
        result = search_tickets("INVALID_TICKET_ID_123")

        self.assertEqual(result, [])

    def test_search_tickets_by_coupon_without_applications(self):
        """Should return empty list when coupon has no applications"""
        result = search_tickets(self.coupon.name)

        self.assertEqual(result, [])

    def test_search_tickets_by_coupon_with_applications(self):
        """Should return tickets for users who applied with coupon"""
        # Create tickets and coupon applications
        insert_test_coupon_application(self.coupon.name, self.event.name)
        insert_test_coupon_application(self.coupon.name, self.event.name)

        result = search_tickets(self.coupon.name)
        self.assertEqual(len(result), 2)

    def test_search_returns_only_allowed_fields(self):
        """Should only return specified fields in search results"""
        insert_test_ticket(self.event.name)
        insert_test_coupon_application(self.coupon.name, self.event.name)

        result = search_tickets(self.coupon.name)

        allowed_fields = {"name", "full_name", "email", "tier", "organization"}
        for ticket_data in result:
            self.assertTrue(set(ticket_data.keys()).issubset(allowed_fields))


class TestTicketQrAuth(FrappeTestCase):
    """get_ticket_qr must only be reachable by the ticket's email match or its creator."""

    def setUp(self):
        frappe.set_user("Administrator")
        self.buyer = "test_ticket_buyer@example.com"
        self.stranger = "test_ticket_stranger@example.com"
        insert_user_profile(self.buyer)
        insert_user_profile(self.stranger)

        self.chapter = insert_test_chapter()
        self.event = insert_test_event(self.chapter, is_paid_event=1, tickets_status="Live")

        # email match: created by Administrator, but the email field is the buyer's
        self.email_match_ticket = insert_test_ticket(self.event.name, email=self.buyer)

        # owner match: created while logged in as the buyer, email is unrelated.
        # ignore_permissions=True since a plain user has no create perm on the
        # doctype (real ticket creation always goes through ignore_permissions);
        # owner is still set from the active session user regardless.
        frappe.set_user(self.buyer)
        self.owner_match_ticket = insert_test_ticket(
            self.event.name, email="someone-else@example.com", ignore_permissions=True
        )
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT_TICKET, self.email_match_ticket.name, force=True)
        frappe.delete_doc(EVENT_TICKET, self.owner_match_ticket.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.db.delete("User", {"name": ["in", [self.buyer, self.stranger]]})
        frappe.db.rollback()

    def test_email_match_can_fetch_qr(self):
        """Session user matching ticket.email (but not its creator) is allowed"""
        frappe.set_user(self.buyer)
        response = get_ticket_qr(self.email_match_ticket.name)
        self.assertEqual(response.mimetype, "image/svg+xml")

    def test_owner_match_can_fetch_qr(self):
        """Session user matching ticket.owner (but not its email) is allowed"""
        frappe.set_user(self.buyer)
        response = get_ticket_qr(self.owner_match_ticket.name)
        self.assertEqual(response.mimetype, "image/svg+xml")

    def test_stranger_is_denied(self):
        """Session user matching neither email nor owner is denied"""
        frappe.set_user(self.stranger)
        with self.assertRaises(frappe.PermissionError):
            get_ticket_qr(self.email_match_ticket.name)

    def test_nonexistent_ticket_denied_same_as_stranger(self):
        """A made-up ticket_id must fail the same way as a real ticket owned by someone else"""
        frappe.set_user(self.stranger)
        with self.assertRaises(frappe.PermissionError):
            get_ticket_qr("NON_EXISTENT_TICKET_ID")
