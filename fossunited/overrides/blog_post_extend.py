from urllib.parse import quote

import frappe

DEFAULT_COVER = "/files/blog-og.png"


# Mixin via `extend_doctype_class`: frappe puts it before the blog app's BlogPost in the MRO,
# so `website` wins and super().get_context() runs the original.
class BlogPostExtend:
    website = frappe._dict(
        template="fossunited/templates/overrides/blog_post.html",
        condition_field="published",
        page_title_field="title",
    )

    def get_context(self, context):
        super().get_context(context)

        context.cover_image = self.meta_image
        # OG image: cover, else first image in the post (set by the blog app), else the blog default
        context.og_image = frappe.utils.get_url(context.metatags.get("image") or DEFAULT_COVER)

        # Blogger fields come first; the author's published FOSS profile fills the gaps, in one query
        blogger = context.get("blogger_info")
        profile = frappe._dict()
        if blogger and blogger.user:
            profile = (
                frappe.db.get_value(
                    "FOSS User Profile",
                    {"user": blogger.user, "is_published": 1},
                    ["username", "bio", "user.user_image as user_image"],
                    as_dict=True,
                )
                or profile
            )
            blogger.avatar = blogger.avatar or profile.user_image
            blogger.bio = blogger.bio or profile.bio
        context.author_profile_route = f"/u/{profile.username}" if profile.username else ""

        # lets templates/includes/comments/comment.html link commenters to their profile.
        # owner, not comment_email: guests type any email, so only logged-in owners get a link.
        for comment in context.comment_list:
            comment.profile_route = get_profile_route(comment.owner)

    def fetch_social_links_info(self):
        """Share links shown under the post; replaces the blog app's list (same Blog Settings switch)."""
        if not frappe.db.get_single_value("Blog Settings", "enable_social_sharing", cache=True):
            return []
        url = quote(frappe.utils.get_url(self.route), safe="")
        title = quote(self.title, safe="")
        return [
            # Share2Fedi lets the reader pick their own Mastodon instance
            {
                "label": "Mastodon",
                "icon": "brand-mastodon",
                "link": f"https://s2f.kytta.dev/?text={title}%20{url}",
            },
            {
                "label": "Bluesky",
                "icon": "brand-bluesky",
                "link": f"https://bsky.app/intent/compose?text={title}%20{url}",
            },
            {
                "label": "FOSS United Forum",
                "icon": "messages",
                "link": f"https://forum.fossunited.org/new-topic?title={title}&body={url}",
            },
            {
                "label": "X",
                "icon": "brand-x",
                "link": f"https://x.com/intent/post?text={title}&url={url}",
            },
            {
                "label": "LinkedIn",
                "icon": "brand-linkedin",
                "link": f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
            },
            {
                "label": "Telegram",
                "icon": "brand-telegram",
                "link": f"https://t.me/share/url?url={url}&text={title}",
            },
            {
                "label": "WhatsApp",
                "icon": "brand-whatsapp",
                "link": f"https://wa.me/?text={title}%20{url}",
            },
            {
                "label": "Email",
                "icon": "mail",
                "link": f"mailto:?cc=team@fossunited.org&subject={title}&body={url}",
            },
        ]


def get_profile_route(user):
    if not user or user == "Guest":
        return ""
    username = frappe.db.get_value(
        "FOSS User Profile", {"user": user, "is_published": 1}, "username"
    )
    return f"/u/{username}" if username else ""
