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
	members = frappe.get_doc("FOSS Chapter", chapter).chapter_members
	for member in members:
		return member.email == frappe.session.user

	return False


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

	return navbar_items


def hide_email(email):

	username, domain = email.split("@")
	username_length = len(username)

	# Calculate the number of characters to hide (5 characters or 50% of the username length, whichever is smaller)
	num_to_hide = min(5, username_length // 2)

	hidden_username = username[:-num_to_hide] + "*" * num_to_hide

	partially_hidden_email = hidden_username + "@" + domain
	return partially_hidden_email


def get_avatar(user):
	person = frappe.db.get_value(
		"FOSS User Profile", {"email": user}, ["profile_photo", "full_name"], as_dict=1
	)

	if person is None:
		return f'<div class="avatar-sm">{get_initials(f"{user}")}</div>'

	if person.profile_photo:
		return f'<img class="grayscale-image profile-image-xs" src="{person.profile_photo}" alt="{person.full_name}">'

	return f'<div class="avatar-sm">{get_initials(person.full_name)}</div>'


def get_initials(name):
	words = name.split(" ")
	initials = ""
	for word in words:
		initials += word[0].upper()

	return initials


def make_badge(text="Default", size="sm"):
	print(size + " " + text)

	# stored in the form of [background-color, text-color]
	colors = {
		"Approved": ["#30A66D", "#FFFFFF"],
		"Open": ["#DB7706", "#FFFFFF"],
		"Review Pending": ["#DB7706", "#FFFFFF"],
		"Rejected": ["#E74C3C", "#FFFFFF"],
		"Cancelled": ["#E74C3C", "#FFFFFF"],
		"Default": ["#171717", "#FFFFFF"],
	}

	if text in colors:
		return f'<span class="badge badge-{size}" style="background-color: {colors[text][0]}; color: {colors[text][1]};">{text}</span>'

	return f'<span class="badge badge-{size}" style="background-color: {colors["Default"][0]}; color: {colors["Default"][1]};">{text}</span>'
