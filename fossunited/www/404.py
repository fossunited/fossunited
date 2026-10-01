import frappe


def get_context(context):
    context.http_status_code = 404
    # Frappe caches rendered 404 HTML under a single shared key ("404") regardless
    # of the requested path (see NotFoundPage in frappe/website). Since our content
    # here depends on the actual path via custom_404_page_context, it must never be
    # cached, or the first 404 rendered gets served for every missing URL after it.
    context.no_cache = 1

    path = frappe.local.request.path.strip("/") if frappe.local.request else ""
    for handler in frappe.get_hooks("custom_404_page_context"):
        result = frappe.get_attr(handler)(path)
        if result:
            context.custom_404 = result
            break
