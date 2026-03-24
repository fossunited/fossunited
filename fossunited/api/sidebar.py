import frappe


@frappe.whitelist(allow_guest=True)
def get_sidebar_items(user: str = frappe.session.user):
    sidebar_items = [
        {
            "parent_label": "Profile",
            "items": [
                {
                    "label": "Details",
                    "route": "/me",
                    "icon": "user",
                },
                {
                    "label": "My Proposals",
                    "route": "/my-proposals",
                    "icon": "file-text",
                },
            ],
        },
        {
            "parent_label": "Hackathons",
            "items": [
                {
                    "label": "Hackathons",
                    "route": "/my-hackathons",
                    "icon": "zap",
                },
            ],
        },
    ]

    if user_is_chapter_member(user):
        sidebar_items.append(
            {
                "parent_label": "Organizer Dashboard",
                "items": [
                    {
                        "label": "Manage Chapter",
                        "route": "/chapter",
                        "icon": "users",
                    },
                ],
            }
        )

    if user_is_localhost_organizer(user):
        sidebar_items[1]["items"].append(
            {
                "label": "Manage Localhost",
                "route": "/localhost",
                "icon": "map-pin",
            }
        )

    if user_is_cfp_reviewer(user):
        sidebar_items.append(
            {
                "parent_label": "CFP Reviewer",
                "items": [
                    {
                        "label": "Review Proposals",
                        "route": "/review",
                        "icon": "check-square",
                    },
                ],
            }
        )

    return sidebar_items


def user_is_chapter_member(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "Chapter Team Member", "parent": user},
        )
    )


def user_is_localhost_organizer(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "Localhost Organizer", "parent": user},
        )
    )


def user_is_cfp_reviewer(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "CFP Reviewer", "parent": user},
        )
    )
