import frappe


def get_context(self, context):
    print("Entering get_context function")
    context.website_settings = frappe.get_doc(
        "Website Settings"
    ).as_dict()

    print(context.website_settings)
    context.footer_items = context.website_settings.get(
        "footer_items"
    )
    context.org_address = context.website_settings.get("address")

    context.copyright = context.website_settings.get("copyright")
