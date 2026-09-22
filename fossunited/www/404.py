import frappe


def get_context(context):
    context.http_status_code = 404

    path = frappe.local.request.path.strip("/") if frappe.local.request else ""
    for handler in frappe.get_hooks("custom_404_page_context"):
        result = frappe.get_attr(handler)(path)
        if result:
            context.custom_404 = result
            break
