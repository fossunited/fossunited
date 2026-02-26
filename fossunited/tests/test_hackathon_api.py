"""
bench --site break.site run-tests --module fossunited.tests.test_hackathon
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.hackathon import (
    create_participant,
    create_project,
    create_team,
    delete_project,
    get_participant,
    join_team_via_code,
    respond_to_join_team_request,
)
from fossunited.doctype_ids import (
    CHAPTER,
    HACKATHON,
    HACKATHON_PARTICIPANT,
    HACKATHON_PROJECT,
    HACKATHON_TEAM,
    HACKATHON_TEAM_MEMBER,
    USER_PROFILE,
)
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_hackathon,
    insert_test_hackathon_join_request,
    insert_test_hackathon_participant,
    insert_test_hackathon_team,
    insert_user_profile,
)


class TestHackathonAPI(FrappeTestCase):
    """Test suite for hackathon permission decorators and security"""

    def setUp(self):
        """Set up before each test"""
        frappe.set_user("Administrator")
        self.user1 = "test_user1@example.com"
        self.user2 = "test_user2@example.com"
        self.user3 = "test_user3@example.com"

        # Create user profiles
        for email in [self.user1, self.user2, self.user3]:
            insert_user_profile(email)

        # Create test chapter and hackathon
        self.chapter = insert_test_chapter(chapter_name="Test Chapter")
        self.hackathon = insert_test_hackathon(
            chapter=self.chapter.name,
            hackathon_name="Test Hackathon",
            max_team_members=2,
        )

    def tearDown(self):
        """Clean up after each test"""
        frappe.set_user("Administrator")
        frappe.delete_doc(HACKATHON_PROJECT, {"hackathon": self.hackathon.name})
        frappe.delete_doc(HACKATHON_TEAM, {"hackathon": self.hackathon.name})
        frappe.delete_doc(HACKATHON_PARTICIPANT, {"hackathon": self.hackathon.name})
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(HACKATHON, self.hackathon.name, force=True)
        frappe.db.delete(
            USER_PROFILE,
            {"email": ["in", [self.user1, self.user2, self.user3]]},
        )

    def test_create_participant_success(self):
        """Test that a logged-in user can create participant"""
        frappe.set_user(self.user1)

        participant = create_participant(
            hackathon={"data": {"name": self.hackathon.name}},
            participant={"full_name": "Test User 1", "is_student": 1},
        )

        self.assertTrue(participant.name)
        self.assertEqual(participant.user, self.user1)
        self.assertEqual(participant.full_name, "Test User 1")

    def test_create_participant_guest_fails(self):
        """Test that guest cannot create participant"""
        frappe.set_user("Guest")

        with self.assertRaises(frappe.PermissionError):
            create_participant(
                hackathon={"data": {"name": self.hackathon.name}},
                participant={"full_name": "Guest User"},
            )

    def test_create_participant_duplicate_fails(self):
        """Test that user cannot register twice for same hackathon"""
        frappe.set_user(self.user1)

        # First registration
        create_participant(
            hackathon={"data": {"name": self.hackathon.name}},
            participant={"full_name": "Test User 1"},
        )

        # Second registration should fail
        with self.assertRaises(Exception) as context:
            create_participant(
                hackathon={"data": {"name": self.hackathon.name}},
                participant={"full_name": "Test User 1"},
            )

        self.assertIn("already registered", str(context.exception))

    def test_get_participant_own_data(self):
        """Test user can get their own participant data"""
        # Create participant using utility
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
            full_name="Test User 1",
        )

        frappe.set_user(self.user1)
        fetched = get_participant(self.hackathon.name)

        self.assertEqual(fetched.name, participant.name)
        self.assertEqual(fetched.user, self.user1)

    def test_create_team_success(self):
        """Test that participant can create a team"""
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )

        frappe.set_user(self.user1)

        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
            },
        )

        self.assertTrue(team.name)
        self.assertEqual(team.team_name, "Test Team")

    def test_create_team_non_participant_fails(self):
        """Test that non-participant cannot create team"""
        frappe.set_user(self.user1)

        with self.assertRaises(frappe.PermissionError):
            create_team(hackathon=self.hackathon.name, team={"team_name": "Test Team"})

    def test_user_cannot_join_multiple_teams(self):
        """Test that a user cannot be in multiple teams"""
        participant1 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )
        participant2 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user2,
            email=self.user2,
        )

        # User 1 creates a team
        frappe.set_user(self.user1)
        create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Team 1",
                "members": [{"member": participant1.name}],
            },
        )

        # User 2 creates another team
        frappe.set_user(self.user2)
        team2 = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Team 2",
                "members": [{"member": participant2.name}],
            },
        )

        # User 1 tries to join team 2
        frappe.set_user(self.user1)

        with self.assertRaises(Exception) as context:
            join_team_via_code(team_code=team2.name, hackathon=self.hackathon.name)

        self.assertIn("is already part of team", str(context.exception))

    def test_join_team_success(self):
        """Test user can successfully join a team"""
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )
        participant2 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user2,
            email=self.user2,
        )

        # User 1 creates a team
        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
            },
        )
        # User 2 joins the team
        frappe.set_user(self.user2)
        join_team_via_code(team_code=team.name, hackathon=self.hackathon.name)
        team.reload()
        # Verify user 2 is in the team
        member_ids = [m.member for m in team.members]
        self.assertIn(participant2.name, member_ids)

    def test_join_team_max_size_fails(self):
        """Test user cannot join team at max capacity"""
        # Set max team size to 2
        frappe.db.set_value(HACKATHON, self.hackathon.name, "max_team_members", 2)

        participant1 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user2,
            email=self.user2,
        )
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user3,
            email=self.user3,
        )

        # User 1 creates team
        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
                "members": [{"member": participant1.name}],
            },
        )

        # User 2 joins
        frappe.set_user(self.user2)
        join_team_via_code(team_code=team.name, hackathon=self.hackathon.name)

        # User 3 tries to join (should fail - team is full)
        frappe.set_user(self.user3)

        with self.assertRaises(Exception) as context:
            join_team_via_code(team_code=team.name, hackathon=self.hackathon.name)

        self.assertIn("Team cannot have more than", str(context.exception))

    def test_create_project_success(self):
        """Test team member can create project"""
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )

        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={"team_name": "Test Team", "members": [{"member": participant.name}]},
        )

        project = create_project(
            hackathon=self.hackathon.name,
            team=team.name,
            project={
                "title": "Test Project",
                "short_description": "A test project",
                "description": "Test project",
            },
        )

        self.assertTrue(project.name)
        self.assertEqual(project.title, "Test Project")
        self.assertEqual(project.team, team.name)

    def test_create_project_non_member_fails(self):
        """Test non-team member cannot create project"""
        participant1 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user2,
            email=self.user2,
        )

        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
                "members": [{"member": participant1.name}],
            },
        )

        # User 2 tries to create project for user 1's team
        frappe.set_user(self.user2)

        with self.assertRaises(frappe.PermissionError):
            create_project(
                hackathon=self.hackathon.name,
                team=team.name,
                project={"title": "Unauthorized Project"},
            )

    def test_create_duplicate_project_fails(self):
        """Test cannot create multiple projects for same team"""
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )

        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
                "members": [{"member": participant.name}],
            },
        )

        # Create first project
        create_project(
            hackathon=self.hackathon.name,
            team=team.name,
            project={"title": "Project 1", "description": "Test project"},
        )

        # Try to create second project
        with self.assertRaises(Exception) as context:
            create_project(
                hackathon=self.hackathon.name,
                team=team.name,
                project={"title": "Project 2", "description": "Test project"},
            )

        self.assertIn("team already has a project", str(context.exception))

    def test_delete_project_success(self):
        """Test team member can delete project"""
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )

        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
                "members": [{"member": participant.name}],
            },
        )

        project = create_project(
            hackathon=self.hackathon.name,
            team=team.name,
            project={"title": "Test Project", "description": "Test project"},
        )

        result = delete_project(hackathon=self.hackathon.name, team=team.name)

        self.assertTrue(result)
        self.assertFalse(frappe.db.exists(HACKATHON_PROJECT, project.name))

    def test_delete_project_non_member_fails(self):
        """Test non-team member cannot delete project"""
        participant1 = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user1,
            email=self.user1,
        )
        insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.user2,
            email=self.user2,
        )

        frappe.set_user(self.user1)
        team = create_team(
            hackathon=self.hackathon.name,
            team={
                "team_name": "Test Team",
                "members": [{"member": participant1.name}],
            },
        )

        create_project(
            hackathon=self.hackathon.name,
            team=team.name,
            project={"title": "Test Project", "description": "Test project"},
        )

        # User 2 tries to delete
        frappe.set_user(self.user2)

        with self.assertRaises(frappe.PermissionError):
            delete_project(hackathon=self.hackathon.name, team=team.name)


class TestRespondToJoinTeamRequest(FrappeTestCase):
    """Tests for the respond_to_join_team_request API endpoint."""

    def setUp(self):
        frappe.set_user("Administrator")
        self.sender = "invite_sender@example.com"
        self.recipient = "invite_recipient@example.com"
        self.outsider = "invite_outsider@example.com"

        for email in [self.sender, self.recipient, self.outsider]:
            insert_user_profile(email)

        self.chapter = insert_test_chapter(chapter_name="Invite Test Chapter")
        self.hackathon = insert_test_hackathon(
            chapter=self.chapter.name,
            hackathon_name="Invite Test Hackathon",
        )

        self.sender_participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.sender,
            email=self.sender,
        )
        self.recipient_participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name,
            user=self.recipient,
            email=self.recipient,
        )

        self.team = insert_test_hackathon_team(hackathon=self.hackathon)
        self.team.append(
            "members",
            {
                "member": self.sender_participant.name,
                "full_name": self.sender_participant.full_name,
                "email": self.sender_participant.email,
            },
        )
        self.team.save()

        frappe.set_user(self.sender)
        self.request = insert_test_hackathon_join_request(
            hackathon_id=self.hackathon.name,
            team_id=self.team.name,
            requested_by=self.sender,
            reciever_email=self.recipient,
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        self.chapter.delete(force=True)
        self.hackathon.delete(force=True)
        self.team.delete(force=True)

    def test_recipient_can_accept_invite(self):
        frappe.set_user(self.recipient)
        result = respond_to_join_team_request(self.request.name, "Accepted")
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "Accepted")
        self.request.reload()
        self.assertEqual(self.request.status, "Accepted")
        self.assertTrue(
            frappe.db.exists(
                HACKATHON_TEAM_MEMBER,
                {"parent": self.team.name, "member": self.recipient_participant.name},
            )
        )

    def test_recipient_can_reject_invite(self):
        frappe.set_user(self.recipient)
        result = respond_to_join_team_request(self.request.name, "Rejected")
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "Rejected")
        self.request.reload()
        self.assertEqual(self.request.status, "Rejected")

    def test_non_recipient_cannot_respond(self):
        frappe.set_user(self.outsider)
        with self.assertRaises(frappe.PermissionError):
            respond_to_join_team_request(self.request.name, "Accepted")

    def test_guest_cannot_respond(self):
        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            respond_to_join_team_request(self.request.name, "Accepted")

    def test_invalid_status_raises_validation_error(self):
        frappe.set_user(self.recipient)
        with self.assertRaises(frappe.ValidationError):
            respond_to_join_team_request(self.request.name, "Pending")

    def test_already_resolved_request_cannot_be_changed(self):
        frappe.set_user(self.recipient)
        respond_to_join_team_request(self.request.name, "Rejected")
        with self.assertRaises(frappe.ValidationError):
            respond_to_join_team_request(self.request.name, "Accepted")
