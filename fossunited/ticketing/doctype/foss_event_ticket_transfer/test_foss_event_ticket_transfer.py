import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase
from frappe.utils import set_request

from fossunited.api.tickets import (
    change_transfer_status,
    create_transfer_request,
    get_ticket_details,
    get_transfer_details,
)
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


class TestChangeTransferStatusAPI(FrappeTestCase):
    """
    End-to-end tests for fossunited.api.tickets.change_transfer_status /
    get_transfer_details - the actual endpoints the ticket-transfer email
    links and dashboard hit.

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

    # -- valid token: works with no login ------------------------------------

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

    def test_system_manager_can_approve_and_reject_regardless_of_email(self):
        """System Manager bypasses the owner/receiver/token check entirely -
        for support staff fixing a stuck transfer via Desk."""
        transfer = self._make_transfer()
        # Administrator (the default test user) carries System Manager.
        change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        transfer.reload()
        self.assertEqual(transfer.status, "Completed")

        transfer_2 = self._make_transfer()
        change_transfer_status(transfer_id=transfer_2.name, status="Cancelled", token=None)
        transfer_2.reload()
        self.assertEqual(transfer_2.status, "Cancelled")

    # -- get_transfer_details: PII requires the same proof as an action -----

    def test_get_transfer_details_hides_pii_without_authorization(self):
        """A bare transfer id isn't enough to see who's involved - it's more
        easily leaked (URLs in logs/referrers) than the token, so it alone
        must not reveal owner/receiver names or emails."""
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        details = get_transfer_details(id=transfer.name)
        frappe.set_user("Administrator")

        self.assertIsNotNone(details)
        self.assertNotIn("approval_token", details)
        self.assertFalse(details.get("owner_email"))
        self.assertFalse(details.get("receiver_email"))

    def test_get_transfer_details_reveals_pii_when_authorized(self):
        """Either the correct token or a matching owner session unlocks the
        PII fields - proven both ways since they're separate code paths."""
        owner_email = fake.email()
        transfer = self._make_transfer(owner_email=owner_email)

        frappe.set_user("Guest")
        details = get_transfer_details(id=transfer.name, token=transfer.approval_token)
        self.assertEqual(details.get("owner_email"), transfer.owner_email)
        self.assertEqual(details.get("receiver_email"), transfer.receiver_email)

        frappe.set_user(owner_email)
        details = get_transfer_details(id=transfer.name)
        frappe.set_user("Administrator")
        self.assertEqual(details.get("owner_email"), transfer.owner_email)

    # -- auto-closing stale sibling transfers for the same ticket ------------

    def test_completing_a_transfer_cancels_other_pending_ones_for_same_ticket(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        transfer_1 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)
        transfer_2 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user("Guest")
        change_transfer_status(
            transfer_id=transfer_1.name, status="Completed", token=transfer_1.approval_token
        )
        frappe.set_user("Administrator")

        transfer_1.reload()
        transfer_2.reload()
        self.assertEqual(transfer_1.status, "Completed")
        self.assertEqual(transfer_2.status, "Cancelled")

    def test_rejecting_a_transfer_does_not_affect_other_pending_ones(self):
        """Rejecting one request is unrelated to the ticket's ownership -
        other pending requests for it are still perfectly valid."""
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        transfer_1 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)
        transfer_2 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user("Guest")
        change_transfer_status(
            transfer_id=transfer_1.name, status="Cancelled", token=transfer_1.approval_token
        )
        frappe.set_user("Administrator")

        transfer_1.reload()
        transfer_2.reload()
        self.assertEqual(transfer_1.status, "Cancelled")
        self.assertEqual(transfer_2.status, "Pending Approval")

    def test_stale_sibling_cannot_be_resurrected_by_the_old_owner(self):
        """The actual bug this closes: without both the auto-cancel and the
        previous-status guard, the original owner's still-matching
        owner_email (or their still-valid token) could resurrect an old,
        auto-cancelled transfer and hijack the ticket back after it had
        already been legitimately transferred to someone else."""
        owner_email = fake.email()
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=owner_email)
        transfer_1 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)
        transfer_2 = FOSSEventTicketTransferFactory.create(ticket=ticket.name)

        frappe.set_user("Guest")
        change_transfer_status(
            transfer_id=transfer_1.name, status="Completed", token=transfer_1.approval_token
        )
        frappe.set_user("Administrator")

        transfer_2.reload()
        self.assertEqual(transfer_2.status, "Cancelled")

        # Neither the original owner's login nor their still-technically-valid
        # token can revive the now-cancelled sibling.
        frappe.set_user(owner_email)
        with self.assertRaises(frappe.ValidationError):
            change_transfer_status(transfer_id=transfer_2.name, status="Completed", token=None)
        frappe.set_user("Guest")
        with self.assertRaises(frappe.ValidationError):
            change_transfer_status(
                transfer_id=transfer_2.name, status="Completed", token=transfer_2.approval_token
            )
        frappe.set_user("Administrator")

        transfer_2.reload()
        self.assertEqual(transfer_2.status, "Cancelled")
        ticket.reload()
        self.assertEqual(ticket.email, transfer_1.receiver_email)

    def test_resolved_transfer_cannot_be_flipped_again(self):
        """Not just siblings - a transfer that resolved normally (no other
        pending requests involved) is also final."""
        transfer = self._make_transfer()

        frappe.set_user("Guest")
        change_transfer_status(
            transfer_id=transfer.name, status="Cancelled", token=transfer.approval_token
        )

        with self.assertRaises(frappe.ValidationError):
            change_transfer_status(
                transfer_id=transfer.name, status="Completed", token=transfer.approval_token
            )
        frappe.set_user("Administrator")

        transfer.reload()
        self.assertEqual(transfer.status, "Cancelled")

    def test_system_manager_can_still_flip_a_resolved_transfer(self):
        """The previous-status guard has the same System Manager escape
        hatch as the permission check, for support fixing a mistake."""
        transfer = self._make_transfer()
        change_transfer_status(transfer_id=transfer.name, status="Cancelled", token=None)

        change_transfer_status(transfer_id=transfer.name, status="Completed", token=None)
        transfer.reload()
        self.assertEqual(transfer.status, "Completed")


class TestChangeTransferStatusRateLimit(FrappeTestCase):
    """
    change_transfer_status is rate-limited to 3 attempts / 12h per IP - the
    actual defense against someone hammering a known transfer_id trying
    tokens (the token itself is 128 bits of entropy, already infeasible to
    brute-force; the limit guards against cheaper abuse/spam instead).

    The @rate_limit decorator only activates inside a real request context
    (it no-ops when frappe.request is falsy, which is the default in unit
    tests) - frappe.utils.set_request() fakes one so this can be exercised
    for real instead of just trusting the decorator is wired up.
    """

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

        set_request(
            method="POST", path="/api/method/fossunited.api.tickets.change_transfer_status"
        )
        frappe.local.request_ip = "192.0.2.42"
        frappe.form_dict.cmd = "fossunited.api.tickets.change_transfer_status"
        self._cache_key = frappe.cache.make_key(
            f"rl:{frappe.form_dict.cmd}:{frappe.local.request_ip}"
        )
        frappe.cache.delete(self._cache_key)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.cache.delete(self._cache_key)
        if hasattr(frappe.local, "request"):
            delattr(frappe.local, "request")
        frappe.local.request_ip = None
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def _make_transfer(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        return FOSSEventTicketTransferFactory.create(ticket=ticket.name)

    def test_blocked_after_limit_reached_even_with_wrong_tokens(self):
        """The first 3 attempts fail normally on the token check (401); the
        4th is rejected purely for volume (429) before the token is even
        looked at - so guessing can never outlast the limit."""
        # Create fixtures as Administrator first: FOSS Event Ticket only
        # grants create to System Manager, so this must happen before we
        # impersonate Guest below.
        transfers = [self._make_transfer() for _ in range(4)]

        frappe.set_user("Guest")

        for transfer in transfers[:3]:
            with self.assertRaises(frappe.AuthenticationError):
                change_transfer_status(
                    transfer_id=transfer.name, status="Completed", token="wrong-guess"
                )

        with self.assertRaises(frappe.RateLimitExceededError):
            change_transfer_status(
                transfer_id=transfers[3].name, status="Completed", token="wrong-guess"
            )

        frappe.set_user("Administrator")


class TestCreateTransferRequestAndTicketDetailsAPI(FrappeTestCase):
    """
    Covers the first step of the flow - fossunited.api.tickets.get_ticket_details
    (the guest-facing lookup on the transfer form) and create_transfer_request
    (submitting the request) - so the whole flow, not just approve/reject, is
    exercised through its real entry points rather than only via factories.
    """

    def setUp(self):
        self.chapter = FOSSChapterFactory.create()
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_get_ticket_details_returns_safe_fields_only(self):
        """Deliberately excludes `email` - the lookup form has no reason to
        expose the current owner's address to whoever's typing in a ticket
        id, and a future edit adding fields here shouldn't reintroduce it
        without someone noticing."""
        ticket = FOSSEventTicketFactory.create(event=self.event.name)

        frappe.set_user("Guest")
        details = get_ticket_details(ticket_id=ticket.name)
        frappe.set_user("Administrator")

        self.assertEqual(details.get("name"), ticket.name)
        self.assertEqual(details.get("tier"), ticket.tier)
        self.assertNotIn("email", details)

    def test_get_ticket_details_unknown_id_returns_none(self):
        frappe.set_user("Guest")
        details = get_ticket_details(ticket_id="does-not-exist")
        frappe.set_user("Administrator")

        self.assertIsNone(details)

    def test_guest_can_create_transfer_request(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        receiver_email = fake.email()

        frappe.set_user("Guest")
        result = create_transfer_request(
            ticket=ticket.name,
            receiver_details={"receiver_name": fake.name(), "receiver_email": receiver_email},
        )
        frappe.set_user("Administrator")

        self.assertEqual(result.get("status"), "Pending Approval")
        transfer = frappe.get_doc(TICKET_TRANSFER, result["name"])
        self.assertEqual(transfer.ticket, ticket.name)
        self.assertEqual(transfer.receiver_email, receiver_email)
        self.assertEqual(transfer.owner_email, ticket.email)

    def test_create_transfer_request_generates_a_token_but_never_returns_it(self):
        ticket = FOSSEventTicketFactory.create(event=self.event.name)

        frappe.set_user("Guest")
        result = create_transfer_request(
            ticket=ticket.name,
            receiver_details={"receiver_name": fake.name(), "receiver_email": fake.email()},
        )
        frappe.set_user("Administrator")

        self.assertNotIn("approval_token", result)
        token = frappe.db.get_value(TICKET_TRANSFER, result["name"], "approval_token")
        self.assertTrue(token)

    def test_create_transfer_request_for_unknown_ticket_raises_not_found(self):
        frappe.set_user("Guest")
        with self.assertRaises(frappe.DoesNotExistError):
            create_transfer_request(
                ticket="does-not-exist",
                receiver_details={"receiver_name": fake.name(), "receiver_email": fake.email()},
            )
        frappe.set_user("Administrator")
