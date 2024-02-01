import frappe


def get_context(self, context):
    context.website_settings = frappe.get_doc(
        "Website Settings"
    ).as_dict()
    context.footer_items = website_settings.get("footer_items")
    context.address = website_settings.get("address")
