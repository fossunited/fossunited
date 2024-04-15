import frappe


def get_context(context):
    context.no_cache = 1
    events = frappe.get_all(
        "FOSS Chapter Event",
        fields=[
            "event_name",
            "chapter",
            "banner_image",
            "route",
            "must_attend",
            "event_location",
            "map_link",
            "event_start_date",
            "banner_image",
        ],
        filters={"status": "Approved", "is_published": 1},
        order_by="event_start_date",
    )

    context.events = events
    context.current_date = frappe.utils.getdate(
        frappe.utils.nowdate()
    )

    (
        context.upcoming_months_list,
        context.past_months_list,
    ) = get_month_list(events, context.current_date)


def get_month_list(events, current_date):
    upcoming_months_list = []
    past_months_list = []

    for event in events:
        if (
            frappe.utils.getdate(event.event_start_date)
            >= current_date
            and frappe.utils.formatdate(
                event.event_start_date, "MMMM yyyy"
            )
            not in upcoming_months_list
        ):
            upcoming_months_list.append(
                frappe.utils.formatdate(
                    event.event_start_date, "MMMM yyyy"
                )
            )

    for event in events:
        if (
            frappe.utils.getdate(event.event_start_date)
            < current_date
            and frappe.utils.formatdate(
                event.event_start_date, "MMMM yyyy"
            )
            not in past_months_list
        ):
            past_months_list.append(
                frappe.utils.formatdate(
                    event.event_start_date, "MMMM yyyy"
                )
            )

    return upcoming_months_list, past_months_list
