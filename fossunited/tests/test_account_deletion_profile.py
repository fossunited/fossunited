"""Regression coverage for profile anonymization through Frappe's deletion workflow."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import USER_PROFILE
from fossunited.foss_profiles.account_deletion import (
    PROFILE_CHILD_FIELDS,
    redact_profile_children,
)
from fossunited.foss_profiles.doctype.foss_user_profile.foss_user_profile import (
    PrivateProfileError,
)
from fossunited.tests.factories.user_factory import UserFactory, get_foss_profile_id


class TestAccountDeletionProfile(FrappeTestCase):
    def setUp(self):
        self.addCleanup(frappe.db.rollback)
        self.email = f"del_profile_{frappe.generate_hash(length=10)}@example.com"
        self.user = UserFactory.create(email=self.email, first_name="Jane", last_name="Doe")
        self.profile = get_foss_profile_id(self.email)
        self.assertTrue(self.profile)
        self.seeded_pii = {
            "full_name": "Jane Doe",
            "bio": "FOSS enthusiast from Bangalore",
            "about": "Long-form about me",
            "profile_photo": "/files/jane-photo.png",
            "cover_image": "/files/jane-cover.png",
            "website": "https://jane.example.com",
            **{
                field: f"https://example.com/jane/{field}"
                for field in (
                    "github",
                    "gitlab",
                    "linkedin",
                    "mastodon",
                    "bluesky",
                    "x",
                    "instagram",
                    "devto",
                    "youtube",
                    "medium",
                )
            },
        }
        doc = frappe.get_doc(USER_PROFILE, self.profile)
        doc.update({"is_published": 1, "is_private": 0, **self.seeded_pii})
        self.child_pii = {
            "education": {
                "institution": "Acme University",
                "degree": "BSc",
                "field_of_study": "Computer Science",
                "start_year": "2018",
                "end_year": "2022",
            },
            "experience": {
                "title": "Developer",
                "company": "Acme",
                "company_website": "https://acme.example.com",
                "city": "Bangalore",
                "country": "India",
                "description": "Private work history",
                "employment_type": "Full-time",
                "start_date": "2022-01-01",
                "end_date": "2023-01-01",
            },
            "projects": {
                "project_name": "Jane's Project",
                "tagline": "My private project",
                "project_link": "https://example.com/jane/project",
                "cover_image": "/files/jane-project.png",
            },
        }
        for table, values in self.child_pii.items():
            doc.append(table, values)
        doc.save(ignore_permissions=True)
        # Location is a Link and gender is fetched from User. Seed stored copies
        # directly to exercise redaction without depending on optional master data.
        self.seeded_pii.update({"current_city": "Bangalore", "gender": "Female"})
        frappe.db.set_value(USER_PROFILE, self.profile, dict(self.seeded_pii))
        self.child_names = {table: doc.get(table)[0].name for table in self.child_pii}

        # Another person's rows can have been edited by the deleting user.
        other = UserFactory.create()
        self.other_profile = get_foss_profile_id(other.name)
        other_doc = frappe.get_doc(USER_PROFILE, self.other_profile)
        for table, values in self.child_pii.items():
            other_doc.append(table, values)
        other_doc.save(ignore_permissions=True)
        for row in other_doc.get_all_children():
            frappe.db.set_value(row.doctype, row.name, "owner", self.email)
        self.other_before = frappe.get_doc(USER_PROFILE, self.other_profile).as_dict()

    def _request(self):
        return frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.email}
        ).insert(ignore_permissions=True)

    def _run_deletion(self):
        req = self._request()
        req.status = "Pending Approval"
        req.save(ignore_permissions=True)
        req.trigger_data_deletion()
        req.reload()
        return req

    def _assert_children_redacted(self):
        profile = frappe.get_doc(USER_PROFILE, self.profile)
        for table, originals in self.child_pii.items():
            row = profile.get(table)[0]
            self.assertEqual(row.name, self.child_names[table])
            for field in PROFILE_CHILD_FIELDS[row.doctype]:
                actual = row.get(field)
                self.assertNotEqual(str(actual), originals[field], f"{table}.{field}")
                self.assertTrue(actual, f"{table}.{field} should have a placeholder")

    def test_profile_and_all_child_tables_redacted(self):
        req = self._run_deletion()
        profile = frappe.get_doc(USER_PROFILE, self.profile)
        for field, original in self.seeded_pii.items():
            self.assertNotEqual(profile.get(field), original, field)
        self.assertEqual(profile.full_name, req.anonymization_value_map["Data"])
        self.assertEqual(profile.email, req.name)
        self.assertEqual(profile.user, req.name)
        self.assertFalse(frappe.db.exists("User", self.email))
        self.assertEqual(frappe.db.get_value("User", req.name, "enabled"), 0)
        self.assertEqual(req.status, "Deleted")
        self.assertTrue(all(step.status == "Deleted" for step in req.deletion_steps))
        # The profile and its children survive, preserving incoming links.
        self._assert_children_redacted()
        other = frappe.get_doc(USER_PROFILE, self.other_profile).as_dict()
        for field in ("user", "full_name", "email", "username", "route"):
            self.assertEqual(other[field], self.other_before[field], field)
        for table in self.child_pii:
            self.assertEqual(len(other[table]), len(self.other_before[table]))
            for actual, expected in zip(other[table], self.other_before[table], strict=True):
                self.assertEqual(actual["name"], expected["name"])
                for field in PROFILE_CHILD_FIELDS[actual["doctype"]]:
                    self.assertEqual(actual[field], expected[field], f"{table}.{field}")

    def test_user_owned_children_are_also_redacted(self):
        profile = frappe.get_doc(USER_PROFILE, self.profile)
        for row in profile.get_all_children():
            frappe.db.set_value(row.doctype, row.name, "owner", self.email)
        self._run_deletion()
        self._assert_children_redacted()

    def test_anonymized_profile_not_served_for_guest_or_admin(self):
        self._run_deletion()
        for user in ("Guest", "Administrator"):
            with self.set_user(user):
                with self.assertRaises(frappe.DoesNotExistError):
                    frappe.get_doc(USER_PROFILE, self.profile).get_context(frappe._dict())

    def test_normal_public_profile_still_renders(self):
        with self.set_user("Guest"):
            context = frappe._dict()
            frappe.get_doc(USER_PROFILE, self.profile).get_context(context)
            self.assertIn("Jane Doe", context.pagetitle)
            self.assertEqual(context.no_cache, 1)

    def test_private_profile_still_rejects_guest(self):
        frappe.db.set_value(USER_PROFILE, self.profile, "is_private", 1)
        with self.set_user("Guest"):
            with self.assertRaises(PrivateProfileError):
                frappe.get_doc(USER_PROFILE, self.profile).get_context(frappe._dict())

    def test_unverified_request_does_not_change_profile(self):
        req = self._request()
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        with self.assertRaises(frappe.ValidationError):
            req.trigger_data_deletion()
        self.assertEqual(frappe.get_doc(USER_PROFILE, self.profile).as_dict(), before)
        self.assertEqual(req.status, "Pending Verification")
        self.assertEqual(frappe.db.get_value("User", self.email, "enabled"), 1)

    def test_non_manager_cannot_approve_deletion(self):
        req = self._request()
        req.status = "Pending Approval"
        req.save(ignore_permissions=True)
        # only_for intentionally bypasses role checks in test mode.
        with self.set_user(self.email), patch.dict(frappe.flags, in_test=False):
            with self.assertRaises(frappe.PermissionError):
                req.trigger_data_deletion()
        self.assertEqual(frappe.db.get_value("User", self.email, "enabled"), 1)
        self.assertEqual(frappe.db.get_value(USER_PROFILE, self.profile, "full_name"), "Jane Doe")

    def test_child_cleanup_is_idempotent(self):
        req = self._run_deletion()
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        redact_profile_children(req)
        after = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        for table in self.child_pii:
            self.assertEqual(
                [{k: v for k, v in row.items() if k != "modified"} for row in before[table]],
                [{k: v for k, v in row.items() if k != "modified"} for row in after[table]],
            )

    def test_pending_request_does_not_scrub_child_data(self):
        req = self._request()
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        redact_profile_children(req)
        self.assertEqual(frappe.get_doc(USER_PROFILE, self.profile).as_dict(), before)
