import frappe
from fossunited.doctype_ids import EVENT, USER_PROFILE


@frappe.whitelist(allow_guest=True)
def get_event_stats():
    """
    Get statistics about events on the platform.

    Returns:
        dict: Event statistics including total events, upcoming events, etc.
    """
    total_events = frappe.db.count(EVENT)
    published_events = frappe.db.count(EVENT, {"is_published": 1})
    upcoming_events = frappe.db.count(
        EVENT,
        {
            "is_published": 1,
            "status": "Live",
            "event_end_date": [">=", frappe.utils.now()],
        }
    )

    return {
        "total_events": total_events,
        "published_events": published_events,
        "upcoming_events": upcoming_events,
        "past_events": published_events - upcoming_events,
    }


@frappe.whitelist(allow_guest=True)
def get_user_stats():
    """
    Get statistics about users on the platform.

    Returns:
        dict: User statistics
    """
    total_users = frappe.db.count(USER_PROFILE)
    active_users = frappe.db.count(
        USER_PROFILE,
        {"show_activity": 1}
    )

    return {
        "total_users": total_users,
        "active_users": active_users,
    }


@frappe.whitelist(allow_guest=True)
def get_platform_stats():
    """
    Get comprehensive platform statistics.

    Returns:
        dict: Combined platform statistics
    """
    event_stats = get_event_stats()
    user_stats = get_user_stats()

    return {
        "events": event_stats,
        "users": user_stats,
        "last_updated": frappe.utils.now(),
    }