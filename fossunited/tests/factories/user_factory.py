from typing import TYPE_CHECKING, Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.doctype_ids import USER_PROFILE

if TYPE_CHECKING:
    from frappe.core.doctype.user.user import User  # noqa: F401

fake = Faker()


def get_foss_profile_id(user: str) -> str | None:
    """Get the FOSS User Profile ID for a given user email."""
    return frappe.db.get_value(USER_PROFILE, {"user": user}, "name")


class UserFactory(BaseFactory["User"]):
    doctype = "User"

    @property
    def default_attributes(self) -> dict[str, Any]:
        email = self.overrides.get("email", fake.email())
        first_name = self.overrides.get("first_name", fake.first_name())
        last_name = self.overrides.get("last_name", fake.last_name())
        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
        }

    @property
    def with_foss_website_user_role(self) -> dict[str, Any]:
        return {
            "roles": [{"role": "FOSS Website User"}],
        }
