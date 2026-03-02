import frappe

from fossunited.doctype_ids import CHAPTER, EVENT, HACKATHON, STUDENT_CLUB


@frappe.whitelist(allow_guest=True)
def search_foss_club(query):
    club_list = frappe.get_all(
        CHAPTER,
        fields=[
            "chapter_name",
            "route",
            "city",
        ],
        filters={
            "chapter_type": STUDENT_CLUB,
        },
        or_filters=[
            ["city", "like", "%" + query + "%"],
            ["chapter_name", "like", "%" + query + "%"],
        ],
    )

    return club_list


@frappe.whitelist(allow_guest=True)
def buy_tickets_page(route):
    event = frappe.db.get_value(
        EVENT,
        {"route": route},
        ["name", "is_paid_event"],
        as_dict=True,
    )

    if not event:
        # return a 404 page or fallback
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/404"
        return

    frappe.local.response["type"] = "redirect"

    # redirect based on whether the event is paid
    if event.is_paid_event:
        frappe.local.response["location"] = f"/dashboard/buy-tickets?event={event.name}"
        return

    frappe.local.response["location"] = f"/{route}/rsvp"
    return


@frappe.whitelist(allow_guest=True)
def partner_projects_redirect(hack=None, project=None):
    if not hack:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/404"
        return

    hackathon = frappe.db.get_value(
        HACKATHON,
        {"route": f"hack/{hack}"},
        ["start_date"],
        as_dict=True,
    )

    if not hackathon or not hackathon.start_date:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/404"
        return

    year = hackathon.start_date.year

    project = project or ""

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/fosshack/{year}/partner-projects{project}"
