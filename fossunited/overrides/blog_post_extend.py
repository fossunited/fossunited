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


def get_profile_route(user):
    if not user:
        return ""
    username = frappe.db.get_value(
        "FOSS User Profile", {"user": user, "is_published": 1}, "username"
    )
    return f"/u/{username}" if username else ""
