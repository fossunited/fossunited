# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt
import uuid

import frappe
from faker import Faker
from frappe.tests import UnitTestCase

from fossunited.doctype_ids import USER_PROFILE


class TestFOSSUserProfile(UnitTestCase):
    def test_add_profile(self):
        # Given a user that does not have a FOSSUnitedProfile
        fake = Faker()
        inserted_username = fake.user_name()
        inserted_name = fake.name()
        profile_exists = frappe.db.exists(USER_PROFILE, {"username": inserted_username})
        self.assertFalse(profile_exists)

        # When a FOSSUnitedProfile is created for the user
        # Note that a Frappe User needs to exist before a Profile can be created
        # Verify that only required values are provided below
        frappe_user = frappe.get_doc(
            {
                "doctype": "User",
                # Create a unique email address as it is used as a database key
                "email": str(uuid.uuid4()) + "@fossunited.org",
                "first_name": inserted_name.split(" ")[0],
                "name": inserted_name,
                "full_name": inserted_name,
            },
        ).insert()

        # Then verify that the Profile has been stored as expected
        profile_exists = frappe.db.exists(USER_PROFILE, {"user": frappe_user.name})

        self.assertTrue(profile_exists)
