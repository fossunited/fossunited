import frappe

from fossunited.doctype_ids import CHAPTER, EVENT, STUDENT_CLUB


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
def get_more_grants(start=0, limit=30):
    grants = frappe.get_all(
        "FOSS Event Grant",
        fields=[
            "event_name",
            "event_start_date",
            "event_location",
            "event_website",
            "grant_amount",
            "custom_amount",
        ],
        filters={"grant_status": "Approved"},
        order_by="event_start_date desc",
        start=int(start),
        page_length=int(limit),
    )

    return {"grants": grants}


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
