import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.checkins import checkin_attendee
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventTicketFactory,
    UserFactory,
)


class TestFOSSEventTicket(FrappeTestCase):
    def setUp(self):
        self.team_member_user = UserFactory.create("with_foss_website_user_role")
        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.team_member_user.name]
        )
        self.event = FOSSChapterEventFactory.create("with_paid_tickets", chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def test_checkin(self):
        # Given that a ticket is created for an event
        ticket = FOSSEventTicketFactory.create(event=self.event.name)

        # There should be no check-ins for that event
        self.assertFalse(ticket.check_ins)

        # Set the user as a chapter member
        frappe.set_user(self.team_member_user.name)

        # When the user checks in the attendee
        checkin_attendee(self.event.name, ticket.as_dict())

        # Then the check-in data should be saved
        ticket.reload()
        self.assertTrue(ticket.check_ins)

        # When the user tries to check-in the attendee again on the same day
        # Then the user should not be able to check-in the attendee again
        with self.assertRaises(frappe.ValidationError):
            checkin_attendee(self.event.name, ticket.as_dict())

    def test_checkin_as_non_chapter_member(self):
        # Given that a ticket is created for an event
        ticket = FOSSEventTicketFactory.create(event=self.event.name)

        self.assertFalse(ticket.check_ins)

        # Set the user as a non-member
        non_member = UserFactory.create()
        frappe.set_user(non_member.name)

        # When the user checks in the attendee
        # Then the user should not have permission to check-in the attendee
        with self.assertRaises(frappe.PermissionError):
            checkin_attendee(self.event.name, ticket.as_dict())

    def test_create_when_tickets_closed(self):
        # Given a paid event with ticket status as "Closed"
        self.event.tickets_status = "Closed"
        self.event.save()
        # When a ticket is created for this event
        # Then an error must be thrown
        with self.assertRaises(frappe.PermissionError):
            FOSSEventTicketFactory.create(event=self.event.name)

    def test_ticket_creation(self):
        # Given an event
        # When the tickets_status is Live
        self.event.tickets_status = "Live"
        self.event.save()

        # Then a ticket for this event should be created without any problem
        ticket = FOSSEventTicketFactory.create(event=self.event.name)
        ticket.delete(force=True)

    def test_ticket_tier_closing(self):
        # Given an event with a ticket tier
        tier = self.event.tiers[0]

        # Make sure this tier is enabled
        self.assertTrue(tier.enabled)

        # make sure there are 0 tickets of this tier to start with
        self.assertEqual(
            frappe.db.count(
                EVENT_TICKET,
                {
                    "event": self.event.name,
                    "tier": tier.title,
                },
            ),
            0,
        )

        # When maximum number of tickets are created of this tier type
        tickets = []
        for _ in range(tier.maximum_tickets):
            ticket = FOSSEventTicketFactory.create(
                event=self.event.name,
                tier=tier.title,
            )
            tickets.append(ticket)

        self.event.reload()

        # Then the tier should be disabled
        tier = self.event.tiers[0]
        self.assertEqual(tier.enabled, 0)

        for ticket in tickets:
            ticket.delete(force=1)

    def test_add_to_email_group(self):
        # Given an Event with tickets "Live"
        self.event.tickets_status = "Live"
        self.event.save()

        attendee_email = "test4@example.com"
        # When a ticket is created with attendee's email
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=attendee_email)
        ticket.subscribe_chapter_mailing = 1
        ticket.save()
        # Then the email should be added to an email group linked to event for participants
        email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.event.name,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": email_group},
            )
        )
        ticket.delete(force=True)

    def test_remove_from_email_group_on_unsubscribe(self):
        attendee_email = "test4@example.com"

        # Given: Ticket created with subscription ON
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=attendee_email)
        ticket.subscribe_chapter_mailing = 1
        ticket.save()

        email_group_id = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.event.name,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
            "name",
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": email_group_id},
            )
        )

        # Verify initial membership in Chapter Event Participants group
        chapter_group_id = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.chapter.name,
                "document_type": CHAPTER,
                "group_type": "Chapter Event Participants",
            },
            "name",
        )
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": chapter_group_id},
            )
        )

        # When: Ticket is updated to unsubscribe
        ticket.subscribe_chapter_mailing = 0
        ticket.save()

        # Then: Email should be removed from email group
        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": email_group_id},
            )
        )

        # Also verify removal from Chapter Event Participants group
        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": chapter_group_id},
            )
        )

        ticket.delete(force=True)

    def test_resub_from_email_group(self):
        attendee_email = "test4@example.com"

        # Insert with default subscription
        ticket = FOSSEventTicketFactory.create(event=self.event.name, email=attendee_email)

        ticket.subscribe_chapter_mailing = 0
        ticket.handle_add_to_email_group()
        ticket.save()

        email_group_id = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.event.name,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
            "name",
        )

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": email_group_id},
            )
        )
        ticket.subscribe_chapter_mailing = 1
        ticket.save()
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {"email": attendee_email, "email_group": email_group_id},
            )
        )

        ticket.delete(force=True)
