from datetime import datetime

import frappe
from frappe.utils import format_datetime, format_time


def get_month(date_string, format_string):
	return date_string.strftime(format_string)


def formatted_datetime_with_tz(datetime_string):
	datetime_string = format_datetime(datetime_string, "EEE, d MMM, h:mm a")
	return datetime_string


def format_time_with_zone(time, format_string="%-I:%m %p %Z"):
	return format_time(time, format_string)


@frappe.whitelist()
def update_rsvp_count(rsvp):
	count = frappe.db.count("FOSS Event RSVP Submission", {"linked_rsvp": rsvp})
	frappe.db.set_value("FOSS Event RSVP", rsvp, "rsvp_count", count)


def is_session_user_team_member(chapter):
	members = frappe.get_doc("FOSS Chapter", chapter).chapter_member
	for member in members:
		if member.email == frappe.session.user:
			return True


def get_event_navbar_items(
	chapter, show_speakers, show_rsvp, show_cfp, show_photos, event_schedule
):
	navbar_items = {
		"Event Description": "event-description",
	}
	is_team_member = is_session_user_team_member(chapter)

	if show_speakers or is_team_member:
		navbar_items["Speakers"] = "speakers"

	if show_rsvp or is_team_member:
		navbar_items["RSVP"] = "rsvp"

	if show_cfp or is_team_member:
		navbar_items["CFP"] = "cfp"

	if event_schedule or is_team_member:
		navbar_items["Schedule"] = "schedule"

	if show_photos or is_team_member:
		navbar_items["Photos"] = "photos"

	return navbar_items
