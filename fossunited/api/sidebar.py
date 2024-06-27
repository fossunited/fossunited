import frappe


@frappe.whitelist(allow_guest=True)
def get_sidebar_items():
    sidebar_items = [
        {
            "parent_label": "Profile",
            "items": [
                {
                    "label": "My Profile",
                    "route": "/me",
                }
            ],
        },
        {
            "parent_label": "Hackathons",
            "items": [
                {
                    "label": "Hackathons",
                    "route": "/my-hackathons",
                },
            ],
        },
    ]

    if user_is_chapter_member():
        sidebar_items.append(
            {
                "parent_label": "Organizer Dashboard",
                "items": [
                    {
                        "label": "Manage Chapter",
                        "route": "/chapters",
                    },
                    {
                        "label": "Manage Events",
                        "route": "/events",
                    },
                ],
            }
        )

    return sidebar_items


def user_is_chapter_member(user: str = frappe.session.user):
    return frappe.db.exists(
        "FOSS Chapter",
        [
            [
                "FOSS Chapter Lead Team Member",
                "email",
                "like",
                frappe.session.user,
            ]
        ],
    )
