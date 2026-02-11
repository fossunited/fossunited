import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import HACKATHON_TEAM, HACKATHON_TEAM_MEMBER, USER_PROFILE
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_hackathon,
    insert_test_hackathon_participant,
    insert_test_hackathon_team,
    insert_user_profile,
)


class TestFOSSHackathonTeam(FrappeTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()
        self.hackathon = insert_test_hackathon(
            chapter=self.chapter.name, is_team_mandatory=True, max_team_members=3
        )

        self.team = insert_test_hackathon_team(hackathon=self.hackathon)

        self.participants = []
        for i in range(4):
            email = f"team_user_{i}@test.com"
            insert_user_profile(email)

            participant = insert_test_hackathon_participant(
                hackathon_id=self.hackathon.name,
                email=email,
                user=email,
            )

            self.participants.append(participant)

    def tearDown(self):
        frappe.set_user("Administrator")
        self.chapter.delete(force=True)
        self.team.delete(force=True)
        for participant in self.participants:
            participant.delete(force=True)
        self.hackathon.delete(force=True)

        for i in range(4):
            email = f"team_user_{i}@test.com"
            profile = frappe.db.get_value(USER_PROFILE, {"user": email}, "name")
            if profile:
                frappe.delete_doc(USER_PROFILE, profile, force=True)
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True)

    def test_add_member_to_team(self):
        # Given a hackathon with a defined max_team_members size
        # When the max number of participants are added to that team
        participant_ids = []
        for i in range(self.hackathon.max_team_members):
            participant_ids.append(self.participants[i].name)
            self.team.append("members", {"member": self.participants[i].name})
        self.team.save()

        # Then it should add those members to the team without any error
        self.assertEqual(len(self.team.members), self.hackathon.max_team_members)

        # Get participant ids of team members of self.team, those should match the
        # IDs of participants that were meant to be added to the team
        members_emails = frappe.get_all(
            HACKATHON_TEAM_MEMBER, {"parent": self.team.name}, pluck="member"
        )
        self.assertEqual(members_emails.sort(), participant_ids.sort())

    def test_add_member_exceeding_max_size(self):
        # Given a hackathon with a defined max number of team members
        # When more than max no. of members are tried to be added to a team
        for i in range(self.hackathon.max_team_members + 1):
            self.team.append("members", {"member": self.participants[i].name})
        # Then a validation error should be raised.
        self.assertRaises(frappe.exceptions.ValidationError, self.team.save)

    def test_cannot_add_duplicate_member(self):
        participant = self.participants[0]

        self.team.append("members", {"member": participant.name})
        self.team.append("members", {"member": participant.name})

        with self.assertRaises(frappe.ValidationError):
            self.team.save()

    def test_member_cannot_join_multiple_teams(self):
        """starting from 2027 ideally they should not be in multiple teams"""
        participant = self.participants[0]

        # Add member to first team
        self.team.append("members", {"member": participant.name})
        self.team.save()

        # Create second team
        team2 = insert_test_hackathon_team(hackathon=self.hackathon)

        team2.append("members", {"member": participant.name})

        with self.assertRaises(frappe.ValidationError):
            team2.save()

        team2.delete(force=True)

    def test_team_member_can_edit_team(self):
        participant = self.participants[0]

        # add participant to team
        self.team.append("members", {"member": participant.name})
        self.team.save()

        # switch to participant user
        frappe.set_user(participant.user)

        self.team.team_name = "Updated by member"
        self.team.save()

    def test_non_member_cannot_edit_team(self):
        participant = self.participants[0]
        other_participant = self.participants[1]

        self.team.append("members", {"member": participant.name})
        self.team.save()

        frappe.set_user(other_participant.user)
        team = frappe.get_doc(HACKATHON_TEAM, self.team.name)
        team.team_name = "Hacked name"
        with self.assertRaises(frappe.PermissionError):
            team.save()
