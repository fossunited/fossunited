# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class FOSSEventCFP(WebsiteGenerator):
	def before_save(self):
		self.self_route()

	def self_route(self):
		self.route = f"events/{self.event}/cfp"
