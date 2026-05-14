import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

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
