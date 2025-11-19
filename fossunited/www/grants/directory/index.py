import json

import frappe

from fossunited.doctype_ids import GRANTS_DIR


def get_context(context):
    docs = frappe.get_all(
        GRANTS_DIR,
        fields=["name", "route", "json_data", "last_updated", "modified"],
        filters={"is_published": 1},
        order_by="last_updated desc, modified desc",
        limit_page_length=200,
    )

    items = []
    for d in docs:
        try:
            data = json.loads(d.get("json_data") or "{}")
        except Exception:
            data = {}

        entity = data.get("entity") or {}
        entity_name = entity.get("name") or d.get("name")
        description = (entity.get("description") or "").strip()

        # inline truncation
        short_desc = (description[:150] + "…") if len(description) > 150 else description

        # inline date formatting (converted to datetime by frappe)
        dt = d.get("last_updated") or d.get("modified")
        dt_fmt = dt.strftime("%d %b %Y") if dt else ""

        items.append(
            frappe._dict(
                {
                    "name": d.name,
                    "route": d.route,
                    "entity_name": entity_name,
                    "description_short": short_desc,
                    "last_updated_iso": dt,
                    "last_updated_fmt": dt_fmt,
                }
            )
        )

    context.items = items
    context.count = len(items)
    context.page_title = "FOSS Grants & Funding"
    return context
