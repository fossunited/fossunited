# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt
import uuid

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import USER_PROFILE
from fossunited.foss_profiles.doctype.foss_user_profile.foss_user_profile import (
    PrivateProfileError,
)
from fossunited.tests.utils import insert_user_profile

fake = Faker()


class TestFOSSUserProfile(FrappeTestCase):
    def test_add_profile(self):
        # When a FOSSUnitedProfile is created for the user
        inserted_email = fake.email()
        insert_user_profile(inserted_email)

        # Then verify that the Profile has been stored as expected
        self.assertTrue(frappe.db.exists(USER_PROFILE, {"user": inserted_email}))

    def test_private_profile_access(self):
        test_name = fake.name()
        test_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": str(uuid.uuid4()) + "@fossunited.org",
                "first_name": test_name.split(" ")[0],
                "name": test_name,
                "full_name": test_name,
            },
        ).insert()

        # Given a private profile
        private_profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
        frappe.db.set_value(USER_PROFILE, private_profile.name, "is_private", "1")

        current_user = frappe.session.user
        frappe.set_user("guest@example.com")

        with self.assertRaises(PrivateProfileError) as context:
            # When accessing the profile not as admin or user
            # then an exception is raised
            private_profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
            # Simulate loading the profile
            private_profile.get_context({})

        self.assertTrue("Profile is Private" in str(context.exception))

        frappe.set_user(current_user)
        frappe.delete_doc(USER_PROFILE, private_profile.name)
        frappe.delete_doc("User", test_user.name)

    def test_profile_route(self):
        # When a user profile is created
        # Then the route for that profile should be of format: u/<username>
        test_email = fake.email()
        test_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": test_email,
                "first_name": fake.name().split()[0],
            },
        ).insert()

        test_user.reload()

        profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
        profile.username = fake.user_name()
        profile.save(ignore_permissions=True)

        profile.reload()

        self.assertTrue(profile.route == f"u/{profile.username}")

        profile.delete(force=True)
        test_user.delete(force=True)

    def test_share_user_with_self(self):
        frappe.set_user("Guest")

        test_email = fake.email()

        test_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": test_email,
                "first_name": fake.name().split()[0],
            },
        ).insert(ignore_permissions=True)
        test_user.reload()

        profile_id = frappe.db.get_value(
            USER_PROFILE,
            {"user": test_user.name},
            "name",
        )

        self.assertTrue(
            frappe.db.exists(
                "DocShare",
                {
                    "user": test_user.name,
                    "share_doctype": USER_PROFILE,
                    "share_name": profile_id,
                },
            )
        )

        test_user.delete(force=True)
