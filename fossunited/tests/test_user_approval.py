"""
Tests for user signup approval flow (fossunited.fossunited.user_utils).

Run:
    bench --site foss.localhost run-tests --module fossunited.tests.test_user_approval
"""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import USER_PROFILE
from fossunited.fossunited.user_utils import approve_user, deny_user, handle_user_signup


def _make_web_user(email, full_name="Test User"):
    if frappe.db.exists("User", email):
        frappe.delete_doc("User", email, force=True, ignore_permissions=True)
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": full_name.split()[0],
            "last_name": " ".join(full_name.split()[1:]),
            "enabled": 1,
            "user_type": "Website User",
        }
    )
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()
    return user


def _mock_system_doc(email):
    # Frappe auto-downgrades System User → Website User in validate if no desk
    # roles exist, so test handle_user_signup directly with a controlled doc.
    return frappe._dict(
        {
            "name": email,
            "email": email,
            "user_type": "System User",
            "full_name": "Desk User",
            "username": "deskuser",
        }
    )


def _cleanup(email):
    frappe.set_user("Administrator")
    frappe.db.delete(USER_PROFILE, {"user": email})
    if frappe.db.exists("User", email):
        frappe.delete_doc("User", email, force=True, ignore_permissions=True)


class TestWebSignup(FrappeTestCase):
    EMAIL = "web_signup_test@example.com"

    def setUp(self):
        frappe.flags.mute_emails = True
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.flags.mute_emails = False
        _cleanup(self.EMAIL)

    def test_web_signup_disables_user(self):
        _make_web_user(self.EMAIL)
        self.assertEqual(frappe.db.get_value("User", self.EMAIL, "enabled"), 0)

    def test_web_signup_does_not_create_profile(self):
        _make_web_user(self.EMAIL)
        self.assertFalse(frappe.db.exists(USER_PROFILE, {"user": self.EMAIL}))


class TestDeskUserCreation(FrappeTestCase):
    EMAIL = "desk_user_test@example.com"

    def setUp(self):
        frappe.flags.mute_emails = True
        frappe.set_user("Administrator")
        if not frappe.db.exists("User", self.EMAIL):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": self.EMAIL,
                    "first_name": "Desk",
                    "enabled": 1,
                    "user_type": "Website User",
                    "new_password": frappe.utils.random_string(10),
                }
            ).insert(ignore_permissions=True)
            frappe.db.set_value("User", self.EMAIL, "enabled", 1)

    def tearDown(self):
        frappe.flags.mute_emails = False
        _cleanup(self.EMAIL)

    def test_system_user_hook_creates_profile(self):
        handle_user_signup(_mock_system_doc(self.EMAIL), method=None)
        self.assertTrue(frappe.db.exists(USER_PROFILE, {"user": self.EMAIL}))

    def test_system_user_hook_does_not_disable(self):
        handle_user_signup(_mock_system_doc(self.EMAIL), method=None)
        self.assertEqual(frappe.db.get_value("User", self.EMAIL, "enabled"), 1)


class TestApproveUser(FrappeTestCase):
    EMAIL = "approve_flow_test@example.com"

    def setUp(self):
        frappe.flags.mute_emails = True
        frappe.set_user("Administrator")
        _make_web_user(self.EMAIL, "Approve Me")

    def tearDown(self):
        frappe.flags.mute_emails = False
        _cleanup(self.EMAIL)

    def test_approve_enables_user(self):
        approve_user(self.EMAIL)
        self.assertEqual(frappe.db.get_value("User", self.EMAIL, "enabled"), 1)

    def test_approve_creates_profile(self):
        approve_user(self.EMAIL)
        self.assertTrue(frappe.db.exists(USER_PROFILE, {"user": self.EMAIL}))

    def test_approve_is_idempotent(self):
        approve_user(self.EMAIL)
        approve_user(self.EMAIL)
        self.assertEqual(frappe.db.count(USER_PROFILE, {"user": self.EMAIL}), 1)

    def test_approve_blocked_for_non_system_manager(self):
        with patch(
            "fossunited.fossunited.user_utils.frappe.only_for", side_effect=frappe.PermissionError
        ):
            with self.assertRaises(frappe.PermissionError):
                approve_user(self.EMAIL)


class TestDenyUser(FrappeTestCase):
    EMAIL = "deny_flow_test@example.com"

    def setUp(self):
        frappe.flags.mute_emails = True
        frappe.set_user("Administrator")
        _make_web_user(self.EMAIL, "Deny Me")

    def tearDown(self):
        frappe.flags.mute_emails = False
        _cleanup(self.EMAIL)

    def test_deny_deletes_user(self):
        deny_user(self.EMAIL)
        self.assertFalse(frappe.db.exists("User", self.EMAIL))

    def test_deny_no_orphan_profile(self):
        deny_user(self.EMAIL)
        self.assertFalse(frappe.db.exists(USER_PROFILE, {"user": self.EMAIL}))

    def test_deny_idempotent(self):
        deny_user(self.EMAIL)
        deny_user(self.EMAIL)  # must not raise

    def test_deny_approved_user_removes_both(self):
        approve_user(self.EMAIL)
        deny_user(self.EMAIL)
        self.assertFalse(frappe.db.exists("User", self.EMAIL))

    def test_deny_blocked_for_non_system_manager(self):
        with patch(
            "fossunited.fossunited.user_utils.frappe.only_for", side_effect=frappe.PermissionError
        ):
            with self.assertRaises(frappe.PermissionError):
                deny_user(self.EMAIL)
