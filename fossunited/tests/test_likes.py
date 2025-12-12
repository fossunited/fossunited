import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import PROPOSAL, USER_PROFILE

# Import the like functions from your module (adjust path if your module path differs)
from fossunited.templates.includes.like.like import add_like, delete_like, like
from fossunited.tests.utils import (
    insert_cfp_form,
    insert_cfp_submission,
    insert_test_chapter,
    insert_test_event,
)

fake = Faker()
CoreTeam = "test1@example.com"


class TestLikeOnProposal(FrappeTestCase):
    def setUp(self):
        # create the environment similar to your CFP tests
        self.chapter = insert_test_chapter(members=[CoreTeam])
        self.event = insert_test_event(chapter=self.chapter)
        self.cfp = insert_cfp_form(event=self.event.name, status="Live")

        speakers = [
            {
                "full_name": fake.name(),
                "email": fake.email(),
                "designation": fake.job(),
                "organization": fake.company(),
                "bio": "Test Submission",
            }
        ]
        self.submission = insert_cfp_submission(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            speakers=speakers,
            submitted_by=CoreTeam,
        )

        frappe.set_user(CoreTeam)

    def tearDown(self):
        # cleanup comments created by tests
        frappe.set_user("Administrator")
        frappe.db.delete(
            "Comment",
            {
                "reference_doctype": PROPOSAL,
                "reference_name": self.submission.name,
                "comment_type": "Like",
            },
        )

        # remove created docs
        submissions = frappe.get_all(PROPOSAL, {"event": self.event.name}, pluck="name")
        for submission in submissions:
            frappe.delete_doc(PROPOSAL, submission, force=True)
        frappe.db.delete(USER_PROFILE, {"email": CoreTeam})
        self.cfp.delete(force=True)
        self.event.delete(force=True)
        self.chapter.delete(force=True)

        frappe.set_user("Administrator")

    def _get_like_comments(self):
        return frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": PROPOSAL,
                "reference_name": self.submission.name,
                "comment_type": "Like",
            },
            fields=["name", "comment_email", "ip_address", "content"],
        )

    def test_add_like_creates_comment_once(self):
        """
        Add a like once and assert exactly one Comment is created.
        """
        # ensure no likes initially
        before = self._get_like_comments()
        assert len(before) == 0

        # call the backend helper directly (simulates internal call)
        like(PROPOSAL, self.submission.name, True)

        likes = self._get_like_comments()
        self.assertEqual(len(likes), 1)
        # the comment_email should match the current user
        self.assertEqual(likes[0]["comment_email"], frappe.session.user)

    def test_repeated_add_like_does_not_create_duplicates(self):
        """
        Repeated calls to add_like should not create multiple Comment rows for same identity.
        """
        # first add
        add_like(PROPOSAL, self.submission.name)
        # repeated add attempts
        like(PROPOSAL, self.submission.name, True)
        add_like(PROPOSAL, self.submission.name)

        likes = self._get_like_comments()
        # still only one comment for this user
        self.assertEqual(len(likes), 1)

    def test_delete_like_removes_comment(self):
        """
        add then delete a like, ensure comment is removed.
        """
        add_like(PROPOSAL, self.submission.name)
        add_like(PROPOSAL, self.submission.name)
        likes = self._get_like_comments()
        self.assertEqual(len(likes), 1)

        delete_like(PROPOSAL, self.submission.name)
        delete_like(PROPOSAL, self.submission.name)
        likes_after = self._get_like_comments()
        self.assertEqual(len(likes_after), 0)

    def test_different_users_create_multiple_likes(self):
        """
        Likes from different logged-in users should create multiple Comment rows.
        """
        frappe.set_user("user1@example.com")
        add_like(PROPOSAL, self.submission.name)

        frappe.set_user("user2@example.com")
        add_like(PROPOSAL, self.submission.name)

        likes = self._get_like_comments()
        # expect 2 likes (distinct comment_email)
        self.assertEqual(len(likes), 2)
        emails = {c["comment_email"] for c in likes}
        self.assertEqual(emails, {"user1@example.com", "user2@example.com"})

        # restore user for tearDown
        frappe.set_user(CoreTeam)

    def test_guest_like_uses_ip_address(self):
        """
        When user is Guest, the comment should store ip_address and delete_like must match ip.
        """
        frappe.set_user("Guest")
        frappe.local.request_ip = "203.0.113.45"

        # even if tried multiple
        like(PROPOSAL, self.submission.name, True)
        add_like(PROPOSAL, self.submission.name)
        like(PROPOSAL, self.submission.name, True)

        likes = frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": PROPOSAL,
                "reference_name": self.submission.name,
                "comment_type": "Like",
                "ip_address": "203.0.113.45",
            },
            fields=["name"],
        )
        self.assertEqual(len(likes), 1)

        delete_like(PROPOSAL, self.submission.name)
        likes_after = self._get_like_comments()
        self.assertEqual(len(likes_after), 0)

        # cleanup guest state
        frappe.local.request_ip = None
        frappe.set_user(CoreTeam)

    def test_get_likes_unique_guest_by_ip(self):
        """
        Multiple guests with different IPs should be counted separately,
        and get_likes() should properly identify each guest's like.
        """
        # Guest 1 likes
        frappe.set_user("Guest")
        frappe.local.request_ip = "203.0.113.10"
        add_like(PROPOSAL, self.submission.name)

        # Guest 2 likes (different IP)
        frappe.local.request_ip = "203.0.113.20"
        add_like(PROPOSAL, self.submission.name)

        likes = self.submission.get_likes()

        # Should return 2 distinct likes
        self.assertEqual(len(likes), 2)

        # Both should have comment_email = "Guest" but different ip_address
        guest_likes = [lik for lik in likes if lik.get("comment_email") == "Guest"]
        self.assertEqual(len(guest_likes), 2)

        ips = {lik.get("ip_address") for lik in guest_likes}
        self.assertEqual(ips, {"203.0.113.10", "203.0.113.20"})

        frappe.local.request_ip = None
        frappe.set_user(CoreTeam)

    def test_context_like_flag_per_guest_ip(self):
        """
        Context should show like=1 only for the guest with matching IP,
        not for all guests.
        """
        # Guest 1 likes
        frappe.set_user("Guest")
        frappe.local.request_ip = "203.0.113.10"
        add_like(PROPOSAL, self.submission.name)

        # Simulate context building for Guest 1
        likes = self.submission.get_likes()
        current_ip = frappe.local.request_ip
        like_flag = 1 if any(lik.get("ip_address") == current_ip for lik in likes) else 0
        self.assertEqual(like_flag, 1, "Guest 1 should see like=1")

        # Simulate context building for Guest 2 (different IP, hasn't liked)
        frappe.local.request_ip = "203.0.113.99"
        current_ip = frappe.local.request_ip
        like_flag = 1 if any(lik.get("ip_address") == current_ip for lik in likes) else 0
        self.assertEqual(like_flag, 0, "Guest 2 should see like=0")

        frappe.local.request_ip = None
        frappe.set_user(CoreTeam)
