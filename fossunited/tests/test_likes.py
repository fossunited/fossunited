import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import PROPOSAL
from fossunited.templates.includes.like.like import add_like, delete_like, like
from fossunited.tests.factories.foss_chapter_event_factory import FOSSChapterEventFactory
from fossunited.tests.factories.foss_chapter_factory import FOSSChapterFactory
from fossunited.tests.factories.foss_event_cfp_submission_factory import (
    FOSSEventCFPFactory,
    FOSSEventCFPSubmissionFactory,
)
from fossunited.tests.factories.user_factory import UserFactory

fake = Faker()


class TestLikeOnProposal(FrappeTestCase):
    def setUp(self):
        self.core_team_user = UserFactory.create("with_foss_website_user_role")
        self.chapter = FOSSChapterFactory.create(
            "with_members", members=[self.core_team_user.name]
        )
        self.event = FOSSChapterEventFactory.create(chapter=self.chapter.name)
        self.cfp = FOSSEventCFPFactory.create(event=self.event.name, status="Live")

        self.submission = FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            submitted_by=self.core_team_user.name,
        )

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
        with self.set_user(self.core_team_user.name):
            before = self._get_like_comments()
            assert len(before) == 0

            like(PROPOSAL, self.submission.name, True)

            likes = self._get_like_comments()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0]["comment_email"], frappe.session.user)

    def test_repeated_add_like_does_not_create_duplicates(self):
        with self.set_user(self.core_team_user.name):
            add_like(PROPOSAL, self.submission.name)
            like(PROPOSAL, self.submission.name, True)
            add_like(PROPOSAL, self.submission.name)

            likes = self._get_like_comments()
            self.assertEqual(len(likes), 1)

    def test_delete_like_removes_comment(self):
        with self.set_user(self.core_team_user.name):
            add_like(PROPOSAL, self.submission.name)
            add_like(PROPOSAL, self.submission.name)
            likes = self._get_like_comments()
            self.assertEqual(len(likes), 1)

            delete_like(PROPOSAL, self.submission.name)
            delete_like(PROPOSAL, self.submission.name)
            likes_after = self._get_like_comments()
            self.assertEqual(len(likes_after), 0)

    def test_different_users_create_multiple_likes(self):
        user1 = UserFactory.create("with_foss_website_user_role")
        user2 = UserFactory.create("with_foss_website_user_role")

        with self.set_user(user1.name):
            add_like(PROPOSAL, self.submission.name)

        with self.set_user(user2.name):
            add_like(PROPOSAL, self.submission.name)

        likes = self._get_like_comments()
        self.assertEqual(len(likes), 2)
        emails = {c["comment_email"] for c in likes}
        self.assertEqual(emails, {user1.name, user2.name})

    def test_guest_like_uses_ip_address(self):
        with self.set_user("Guest"):
            frappe.local.request_ip = "203.0.113.45"

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

            frappe.local.request_ip = None

    def test_get_likes_unique_guest_by_ip(self):
        with self.set_user("Guest"):
            frappe.local.request_ip = "203.0.113.10"
            add_like(PROPOSAL, self.submission.name)

            frappe.local.request_ip = "203.0.113.20"
            add_like(PROPOSAL, self.submission.name)

            likes = self.submission.get_likes()

            self.assertEqual(len(likes), 2)

            guest_likes = [lik for lik in likes if lik.get("comment_email") == "Guest"]
            self.assertEqual(len(guest_likes), 2)

            ips = {lik.get("ip_address") for lik in guest_likes}
            self.assertEqual(ips, {"203.0.113.10", "203.0.113.20"})

            frappe.local.request_ip = None

    def test_context_like_flag_per_guest_ip(self):
        with self.set_user("Guest"):
            frappe.local.request_ip = "203.0.113.10"
            add_like(PROPOSAL, self.submission.name)

            likes = self.submission.get_likes()
            current_ip = frappe.local.request_ip
            like_flag = 1 if any(lik.get("ip_address") == current_ip for lik in likes) else 0
            self.assertEqual(like_flag, 1, "Guest 1 should see like=1")

            frappe.local.request_ip = "203.0.113.99"
            current_ip = frappe.local.request_ip
            like_flag = 1 if any(lik.get("ip_address") == current_ip for lik in likes) else 0
            self.assertEqual(like_flag, 0, "Guest 2 should see like=0")

            frappe.local.request_ip = None
