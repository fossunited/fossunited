import frappe


@frappe.whitelist()
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
                    "label": "My Hackathons",
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
                        "route": "/chapter",
                    },
                    {
                        "label": "Manage Events",
                        "route": "/events",
                    },
                ],
            }
        )

    if user_is_localhost_organizer():
        sidebar_items[1]["items"].append(
            {
                "label": "Manage Localhost",
                "route": "/localhost",
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
                user,
            ]
        ],
    )


def user_is_localhost_organizer(user: str = frappe.session.user):
    return frappe.db.exists(
        "FOSS Hackathon LocalHost",
        [
            [
                "FOSS Hackathon LocalHost Organizer",
                "user",
                "=",
                user,
            ]
        ],
    )
