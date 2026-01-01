import json

import frappe

from fossunited.doctype_ids import GRANTS_DIR


def get_context(context):
    docs = frappe.get_all(
        GRANTS_DIR,
        fields=["name", "route", "json_data", "last_updated", "modified", "creation"],
        filters={"is_published": 1},
        order_by="last_updated desc, modified desc",
        limit_page_length=200,
    )

    items = []
    for d in docs:
        try:
            data = json.loads(d.get("json_data") or "{}")
        except json.JSONDecodeError:
            data = {}

        entity = data.get("entity") or {}
        entity_name = entity.get("name") or d.get("name")
        description = (entity.get("description") or "").strip()

        # inline truncation
        short_desc = (description[:150] + "…") if len(description) > 150 else description

        dt_created = d.get("creation")
        # not using last_updated cause we keep it just as ref when we tried to re-fetch
        # we use modified since that indicates there was update in json data somewhere
        dt_updated = d.get("modified")

        projects = data.get("projects") or []
        projects_count = len(projects)

        tags = []
        seen = set()

        for project in projects:
            for tag in project.get("tags") or []:
                if isinstance(tag, str) and tag not in seen:
                    seen.add(tag)
                    tags.append(tag)

        items.append(
            frappe._dict(
                {
                    "name": d.name,
                    "route": d.route,
                    "entity_name": entity_name,
                    "description_short": short_desc,
                    "last_updated_iso": dt_updated.isoformat() if dt_updated else "",
                    "last_updated_fmt": dt_updated.strftime("%d %b %Y"),
                    "tags": tags,
                    "created_iso": dt_created.isoformat() if dt_created else "",
                    "created_fmt": dt_created.strftime("%d %b %Y"),
                    "projects_count": projects_count,
                }
            )
        )

    context.items = items
    context.all_tags = sorted({tag for it in items for tag in it.get("tags", [])})
    context.count = len(items)
    context.page_title = "FOSS Grants & Funding"
    context.no_cache = 1
    return context
