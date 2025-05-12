import frappe

from fossunited.doctype_ids import EVENT, EVENT_CFP


@frappe.whitelist(allow_guest=True)
def get_cfp_from_route(route: str) -> dict:
    event = frappe.db.get_value(
        EVENT,
        {"route": f"c/{route}"},
        [
            "route",
            "name",
            "event_name",
            "event_logo",
            "event_location",
            "event_start_date",
            "event_end_date",
        ],
        as_dict=True,
    )

    cfp = frappe.get_doc(EVENT_CFP, {"event": event.name}).as_dict()
    cfp.event = event

    return cfp


@frappe.whitelist(allow_guest=True)
def get_global_cfp_guidelines() -> dict:
    """
    Get the global CFP guidelines.
    """
    return frappe.db.get_value("Global CFP Settings", None, "guidelines", as_dict=True)
