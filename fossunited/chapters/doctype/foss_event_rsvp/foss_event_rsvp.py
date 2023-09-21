# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventRSVP(WebsiteGenerator):
	def before_save(self):
		self.set_route()

	def on_update(self):
		if self.rsvp_count >= self.max_rsvp_count:
			self.is_published = 0
		else:
			self.is_published = 1

	def set_route(self):
		self.route = f"events/{self.event}/rsvp"
