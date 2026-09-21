import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.api.tickets import change_transfer_status, get_transfer_details
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET, TICKET_TRANSFER
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventTicketFactory,
    FOSSEventTicketTransferFactory,
)

fake = Faker()


class TestFOSSEventTicketTransfer(FrappeTestCase):
    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_ticket_transfer(self):
        owner_email = fake.email()
        receiver_email = fake.email()
        receiver_name = fake.name()

        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=owner_email)
        transfer = FOSSEventTicketTransferFactory.create(
            ticket=ticket.name,
            receiver_email=receiver_email,
            receiver_name=receiver_name,
        )
        self.assertEqual(transfer.status, "Pending Approval")

        transfer.status = "Completed"
        transfer.save()

        self.assertFalse(
            frappe.db.exists(EVENT_TICKET, {"email": owner_email, "event": self.event.name})
        )
        self.assertTrue(
            frappe.db.exists(
                EVENT_TICKET,
                {"email": receiver_email, "full_name": receiver_name, "event": self.event.name},
            )
        )

    def test_status_pending_on_create(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        with self.assertRaises(frappe.exceptions.ValidationError):
            frappe.get_doc(
                {
                    "doctype": TICKET_TRANSFER,
                    "ticket": ticket.name,
                    "receiver_name": fake.name(),
                    "receiver_email": fake.email(),
                    "status": "Completed",
                }
            ).insert()

    def test_transfer_already_transferred_ticket(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=fake.email())

        transfer_1 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)
        transfer_1.status = "Completed"
        transfer_1.save()
        ticket.reload()
        self.assertTrue(ticket.has_value_changed("is_transfer_ticket"))

        transfer_2 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)
        transfer_2.status = "Completed"
        transfer_2.save()
        ticket.reload()
        self.assertTrue(ticket.has_value_changed("is_transfer_ticket"))

    def test_receiver_cannot_approve(self):
        receiver_email = fake.email()
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        transfer = FOSSEventTicketTransferFactory.create(
            ticket=ticket.name, receiver_email=receiver_email
        )

        frappe.set_user(receiver_email)
        transfer.status = "Completed"
        with self.assertRaises(frappe.PermissionError):
            transfer.save(ignore_permissions=True)

    def test_stranger_cannot_change_status(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        transfer = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user(fake.email())
        transfer.status = "Completed"
        with self.assertRaises(frappe.PermissionError):
            transfer.save(ignore_permissions=True)

    def test_owner_can_approve(self):
        owner_email = fake.email()
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=owner_email)
        transfer = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user(owner_email)
        transfer.status = "Completed"
        transfer.save(ignore_permissions=True)
        self.assertEqual(transfer.status, "Completed")

    def test_free_pass_ticket_cannot_transfer(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name, tier="Free Pass")
        with self.assertRaises(frappe.ValidationError):
            FOSSEventTicketTransferFactory.create(ticket=ticket.name)

    def test_non_live_event_ticket_cannot_transfer(self):
        closed_event = FOSSChapterEventFactory.create(
            "with_paid_tickets", chapter=self.chapter.name, status="Concluded"
        )
        ticket = FOSSEventTicketFactory.create(event=closed_event.name)
        with self.assertRaises(frappe.ValidationError):
            FOSSEventTicketTransferFactory.create(ticket=ticket.name)

    def test_transfer_updates_all_ticket_fields(self):
        ticket = FOSSEventTicketFactory.create(
            event=self.event.name, wants_tshirt=1, tshirt_size="M"
        )
        transfer = FOSSEventTicketTransferFactory.create(
            ticket=ticket.name,
            receiver_name=fake.name(),
            receiver_email=fake.email(),
            designation="Engineer",
            organization="FOSS United",
            wants_tshirt=1,
            tshirt_size="XL",
        )
        transfer.status = "Completed"
        transfer.save()

        ticket.reload()
        self.assertEqual(ticket.full_name, transfer.receiver_name)
        self.assertEqual(ticket.email, transfer.receiver_email)
        self.assertEqual(ticket.designation, "Engineer")
        self.assertEqual(ticket.organization, "FOSS United")
        self.assertEqual(ticket.wants_tshirt, 1)
        self.assertEqual(ticket.tshirt_size, "XL")
        self.assertTrue(ticket.is_transfer_ticket)

    def test_owner_and_receiver_can_cancel(self):
        owner_email = fake.email()
        receiver_email = fake.email()
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=owner_email)

        for user_email in [owner_email, receiver_email]:
            transfer = FOSSEventTicketTransferFactory.create(
                ticket=ticket.name, receiver_email=receiver_email
            )
            frappe.set_user(user_email)
            transfer.status = "Cancelled"
            transfer.save(ignore_permissions=True)
            self.assertEqual(transfer.status, "Cancelled")
            frappe.set_user("Administrator")

    def test_owner_email_case_insensitive(self):
        """A ticket's email is saved verbatim (no normalization), but Frappe
        account emails/session users are lowercase - the permission check
        must compare case-insensitively or a legitimate owner gets locked
        out of their own transfer."""
        owner_email = "MixedCase.Owner@Example.com"
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=owner_email)
        transfer = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user(owner_email.lower())
        transfer.status = "Completed"
        transfer.save(ignore_permissions=True)
        frappe.set_user("Administrator")

        self.assertEqual(transfer.status, "Completed")


class TestChangeTransferStatusAPI(FrappeTestCase):
    """
    End-to-end tests for fossunited.api.tickets.change_transfer_status -
    the actual endpoint the ticket-transfer email links and dashboard hit.

    Two independent ways to prove you're allowed to act on a transfer:
      1. The single-use `token` from the emailed link (no login needed).
      2. Being logged in as the ticket owner (approve) or owner/receiver
         (reject) - the pre-token fallback, kept for links already sent.

    An attacker with neither a valid token nor a matching login must always
    be rejected, regardless of which transfer or ticket they target.
    """

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def _make_transfer(self, owner_email=None, receiver_email=None):
        ticket = FOSSEventTicketFactory.create(
            event=self.event.name, email=owner_email or fake.email()
        )
        return FOSSEventTicketTransferFactory.create(
            ticket=ticket.name, receiver_email=receiver_email or fake.email()
        )

    # -- valid token: works with no login, regardless of who's logged in ----

    def test_valid_token_approves_without_login(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        result = change_transfer_status(
            transfer_id=transfer.name, status="Completed", token=transfer.approval_token
        )
        frappe.set_user("Administrator")

        self.assertTrue(result)
        transfer.reload()
        self.assertEqual(transfer.status, "Completed")

    def test_valid_token_rejects_without_login(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        change_transfer_status(
            transfer_id=transfer.name, status="Cancelled", token=transfer.approval_token
        )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Cancelled")

    def test_valid_token_works_even_if_logged_in_as_a_stranger(self):
        """The token alone is sufficient proof - session identity shouldn't
        matter once the token checks out."""
        transfer = self._make_transfer()

        frappe.set_user(fake.email())
        change_transfer_status(
            transfer_id=transfer.name, status="Completed", token=transfer.approval_token
        )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Completed")

    # -- no valid token: attacker must always be blocked ---------------------

    def test_no_token_guest_is_blocked(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    def test_wrong_token_guest_is_blocked(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            change_transfer_status(
                transfer_id=transfer.name, status="Completed", token="not-the-real-token"
            )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    def test_wrong_token_and_stranger_login_is_blocked(self):
        transfer = self._make_transfer()

        frappe.set_user(fake.email())
        with self.assertRaises(frappe.PermissionError):
            change_transfer_status(
                transfer_id=transfer.name, status="Completed", token="not-the-real-token"
            )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    def test_token_from_a_different_transfer_is_rejected(self):
        """A valid token for someone else's transfer must not work here -
        tokens are checked against the specific doc being acted on."""
        transfer_1 = self._make_transfer()
        transfer_2 = self._make_transfer()

        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            change_transfer_status(
                transfer_id=transfer_1.name, status="Completed", token=transfer_2.approval_token
            )
        frappe.set_user("Administrator")

        transfer_1.reload()
        self.assertEqual(transfer_1.status, "Pending Approval")

    def test_slightly_altered_token_is_rejected(self):
        """Tokens are matched exactly (case-sensitive) - unlike emails."""
        transfer = self._make_transfer()
        tampered_token = transfer.approval_token.upper()
        self.assertNotEqual(tampered_token, transfer.approval_token)

        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            change_transfer_status(
                transfer_id=transfer.name, status="Completed", token=tampered_token
            )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    # -- session-login fallback: pre-token links still work ------------------

    def test_owner_login_without_token_approves(self):
        owner_email = fake.email()
        transfer = self._make_transfer(owner_email=owner_email)

        frappe.set_user(owner_email)
        change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Completed")

    def test_owner_login_case_insensitive(self):
        owner_email = "MixedCase.Owner@Example.com"
        transfer = self._make_transfer(owner_email=owner_email)

        frappe.set_user(owner_email.lower())
        change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Completed")

    def test_receiver_login_without_token_can_reject(self):
        receiver_email = fake.email()
        transfer = self._make_transfer(receiver_email=receiver_email)

        frappe.set_user(receiver_email)
        change_transfer_status(transfer_id=transfer.name, status="Cancelled", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Cancelled")

    def test_receiver_login_without_token_cannot_approve(self):
        receiver_email = fake.email()
        transfer = self._make_transfer(receiver_email=receiver_email)

        frappe.set_user(receiver_email)
        with self.assertRaises(frappe.PermissionError):
            change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    def test_stranger_login_without_token_is_blocked(self):
        transfer = self._make_transfer()

        frappe.set_user(fake.email())
        with self.assertRaises(frappe.PermissionError):
            change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    # -- invalid status / bad transfer id -------------------------------------

    def test_invalid_status_value_rejected(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        with self.assertRaises(frappe.ValidationError):
            change_transfer_status(
                transfer_id=transfer.name, status="Bogus", token=transfer.approval_token
            )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Pending Approval")

    def test_unknown_transfer_id_raises_not_found(self):
        frappe.set_user("Guest")
        with self.assertRaises(frappe.DoesNotExistError):
            change_transfer_status(
                transfer_id="does-not-exist", status="Completed", token="whatever"
            )
        frappe.set_user("Administrator")

    # -- get_transfer_details must never leak the token -----------------------

    def test_get_transfer_details_never_returns_token(self):
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        details = get_transfer_details(id=transfer.name)
        frappe.set_user("Administrator")

        self.assertIsNotNone(details)
        self.assertNotIn("approval_token", details)
