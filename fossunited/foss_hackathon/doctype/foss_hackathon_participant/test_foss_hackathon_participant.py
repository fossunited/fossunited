import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    EMAIL_GROUP,
    EMAIL_MEMBER,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
)
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_hackathon,
    insert_test_hackathon_localhost,
)


class TestFOSSHackathonParticipant(FrappeTestCase):
    def setUp(self):
        """Set up test data"""
        frappe.set_user("Administrator")

        # Test users
        self.PARTICIPANT_EMAIL = "participant@example.com"
        self.ORGANIZER_EMAIL = "organizer@example.com"

        # Create test chapter and hackathon
        self.chapter = insert_test_chapter()
        self.hackathon = insert_test_hackathon(chapter=self.chapter.name)
        self.localhost = insert_test_hackathon_localhost(parent_hackathon=self.hackathon.name)

    def tearDown(self):
        """Clean up test data"""
        frappe.set_user("Administrator")
        # Delete in reverse order to avoid FK constraints
        frappe.db.delete(HACKATHON_PARTICIPANT, {"hackathon": self.hackathon.name})
        frappe.db.delete(EMAIL_MEMBER, {"email": self.PARTICIPANT_EMAIL})
        frappe.db.delete(EMAIL_MEMBER, {"email": "participant1@example.com"})
        frappe.db.delete(EMAIL_MEMBER, {"email": "participant2@example.com"})
        frappe.db.delete(EMAIL_GROUP, {"chapter": self.chapter.name})
        self.localhost.delete(force=True)
        self.hackathon.delete(force=True)
        self.chapter.delete(force=True)

    def test_status_based_email_group_sync(self):
        """
        Comprehensive test for status-based email group synchronization.
        Tests all status transitions and verifies email group membership.
        """
        # Create participant with localhost
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
                "subscribe_chapter_mailing": 1,
            }
        )
        participant.insert()

        # Test 1: Initial status should be "Pending"
        self.assertEqual(participant.localhost_request_status, "Pending")
        self._assert_in_group("Pending", participant.email)
        self._assert_not_in_groups(
            ["Pending Confirmation", "Accepted", "Rejected"], participant.email
        )

        # Test 2: Change to "Pending Confirmation"
        participant.localhost_request_status = "Pending Confirmation"
        participant.save()
        self._assert_in_group("Pending Confirmation", participant.email)
        self._assert_not_in_groups(["Pending", "Accepted", "Rejected"], participant.email)

        # Test 3: Change to "Accepted"
        participant.localhost_request_status = "Accepted"
        participant.save()
        self._assert_in_group("Accepted", participant.email)
        self._assert_not_in_groups(
            ["Pending", "Pending Confirmation", "Rejected"], participant.email
        )

        # Test 4: Change to "Rejected"
        participant.localhost_request_status = "Rejected"
        participant.save()
        self._assert_in_group("Rejected", participant.email)
        self._assert_not_in_groups(
            ["Pending", "Pending Confirmation", "Accepted"], participant.email
        )

        # Test 5: Back to "Pending" (edge case)
        participant.localhost_request_status = "Pending"
        participant.save()
        self._assert_in_group("Pending", participant.email)
        self._assert_not_in_groups(
            ["Pending Confirmation", "Accepted", "Rejected"], participant.email
        )

        # Test 6: Delete participant - should remove from all groups
        participant.delete()
        self._assert_not_in_groups(
            ["Pending", "Pending Confirmation", "Accepted", "Rejected"],
            self.PARTICIPANT_EMAIL,
        )

    def test_localhost_change_resets_status(self):
        """Test that changing localhost resets status to Pending and removes from old groups"""
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
                "subscribe_chapter_mailing": 1,
            }
        )
        participant.insert()

        # Change to Accepted status
        participant.localhost_request_status = "Accepted"
        participant.save()

        # Verify in Accepted group of localhost1
        self._assert_in_group("Accepted", participant.email, self.localhost.name)

        # Create another localhost and switch
        localhost2 = insert_test_hackathon_localhost(parent_hackathon=self.hackathon.name)

        participant.localhost = localhost2.name
        participant.save()

        # Should reset to Pending
        self.assertEqual(participant.localhost_request_status, "Pending")

        # Should be in Pending group of new localhost
        pending_group_name = self._get_group_name("Pending", localhost2.name)
        self.assertTrue(
            self._is_member_of_group(pending_group_name, participant.email),
            "Participant should be in Pending group of new localhost",
        )

        # Should NOT be in any groups of old localhost
        old_accepted_group = self._get_group_name("Accepted", self.localhost.name)
        if old_accepted_group:
            self.assertFalse(
                self._is_member_of_group(old_accepted_group, participant.email),
                "Participant should be removed from old localhost groups",
            )

        participant.delete()
        localhost2.delete(force=True)

    def test_chapter_subscription_preference(self):
        """Test that chapter subscription is respected"""
        # Test 1: With chapter subscription
        participant1 = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": "participant1@example.com",
                "full_name": "Participant 1",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
                "subscribe_chapter_mailing": 1,
            }
        )
        participant1.insert()

        chapter_group = self._get_chapter_group()
        self.assertTrue(
            self._is_member_of_group(chapter_group, participant1.email),
            "Should be in chapter group when subscribed",
        )

        # Test 2: Without chapter subscription
        participant2 = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": "participant2@example.com",
                "full_name": "Participant 2",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
                "subscribe_chapter_mailing": 0,
            }
        )
        participant2.insert()

        self.assertFalse(
            self._is_member_of_group(chapter_group, participant2.email),
            "Should not be in chapter group when not subscribed",
        )

        # Test 3: Unsubscribe from chapter
        participant1.subscribe_chapter_mailing = 0
        participant1.save()

        self.assertFalse(
            self._is_member_of_group(chapter_group, participant1.email),
            "Should be removed from chapter group when unsubscribed",
        )

        # Cleanup
        participant1.delete()
        participant2.delete()

    def test_wants_to_attend_locally_validation(self):
        """Test validation when wants_to_attend_locally is True but no localhost"""
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 1,
                "localhost": None,  # No localhost provided
            }
        )

        with self.assertRaises(frappe.ValidationError):
            participant.insert()

    def test_permissions(self):
        """Test participant permissions"""
        # Create participant
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
            }
        )
        participant.insert()

        # Test 1: Administrator has all permissions
        frappe.set_user("Administrator")
        self.assertTrue(participant.has_permission("read"))
        self.assertTrue(participant.has_permission("write"))

        # Test 2: Guest has no write permission
        frappe.set_user("Guest")
        self.assertTrue(participant.has_permission("read"))
        self.assertFalse(participant.has_permission("write"))

        # Test 3: Owner has write permission
        if frappe.db.exists("User", self.PARTICIPANT_EMAIL):
            frappe.set_user(self.PARTICIPANT_EMAIL)
            self.assertTrue(participant.has_permission("read"))
            self.assertTrue(participant.has_permission("write"))

        frappe.set_user("Administrator")
        participant.delete()

    def test_rejection_prevents_reapplication(self):
        """Test that rejected participants cannot reapply to same localhost"""
        # Create a regular user (not system user)
        if not frappe.db.exists("User", self.PARTICIPANT_EMAIL):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": self.PARTICIPANT_EMAIL,
                    "first_name": "Test",
                    "user_type": "Website User",
                }
            ).insert(ignore_permissions=True)

        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
            }
        )
        participant.insert()

        # Reject the participant
        participant.localhost_request_status = "Rejected"
        participant.save()

        # Switch to participant user and try to reapply
        frappe.set_user(self.PARTICIPANT_EMAIL)
        participant.reload()

        # Try to set wants_to_attend_locally = 1 again (reapply)
        participant.wants_to_attend_locally = 1

        with self.assertRaises(frappe.PermissionError):
            participant.save()

        frappe.set_user("Administrator")
        participant.delete()

    def test_localhost_switch_from_different_statuses(self):
        """Test localhost switching works correctly from any status"""
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 1,
                "localhost": self.localhost.name,
                "subscribe_chapter_mailing": 1,
            }
        )
        participant.insert()

        # Test switching from each status
        test_statuses = ["Pending", "Pending Confirmation", "Accepted", "Rejected"]

        for status in test_statuses:
            # Set status
            participant.localhost_request_status = status
            participant.save()

            # Verify in correct group
            current_localhost = participant.localhost
            self._assert_in_group(status, participant.email, current_localhost)

            # Create new localhost
            new_localhost = insert_test_hackathon_localhost(parent_hackathon=self.hackathon.name)

            # Switch localhost
            participant.localhost = new_localhost.name
            participant.save()

            # Verify status reset to Pending
            self.assertEqual(participant.localhost_request_status, "Pending")

            # Verify in Pending group of new localhost
            self._assert_in_group("Pending", participant.email, new_localhost.name)

            # Verify removed from old localhost groups
            old_group = self._get_group_name(status, current_localhost)
            if old_group:
                self.assertFalse(
                    self._is_member_of_group(old_group, participant.email),
                    f"Should be removed from {status} group of old localhost",
                )

            # Clean up new localhost (keep participant on the latest one for next iteration)

        participant.delete()

    def test_without_localhost(self):
        """Test participant without localhost doesn't create localhost groups"""
        participant = frappe.get_doc(
            {
                "doctype": HACKATHON_PARTICIPANT,
                "hackathon": self.hackathon.name,
                "email": self.PARTICIPANT_EMAIL,
                "full_name": "Test Participant",
                "wants_to_attend_locally": 0,
                "subscribe_chapter_mailing": 1,
            }
        )
        participant.insert()

        # Should only be in chapter/hackathon groups, not localhost groups
        chapter_group = self._get_chapter_group()
        self.assertTrue(self._is_member_of_group(chapter_group, participant.email))

        # Should not be in any localhost status groups
        self._assert_not_in_groups(
            ["Pending", "Accepted", "Rejected", "Pending Confirmation"],
            participant.email,
        )

        participant.delete()

    # Helper methods
    def _get_group_name(self, status, localhost_name=None):
        """Get email group name for given status and localhost"""
        target_localhost = localhost_name or self.localhost.name
        group = frappe.db.get_value(
            EMAIL_GROUP,
            {
                "title": f"{status}-{target_localhost}-Localhost",
                "document_type": HACKATHON_LOCALHOST,
                "reference_document": target_localhost,
            },
            "name",
        )
        return group

    def _get_chapter_group(self):
        """Get chapter email group name"""
        group = frappe.db.get_value(
            EMAIL_GROUP,
            {
                "chapter": self.chapter.name,
                "group_type": "Chapter Event Participants",
            },
            "name",
        )
        return group

    def _is_member_of_group(self, group_name, email):
        """Check if email is member of group"""
        if not group_name:
            return False
        return frappe.db.exists(EMAIL_MEMBER, {"email_group": group_name, "email": email})

    def _assert_in_group(self, status, email, localhost_name=None):
        """Assert email is in the group for given status"""
        group_name = self._get_group_name(status, localhost_name)
        self.assertTrue(
            self._is_member_of_group(group_name, email),
            f"Email {email} should be in {status} group",
        )

    def _assert_not_in_groups(self, statuses, email, localhost_name=None):
        """Assert email is not in any of the given status groups"""
        for status in statuses:
            group_name = self._get_group_name(status, localhost_name)
            if group_name:
                self.assertFalse(
                    self._is_member_of_group(group_name, email),
                    f"Email {email} should not be in {status} group",
                )
