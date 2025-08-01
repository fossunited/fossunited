import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import (
    EVENT,
    # JOB,
    # JOB_STATUS_APPROVED,
    # JOB_STATUS_EXPIRED,
    ORG,
    USER_PROFILE,
)
from fossunited.tests.utils import insert_test_organization

fake = Faker()


class TestOrganization(FrappeTestCase):
    def setUp(self):
        self.lead_user = self.create_user_profile()
        self.member_users = [self.create_user_profile() for _ in range(2)]
        self.organization = insert_test_organization(
            org_lead=self.lead_user.user,
            members=[u.user for u in self.member_users],
            github="https://github.com/example",
            linkedin="https://linkedin.com/example",
            x="https://x.com/example",
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(ORG, self.organization.name, force=True)
        for user in [self.lead_user] + self.member_users:
            frappe.delete_doc(USER_PROFILE, user.name, force=True)

    def print_debug(self, *args):
        """
        Print debugging is better than Think debugging!
        """
        banner = "=" * 20 + "=> DEBUG OUTPUT <=" + "=" * 20
        print(f"\n{banner}")
        for arg in args:
            print(arg)
        print("=" * len(banner) + "\n")

    def create_user_profile(self):
        user = fake.email()

        doc = frappe.get_doc(
            {
                "doctype": USER_PROFILE,
                "user": user,
                "full_name": fake.name(),
                "username": fake.user_name(),
            }
        )
        doc.db_insert()
        return doc

    def test_organization_created_with_valid_data(self):
        # Given: An organization created via insert_test_organization
        print(self.member_users)
        print(self.organization)
        org = self.organization

        # # Then: Organization is inserted correctly
        self.assertTrue(frappe.db.exists(ORG, org.name))
        self.assertEqual(
            org.org_lead, frappe.db.get_value(USER_PROFILE, {"user": self.lead_user.user})
        )
        for member in self.member_users:
            org_link = frappe.db.get_value(USER_PROFILE, member.name, "org_link")
            print(org_link)
            self.assertEqual(org_link, org.org_name)

    def test_organization_social_links(self):
        # Given: An org with social fields
        org = self.organization

        # When: Calling get_social_links
        links = org.get_social_links()

        # Then: Correct keys should be returned
        print(links)
        self.assertIn("github_light", links)
        self.assertIn("linkedin", links)
        self.assertIn("x", links)

    def test_organization_get_members(self):
        # Given: An organization with members
        org = self.organization

        # When: Getting members from get_members
        members = org.get_members()

        # Then: Member info is returned correctly
        self.assertEqual(len(members), len(self.member_users))
        print(members)
        for member in members:
            self.assertIn("full_name", member)
            self.assertIn("profile_picture", member)
            self.assertIn("route", member)

    # D_NOTE: Commented some test since we need to get Job Board doctype

    # def test_get_org_jobs(self):
    #     # Given: A job associated with the org
    #     job_approved = frappe.get_doc(
    #         {
    #             "doctype": JOB,
    #             "title": "Approved Job",
    #             "status": JOB_STATUS_APPROVED,
    #             "company_name": self.organization.org_name,
    #         }
    #     )
    #     job_approved.db_insert()

    #     job_expired = frappe.get_doc(
    #         {
    #             "doctype": JOB,
    #             "title": "Expired Job",
    #             "status": JOB_STATUS_EXPIRED,
    #             "company_name": self.organization.org_name,
    #         }
    #     )
    #     job_expired.db_insert()

    #     # When: Fetching jobs via organization methods
    #     active = self.organization.get_org_jobs(JOB_STATUS_APPROVED)
    #     expired = self.organization.get_org_jobs(JOB_STATUS_EXPIRED)

    #     # Then: Correct jobs are returned
    #     self.assertEqual(len(active), 1)
    #     self.assertEqual(active[0].title, "Approved Job")
    #     self.assertEqual(len(expired), 1)
    #     self.assertEqual(expired[0].title, "Expired Job")

    #     # Cleanup
    #     frappe.delete_doc(JOB, job_approved.name, force=True)
    #     frappe.delete_doc(JOB, job_expired.name, force=True)

    # def test_get_context_structure(self):
    #     # Given: A context dict and organization
    #     context = frappe._dict()

    #     # When: get_context is called
    #     self.organization.get_context(context)

    #     # Then: All required context keys should exist
    #     self.assertIn("members", context)
    #     self.assertIn("social_links", context)
    #     # self.assertIn("org_active_jobs", context)
    #     # self.assertIn("org_expired_jobs", context)
    #     self.assertIn("past_sponsored_events", context)
    #     self.assertIn("present_sponsored_events", context)
    #     self.assertIn("past_sponsored_hackathons", context)
    #     self.assertIn("present_sponsored_hackathons", context)
    #     self.assertIn("org_about_html", context)

    def test_invalid_org_lead_raises(self):
        # When: org_lead email does not exist
        with self.assertRaises(ValueError):
            insert_test_organization(org_lead="invalid@example.com")

    def test_partial_members_does_not_break(self):
        # Given: one valid, one invalid member
        valid_user = self.create_user_profile()
        insert_test_organization(
            org_lead=self.lead_user.user, members=[valid_user.user, "ghost@example.com"]
        )

        # Then: valid member should be linked correctly
        org_link = frappe.db.get_value(USER_PROFILE, valid_user.name, "org_link")
        self.assertIsNotNone(org_link)

    def test_no_sponsored_docs_returns_empty(self):
        # Given: An organization with no sponsorship
        docs = self.organization.get_sponsored_docs(EVENT)
        self.assertEqual(docs, [])

    def test_admin_can_update_organization_social_links(self):
        # Assume 'Administrator' user exists
        frappe.set_user("Administrator")

        self.organization.github = "https://github.com/admin"
        self.organization.save()

        updated = frappe.get_doc(ORG, self.organization.name)
        # self.print_debug(updated.github)
        self.assertEqual(updated.github, "https://github.com/admin")

        frappe.set_user("Guest")

    def test_normal_user_cannot_update_org_info(self):
        unrelated_user = self.create_user_profile()
        frappe.set_user(unrelated_user.user)

        self.organization.twitter = "https://x.com/hacker"

        with self.assertRaises(frappe.PermissionError):
            self.organization.save()

        frappe.set_user("Guest")

    def test_guest_cannot_update_org(self):
        frappe.set_user("Guest")

        self.organization.org_about = "Hacked"

        with self.assertRaises(frappe.PermissionError):
            self.organization.save()

    def test_guest_can_retrieve_organization_info(self):
        frappe.set_user("Guest")

        org = frappe.get_doc(ORG, self.organization.name)

        self.assertEqual(org.org_name, self.organization.org_name)
        self.assertIsNotNone(org.org_about)

    def test_authenticated_user_can_view_org_info(self):
        user = self.create_user_profile()
        frappe.set_user(user.user)

        org = frappe.get_doc(ORG, self.organization.name)

        self.assertEqual(org.org_name, self.organization.org_name)
        self.assertIsNotNone(org.org_lead)

    def test_member_user_cannot_update_organization(self):
        member = self.member_users[0]
        frappe.set_user(member.user)

        self.organization.website = "https://member-edit.com"
        with self.assertRaises(frappe.PermissionError):
            self.organization.save()
