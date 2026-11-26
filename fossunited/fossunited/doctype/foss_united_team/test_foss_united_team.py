# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate

from fossunited.doctype_ids import FOSS_UNITED_TEAM, USER_PROFILE
from fossunited.fossunited.doctype.foss_united_team.foss_united_team import (
    get_role,
    get_staff,
    is_staff,
)
from fossunited.tests.factories import (
    FOSSUnitedTeamFactory,
    UserFactory,
    get_foss_profile_id,
)


class TestFOSSUnitedTeam(FrappeTestCase):
    def setUp(self):
        self.staff_user = UserFactory.create(first_name="Nico", last_name="Robin")
        self.alias_user = UserFactory.create(first_name="Nico", last_name="Robinwork")
        self.volunteer_user = UserFactory.create(first_name="Brook", last_name="Soulking")

        self.staff_profile = get_foss_profile_id(self.staff_user.name)
        self.alias_profile = get_foss_profile_id(self.alias_user.name)
        self.volunteer_profile = get_foss_profile_id(self.volunteer_user.name)

        self.team_row = FOSSUnitedTeamFactory.create(
            foss_user_profile=self.staff_profile,
            other_profile=self.alias_profile,
            org_role="Full-Time",
            joined_on=add_days(nowdate(), -30),
        )

    def tearDown(self):
        frappe.delete_doc(FOSS_UNITED_TEAM, self.team_row.name, force=True)
        for profile in (self.staff_profile, self.alias_profile, self.volunteer_profile):
            frappe.delete_doc(USER_PROFILE, profile, force=True)
        for user in (self.staff_user, self.alias_user, self.volunteer_user):
            frappe.delete_doc("User", user.name, force=True)

    def test_get_staff_includes_primary_and_alias_profile(self):
        staff = get_staff()
        self.assertIn(self.staff_profile, staff)
        self.assertIn(self.alias_profile, staff)

    def test_get_staff_excludes_non_staff_profile(self):
        staff = get_staff()
        self.assertNotIn(self.volunteer_profile, staff)

    def test_is_staff_true_within_tenure(self):
        staff = get_staff()
        self.assertTrue(is_staff(staff, self.staff_profile, nowdate()))
        self.assertTrue(is_staff(staff, self.alias_profile, nowdate()))

    def test_is_staff_false_before_joined_on(self):
        staff = get_staff()
        before_joining = add_days(nowdate(), -60)
        self.assertFalse(is_staff(staff, self.staff_profile, before_joining))

    def test_is_staff_false_after_exited_on(self):
        self.team_row.exited_on = add_days(nowdate(), -1)
        self.team_row.save()

        staff = get_staff()
        self.assertFalse(is_staff(staff, self.staff_profile, nowdate()))
        # but still true for a date while they were still staff
        self.assertTrue(is_staff(staff, self.staff_profile, add_days(nowdate(), -10)))

    def test_is_staff_false_for_unknown_profile(self):
        staff = get_staff()
        self.assertFalse(is_staff(staff, self.volunteer_profile, nowdate()))

    def test_status_derived_from_exited_on(self):
        self.assertEqual(self.team_row.status, "Active")

        self.team_row.exited_on = nowdate()
        self.team_row.save()
        self.assertEqual(self.team_row.status, "Inactive")

    def test_status_manually_set_inactive_without_dates_stays_inactive(self):
        """A row with no joined_on/exited_on at all (e.g. a Volunteer whose
        dates were never tracked) can still be marked Inactive by hand --
        blank exited_on must never force it back to Active."""
        self.team_row.joined_on = None
        self.team_row.status = "Inactive"
        self.team_row.save()
        self.assertEqual(self.team_row.status, "Inactive")

    def test_get_staff_with_profile_arg_fetches_single_person(self):
        staff = get_staff(profile=self.staff_profile)
        self.assertIn(self.staff_profile, staff)
        self.assertIn(self.alias_profile, staff)
        self.assertNotIn(self.volunteer_profile, staff)

    def test_get_role_returns_org_role_within_tenure(self):
        self.assertEqual(get_role(self.staff_profile, nowdate()), "Full-Time")
        # alias profile resolves to the same team row
        self.assertEqual(get_role(self.alias_profile, nowdate()), "Full-Time")

    def test_get_role_none_before_joined_on(self):
        before_joining = add_days(nowdate(), -60)
        self.assertIsNone(get_role(self.staff_profile, before_joining))

    def test_get_role_none_after_exited_on(self):
        self.team_row.exited_on = add_days(nowdate(), -1)
        self.team_row.save()
        self.assertIsNone(get_role(self.staff_profile, nowdate()))

    def test_get_role_none_for_unpaid_role(self):
        founder_row = FOSSUnitedTeamFactory.create(
            foss_user_profile=self.volunteer_profile, org_role="Founder"
        )
        try:
            self.assertIsNone(get_role(self.volunteer_profile, nowdate()))
        finally:
            frappe.delete_doc(FOSS_UNITED_TEAM, founder_row.name, force=True)
