from collections import OrderedDict, defaultdict

import frappe


def get_stack_dict():
    """Active tools, grouped by category (case-insensitive, e.g. "Docs" and "docs" merge)."""
    stacks = frappe.get_all(
        doctype="Stack",
        filters={"status": ["in", ["Active", ""]]},
        fields=["title", "icon", "category", "link", "description", "hosted_url", "status"],
        order_by="title asc",
        page_length=999,
    )

    stack_dict = defaultdict(list)
    labels = {}
    for item in stacks:
        category = (item.category or "").strip() or "Uncategorized"
        key = category.lower()
        labels.setdefault(key, category)
        stack_dict[key].append(item)

    # Alphabetical, with "Uncategorized" pushed to the end
    ordered_keys = sorted(stack_dict, key=lambda key: (key == "uncategorized", key))
    return OrderedDict((labels[key], stack_dict[key]) for key in ordered_keys)


def get_inactive_stack():
    """Not Actively Used / Deprecated tools, flat list (no category grouping)."""
    stacks = frappe.get_all(
        doctype="Stack",
        filters={"status": ["in", ["Not Actively Used", "Deprecated"]]},
        fields=["title", "icon", "link", "description", "hosted_url", "status"],
        order_by="title asc",
        page_length=999,
    )
    return stacks
