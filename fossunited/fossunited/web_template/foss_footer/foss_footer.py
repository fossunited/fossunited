import frappe


def get_context(context):
    website_settings = frappe.get_doc("Website Settings").as_dict()

    context.website_settings = website_settings

    context.footer_items = website_settings.get("footer_items")
    context.footer_logo = website_settings.get("footer_logo")

    context.copyright = website_settings.get("copyright")
