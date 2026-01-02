import json

import frappe

from fossunited.doctype_ids import GRANTS_DIR


def get_context(context):
    docs = frappe.get_all(
        GRANTS_DIR,
        fields=["name", "route", "json_data", "last_updated", "modified", "creation"],
        filters={"is_published": 1},
        order_by="modified desc",
        limit_page_length=500,
    )

    items = []
    for d in docs:
        try:
            data = json.loads(d.get("json_data") or "{}")
        except json.JSONDecodeError:
            data = {}

        items.append(
            {
                "name": d.name,
                "route": d.route,
                "entity": data.get("entity") or {},
                "projects": data.get("projects") or [],
                "created": d.creation.isoformat() if d.creation else "",
                "modified": d.modified.isoformat() if d.modified else "",
            }
        )

    context.items = items
    context.page_title = "FOSS Grants Directory"
    context.no_cache = 1
    return context
