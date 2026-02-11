import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import EMAIL_GROUP, EMAIL_MEMBER, HACKATHON, USER_PROFILE
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_hackathon,
    insert_test_hackathon_localhost,
    insert_test_hackathon_participant,
    insert_user_profile,
)


class TestFOSSHackathonParticipant(FrappeTestCase):
    def setUp(self):
        self.LOCALHOST_ORGANIZER = "test3@example.com"
        self.PARTICIPANT_1 = "test4@example.com"
        self.PARTICIPANT_2 = "test2@example.com"
        self.localhost_org = insert_user_profile(self.LOCALHOST_ORGANIZER)
        frappe.get_doc("User", self.LOCALHOST_ORGANIZER).add_roles("Localhost Organizer")
        self.user1 = insert_user_profile(self.PARTICIPANT_1)
        self.user2 = insert_user_profile(self.PARTICIPANT_2)
        self.chapter = insert_test_chapter()
        self.hackathon = insert_test_hackathon(chapter=self.chapter.name)
        self.participant_1 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=self.PARTICIPANT_1,
            user=self.PARTICIPANT_1,
        )

        self.localhost = insert_test_hackathon_localhost(
            parent_hackathon=self.hackathon.name,
            organizers=[
                {
                    "profile": self.localhost_org,
                }
            ],
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        self.participant_1.delete(force=True)
        self.localhost.delete(force=True)
        self.hackathon.delete(force=True)
        self.chapter.delete(force=True)
        frappe.delete_doc(USER_PROFILE, self.localhost_org, force=True)
        frappe.delete_doc(USER_PROFILE, self.user1, force=True)
        frappe.delete_doc(USER_PROFILE, self.user2, force=True)
        for email in [self.LOCALHOST_ORGANIZER, self.PARTICIPANT_1, self.PARTICIPANT_2]:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True)

    def test_participant_creation(self):
        # Testing that website users have the permission to create Participant doctype
        frappe.set_user(self.PARTICIPANT_2)

        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=frappe.session.user,
            user=frappe.session.user,
        )

        participant.delete(force=True, ignore_permissions=True)

    def test_add_to_email_group(self):
        frappe.set_user(self.PARTICIPANT_2)

        # Given a hackathon
        # When a participant registers for this hackathon and subscribes for mailing
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=frappe.session.user,
            user=frappe.session.user,
            subscribe_chapter_mailing=1,
        )

        email_group_id = frappe.db.get_value(
            EMAIL_GROUP,
            {
                "document_type": HACKATHON,
                "reference_document": self.hackathon.name,
                "group_type": "Event Participants",
            },
            "name",
        )

        # Then that participant email should be added to an email group linked to the hackathon
        self.assertIsNotNone(
            frappe.db.exists(
                EMAIL_MEMBER,
                {
                    "email_group": email_group_id,
                    "email": frappe.session.user,
                },
            )
        )

        participant.delete(force=True, ignore_permissions=True)

    def test_localhost_rejection(self):
        frappe.set_user(self.PARTICIPANT_1)
        # Given a participant who wants to attend hackathon locally
        self.participant_1.wants_to_attend_locally = 1
        self.participant_1.localhost = self.localhost.name
        self.participant_1.save()

        self.assertEqual(self.participant_1.localhost_request_status, "Pending")

        # When the application is rejected by organizer
        frappe.set_user(self.LOCALHOST_ORGANIZER)
        self.participant_1.localhost_request_status = "Rejected"
        self.participant_1.save()

        # Then participant mode should be auto changed to removed
        self.assertFalse(self.participant_1.wants_to_attend_locally)

        # When the participant tries to apply for the same localhost again
        frappe.set_user(self.PARTICIPANT_1)
        self.participant_1.wants_to_attend_locally = 1
        self.participant_1.localhost = self.localhost.name

        self.assertEqual(self.participant_1.localhost_request_status, "Rejected")
        # Then a permission error should be thrown
        with self.assertRaises(frappe.PermissionError):
            self.participant_1.save()

    def test_remove_from_email_group_on_unsubscribe(self):
        frappe.set_user(self.PARTICIPANT_2)

        # Participant subscribes to email group
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=frappe.session.user,
            user=frappe.session.user,
            subscribe_chapter_mailing=1,
        )

        email_group_id = frappe.db.get_value(
            EMAIL_GROUP,
            {
                "document_type": HACKATHON,
                "reference_document": self.hackathon.name,
                "group_type": "Event Participants",
            },
            "name",
        )

        self.assertTrue(
            frappe.db.exists(
                EMAIL_MEMBER,
                {"email_group": email_group_id, "email": frappe.session.user},
            )
        )

        # Participant unsubscribes (update subscription flag)
        participant.subscribe_chapter_mailing = 0
        participant.save()

        # Ensure email is removed from the group
        self.assertFalse(
            frappe.db.exists(
                EMAIL_MEMBER,
                {"email_group": email_group_id, "email": frappe.session.user},
            )
        )

        participant.delete(force=True, ignore_permissions=True)

    def test_email_group_cleanup_on_participant_deletion(self):
        frappe.set_user(self.PARTICIPANT_2)

        # Step 1: Register with mailing subscription
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=frappe.session.user,
            user=frappe.session.user,
            subscribe_chapter_mailing=1,
        )

        email_group_id = frappe.db.get_value(
            EMAIL_GROUP,
            {
                "document_type": HACKATHON,
                "reference_document": self.hackathon.name,
                "group_type": "Event Participants",
            },
            "name",
        )

        self.assertTrue(
            frappe.db.exists(
                EMAIL_MEMBER,
                {"email_group": email_group_id, "email": frappe.session.user},
            )
        )

        participant.delete(force=True, ignore_permissions=True)
        self.assertFalse(
            frappe.db.exists(
                EMAIL_MEMBER,
                {"email_group": email_group_id, "email": frappe.session.user},
            )
        )

    def test_participant_has_permission(self):
        """Check for Participant has_permission as expected"""

        frappe.set_user(self.PARTICIPANT_1)
        self.participant_1.full_name = "Owner Edit"
        self.participant_1.save()  # should succeed

        # --- other user cannot edit ---
        frappe.set_user(self.PARTICIPANT_2)
        self.participant_1.full_name = "Hacker Edit"
        with self.assertRaises(frappe.PermissionError):
            self.participant_1.save()

        # --- organizer can edit ---
        frappe.set_user(self.LOCALHOST_ORGANIZER)
        self.participant_1.full_name = "Organizer Edit"
        self.participant_1.save()  # should succeed

        # --- guest cannot create ---
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            insert_test_hackathon_participant(
                hackathon_id=self.hackathon.name, email="guest@test.com"
            )

        # --- logged-in user can create ---
        frappe.set_user(self.PARTICIPANT_2)
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            email=frappe.session.user,
            user=frappe.session.user,
        )

        participant.delete(force=True, ignore_permissions=True)
