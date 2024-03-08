import frappe


@frappe.whitelist(allow_guest=True)
def search_foss_club(query):
    club_list = frappe.get_all(
        "FOSS Chapter",
        fields=[
            "chapter_name",
            "route",
            "city",
        ],
        filters={
            "chapter_type": "FOSS Club",
        },
        or_filters=[
            ["city", "like", "%" + query + "%"],
            ["chapter_name", "like", "%" + query + "%"],
        ],
    )

    return club_list
