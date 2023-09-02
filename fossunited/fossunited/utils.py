from datetime import datetime

from frappe.utils.data import format_datetime


def get_month(date_string, format_string):
	return date_string.strftime(format_string)


def formatted_datetime_with_tz(datetime_string):
	datetime_string = format_datetime(datetime_string, "EEE, d MMM, h:mm a")
	return datetime_string
