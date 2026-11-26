# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.caching import redis_cache

from fossunited.doctype_ids import FOSS_UNITED_TEAM

# org_roles that are paid staff. Founder/Governing Board/Volunteer are not
STAFF_ROLES = ["Board", "Full-Time", "Part-Time", "Intern", "Fellow"]


class FOSSUnitedTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        designation: DF.Data | None
        exited_on: DF.Date | None
        foss_user_profile: DF.Link | None
        full_name: DF.Data | None
        headshot: DF.AttachImage | None
        joined_on: DF.Date | None
        org_role: DF.Literal[
            "",
            "Founder",
            "Board",
            "Governing Board",
            "Full-Time",
            "Part-Time",
            "Intern",
            "Fellow",
            "Volunteer",
        ]
        other_profile: DF.Link | None
        portfolio_url: DF.Data | None
        status: DF.Literal["Active", "Inactive"]
        user_bio: DF.SmallText | None
        username: DF.Data | None
    # end: auto-generated types

    def validate(self):
        # Only force Inactive when exited_on says so. Never force Active back
        # -- a row with no joined_on/exited_on at all (e.g. a Volunteer whose
        # dates were never tracked) can still be marked Inactive by hand.
        if self.exited_on:
            self.status = "Inactive"


@redis_cache(ttl=2592000)
def get_staff(profile=None):
    """profile_id -> (joined_on, exited_on) for every paid staff member
    (primary + other_profile alias). Pass `profile` to fetch just one person
    (profile page); omit it to prefetch everyone once for a list page
    (chapter, event). Cached -- the team roster barely changes; invalidated
    by clear_staff_cache on any FOSS United Team save/delete."""
    or_filters = {"foss_user_profile": profile, "other_profile": profile} if profile else None
    rows = frappe.get_all(
        FOSS_UNITED_TEAM,
        filters={"org_role": ["in", STAFF_ROLES]},
        or_filters=or_filters,
        fields=["foss_user_profile", "other_profile", "joined_on", "exited_on"],
    )
    staff = {}
    for row in rows:
        dates = (row.joined_on, row.exited_on)
        if row.foss_user_profile:
            staff[row.foss_user_profile] = dates
        if row.other_profile:
            staff[row.other_profile] = dates
    return staff


def is_staff(staff, profile_id, date):
    """Was profile_id staff on this date, per get_staff()'s result?"""
    if profile_id not in staff:
        return False
    joined_on, exited_on = staff[profile_id]
    return is_active(joined_on, exited_on, date)


@redis_cache(ttl=2592000)
def get_role(profile_id, date):
    """This profile's paid org_role (e.g. "Full-Time") on this date, or None
    if they weren't paid staff then. One row lookup -- for a single profile
    page, not a list (use get_staff()/is_staff() for that). Cached, same as
    get_staff()."""
    rows = frappe.get_all(
        FOSS_UNITED_TEAM,
        filters={"org_role": ["in", STAFF_ROLES]},
        or_filters={"foss_user_profile": profile_id, "other_profile": profile_id},
        fields=["org_role", "joined_on", "exited_on"],
    )
    if not rows:
        return None
    row = rows[0]
    if not is_active(row.joined_on, row.exited_on, date):
        return None
    return row.org_role


def is_active(joined_on, exited_on, date):
    """Does a joined_on/exited_on tenure window cover this date? Blank
    joined_on/exited_on means no lower/upper bound."""
    date = frappe.utils.getdate(date)
    if joined_on and frappe.utils.getdate(joined_on) > date:
        return False
    if exited_on and frappe.utils.getdate(exited_on) < date:
        return False
    return True


def clear_staff_cache(doc=None, method=None):
    get_staff.clear_cache()
    get_role.clear_cache()
