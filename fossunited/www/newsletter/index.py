import frappe


def get_context(context):
    context.newsletters = frappe.get_all(
        "Newsletter",
        filters={"published": 1},
        fields=["name", "subject", "route"],
        order_by="creation desc",
    )
