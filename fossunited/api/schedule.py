from datetime import datetime

import frappe


@frappe.whitelist(allow_guest=True)
def get_event_schedule(event_id: str) -> dict:
    """
    Get the schedule for the event

    Args:
        event_id (str): Event ID

    Returns:
        dict: Schedule data
    """

    schedule = frappe.db.get_all("FOSS Event Schedule", {"parent": event_id, "parenttype": "FOSS Chapter Event"}, ["*"], order_by="start_time")

    schedule_by_date = get_schedule_by_date(schedule)

    schedule_by_date_and_hall = {}

    for date, sessions in schedule_by_date.items():
        schedule_by_date_and_hall[date] = get_schedule_by_hall(sessions)

    return schedule_by_date_and_hall


def get_schedule_by_date(schedule: list) -> dict:
    """
    Arrange the schedule in a dict, with keys as dates

    Args:
        schedule (list): List of schedule items

    Returns:
        dict: Schedule arranged by date
    """

    dates = get_event_dates(schedule)

    _schedule = {}
    for session in schedule:
        date = session.get("scheduled_date").strftime("%d/%m/%Y")
        if date not in _schedule:
            _schedule[date] = []

        session.day = dates.index(date) + 1

        _schedule[date].append(session)

    return _schedule


def get_event_dates(schedule: list) -> list:
    """
    Get the list of dates for the event

    Args:
        schedule (list): List of schedule items

    Returns:
        list: List of dates
    """

    dates = []
    for session in schedule:
        date = session.get("scheduled_date")
        if date not in dates:
            dates.append(date)

    dates.sort()
    return [date.strftime("%d/%m/%Y") for date in dates]


def get_schedule_by_hall(schedule: list) -> dict:
    """
    Arrange the schedule in a dict, with keys as halls

    Args:
        schedule (list): List of schedule items

    Returns:
        dict: Schedule arranged by hall
    """

    _schedule = {}
    for session in schedule:
        hall = session.get("hall") or "no-hall"
        if hall not in _schedule:
            _schedule[hall] = []

        _schedule[hall].append(session)

    return _schedule
