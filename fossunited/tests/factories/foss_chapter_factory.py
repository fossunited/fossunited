from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from fossunited.chapters.doctype.foss_chapter.foss_chapter import FOSSChapter
from fossunited.doctype_ids import CHAPTER, CITY_COMMUNITY
from fossunited.tests.factories.user_factory import UserFactory, get_foss_profile_id

fake = Faker()


class FOSSChapterFactory(BaseFactory[FOSSChapter]):
    doctype = CHAPTER

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "chapter_name": self.overrides.get("chapter_name", fake.text(max_nb_chars=40).strip()),
            "chapter_type": self.overrides.get("chapter_type", CITY_COMMUNITY),
            "slug": self.overrides.get("slug", fake.slug().replace("-", "_")),
            "city": self.overrides.get("city", "Bangalore"),
            "state": self.overrides.get("state", "Karnataka"),
            "country": "India",
            "email": self.overrides.get("email", fake.email()),
            "facebook": self.overrides.get("facebook", fake.url()),
            "instagram": self.overrides.get("instagram", fake.url()),
            "linkedin": self.overrides.get("linkedin", fake.url()),
            "mastodon": self.overrides.get("mastodon", fake.url()),
            "matrix": self.overrides.get("matrix", fake.url()),
            "x": self.overrides.get("x", fake.url()),
        }

    @property
    def with_members(self) -> dict[str, Any]:
        members = self.overrides.get(
            "members",
            [user.name for user in UserFactory.create_list(2, "with_foss_website_user_role")],
        )
        chapter_members = []

        for user in members:
            profile_name = get_foss_profile_id(user)
            chapter_members.append(
                {
                    "chapter_member": profile_name,
                    "role": "Core Team Member",
                }
            )

        return {"chapter_members": chapter_members}
