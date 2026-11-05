import frappe

DEFAULT_COVER = "/assets/fossunited/images/defaults/blog-og.png"


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

        blogger_user = (
            frappe.db.get_value("Blogger", self.blogger, "user") if self.blogger else None
        )
        context.author_profile_route = get_profile_route(blogger_user)
        # Blogger avatar is often empty; fall back to the user's profile image
        if context.get("blogger_info") and not context.blogger_info.avatar and blogger_user:
            context.blogger_info.avatar = frappe.db.get_value("User", blogger_user, "user_image")

        # lets templates/includes/comments/comment.html link commenters to their profile
        for comment in context.comment_list:
            comment.profile_route = get_profile_route(comment.comment_email)


def get_profile_route(user):
    if not user:
        return ""
    username = frappe.db.get_value("FOSS User Profile", {"user": user}, "username")
    return f"/u/{username}" if username else ""
