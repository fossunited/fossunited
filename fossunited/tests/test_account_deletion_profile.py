"""Regression coverage for profile anonymization through Frappe's deletion workflow."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import USER_PROFILE
from fossunited.foss_profiles.account_deletion import (
    PROFILE_CHILD_DOCTYPES,
    PROFILE_NULL_FIELDS,
    finalize_profile_anonymization,
)
from fossunited.foss_profiles.doctype.foss_user_profile.foss_user_profile import (
    PrivateProfileError,
)
from fossunited.tests.factories.user_factory import UserFactory, get_foss_profile_id

CHILD_ROWS = {
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


class TestAccountDeletionProfile(FrappeTestCase):
    def setUp(self):
        self.addCleanup(frappe.db.rollback)
        self.email = f"del_profile_{frappe.generate_hash(length=10)}@example.com"
        self.user = UserFactory.create(email=self.email, first_name="Jane", last_name="Doe")
        self.profile = get_foss_profile_id(self.email)
        self.assertTrue(self.profile)

        self.redacted_data = {
            "full_name": "Jane Doe",
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
        self.null_values = {
            "bio": "FOSS enthusiast from Bangalore",
            "about": "Long-form about me",
            "profile_photo": "/files/jane-photo.png",
            "cover_image": "/files/jane-cover.png",
        }
        doc = frappe.get_doc(USER_PROFILE, self.profile)
        doc.update({"is_published": 1, "is_private": 0, **self.redacted_data, **self.null_values})
        self._seed_children(doc)
        doc.save(ignore_permissions=True)
        self.orig_username = doc.username
        self.orig_route = doc.route
        # current_city is a Link and gender is fetched from User; seed stored copies
        # directly so redaction is exercised without optional master data.
        frappe.db.set_value(
            USER_PROFILE, self.profile, {"current_city": "Bangalore", "gender": "Female"}
        )

        # A File attached to the profile — its photos must not stay public.
        self.file_name = (
            frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": "jane-photo.png",
                    "attached_to_doctype": USER_PROFILE,
                    "attached_to_name": self.profile,
                    "is_private": 0,
                    "content": "fake-image-bytes",
                }
            )
            .insert(ignore_permissions=True)
            .name
        )

        # Control: another person's profile + child rows must be untouched.
        self.other_profile = get_foss_profile_id(UserFactory.create().name)
        other = frappe.get_doc(USER_PROFILE, self.other_profile)
        self._seed_children(other)
        other.save(ignore_permissions=True)
        self.other_before = frappe.get_doc(USER_PROFILE, self.other_profile).as_dict()
        # Control File on the other profile — deletion must be scoped, not blanket.
        self.other_file_name = (
            frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": "other-photo.png",
                    "attached_to_doctype": USER_PROFILE,
                    "attached_to_name": self.other_profile,
                    "is_private": 0,
                    "content": "other-image-bytes",
                }
            )
            .insert(ignore_permissions=True)
            .name
        )

    def _seed_children(self, doc):
        for table, values in CHILD_ROWS.items():
            doc.append(table, values)
        skill = (
            frappe.db.get_value("FOSS User Skill", {"skill": "Python"})
            or frappe.get_doc({"doctype": "FOSS User Skill", "skill": "Python"})
            .insert(ignore_permissions=True)
            .name
        )
        doc.append("skills", {"skill": skill})

    def _run_deletion(self):
        req = frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.email}
        ).insert(ignore_permissions=True)
        req.status = "Pending Approval"
        req.save(ignore_permissions=True)
        req.trigger_data_deletion()
        req.reload()
        return req

    def _child_count(self, profile):
        return {
            dt: frappe.db.count(dt, {"parenttype": USER_PROFILE, "parent": profile})
            for dt in PROFILE_CHILD_DOCTYPES
        }

    # ---- the full happy path -------------------------------------------------
    def test_full_profile_anonymization(self):
        req = self._run_deletion()
        redacted = req.anonymization_value_map["Data"]
        p = frappe.get_doc(USER_PROFILE, self.profile)

        # Plain Data fields -> standard placeholder; email (filter_by) -> anon id.
        for field in self.redacted_data:
            self.assertEqual(p.get(field), redacted, field)
        self.assertEqual(p.email, req.name)
        self.assertEqual(p.gender, redacted)

        # Broken-placeholder fields are cleared.
        for field in PROFILE_NULL_FIELDS:
            self.assertIsNone(p.get(field), field)

        # Hidden from page + listings, and the name-derived route is regenerated.
        self.assertEqual(p.is_published, 0)
        self.assertEqual(p.is_private, 1)
        self.assertTrue(p.username.startswith("deleted_"))
        self.assertEqual(p.route, f"u/{p.username}")
        self.assertNotEqual(p.username, self.orig_username)

        # Child rows are deleted outright (pure PII, no incoming links).
        self.assertEqual(self._child_count(self.profile), dict.fromkeys(PROFILE_CHILD_DOCTYPES, 0))

        # Uploaded File is gone.
        self.assertFalse(frappe.db.exists("File", self.file_name))

        # Account itself anonymized.
        self.assertEqual(p.user, req.name)
        self.assertFalse(frappe.db.exists("User", self.email))
        self.assertEqual(frappe.db.get_value("User", req.name, "enabled"), 0)
        # The User's own handle must not keep the person's chosen username.
        self.assertNotEqual(frappe.db.get_value("User", req.name, "username"), self.orig_username)
        self.assertEqual(req.status, "Deleted")
        self.assertTrue(all(step.status == "Deleted" for step in req.deletion_steps))

        # Shared skill master is kept (only the join rows are removed).
        self.assertTrue(frappe.db.exists("FOSS User Skill", "Python"))

    def test_other_profile_is_untouched(self):
        self._run_deletion()
        other = frappe.get_doc(USER_PROFILE, self.other_profile).as_dict()
        for field in ("user", "full_name", "email", "username", "route"):
            self.assertEqual(other[field], self.other_before[field], field)
        counts = self._child_count(self.other_profile)
        self.assertTrue(all(c >= 1 for c in counts.values()), counts)
        # File deletion is scoped to the target profile only.
        self.assertTrue(frappe.db.exists("File", self.other_file_name))

    # ---- render guards -------------------------------------------------------
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

    # ---- workflow guards -----------------------------------------------------
    def test_unverified_request_does_not_change_profile(self):
        req = frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.email}
        ).insert(ignore_permissions=True)
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        with self.assertRaises(frappe.ValidationError):
            req.trigger_data_deletion()
        self.assertEqual(frappe.get_doc(USER_PROFILE, self.profile).as_dict(), before)
        self.assertEqual(req.status, "Pending Verification")
        self.assertEqual(frappe.db.get_value("User", self.email, "enabled"), 1)

    def test_non_manager_cannot_approve_deletion(self):
        req = frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.email}
        ).insert(ignore_permissions=True)
        req.status = "Pending Approval"
        req.save(ignore_permissions=True)
        with self.set_user(self.email), patch.dict(frappe.flags, in_test=False):
            with self.assertRaises(frappe.PermissionError):
                req.trigger_data_deletion()
        self.assertEqual(frappe.db.get_value("User", self.email, "enabled"), 1)
        self.assertEqual(frappe.db.get_value(USER_PROFILE, self.profile, "full_name"), "Jane Doe")

    # ---- handler idempotence / guards ---------------------------------------
    def test_finalize_is_idempotent(self):
        req = self._run_deletion()
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        finalize_profile_anonymization(req)  # run again
        after = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        self.assertEqual(self._child_count(self.profile), dict.fromkeys(PROFILE_CHILD_DOCTYPES, 0))
        for field in PROFILE_NULL_FIELDS:
            self.assertIsNone(after.get(field))
        self.assertEqual(before["username"], after["username"])

    def test_pending_request_is_a_noop(self):
        req = frappe.get_doc(
            {"doctype": "Personal Data Deletion Request", "email": self.email}
        ).insert(ignore_permissions=True)
        before = frappe.get_doc(USER_PROFILE, self.profile).as_dict()
        finalize_profile_anonymization(req)  # status != Deleted
        self.assertEqual(frappe.get_doc(USER_PROFILE, self.profile).as_dict(), before)
