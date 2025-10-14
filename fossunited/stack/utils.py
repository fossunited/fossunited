from collections import OrderedDict, defaultdict

import frappe


def get_stack_dict():
    stacks = frappe.get_all(
        doctype="Stack", fields=["title", "icon", "category", "link"], page_length=999
    )

    # Group items by category
    stack_dict = defaultdict(list)
    for item in stacks:
        stack_dict[item.category].append(item)

    # Sort categories alphabetically (case-insensitive), with "Past Utilities" at the end
    sorted_categories = sorted(
        [cat for cat in stack_dict if cat.lower() != "past utilities"],
        key=lambda x: x.lower(),
    )
    if "Past Utilities" in stack_dict:
        sorted_categories.append("Past Utilities")

    # Create an OrderedDict to maintain sorted order
    sorted_stack_dict = OrderedDict()

    for category in sorted_categories:
        # Sort items in each category by title (case-insensitive)
        sorted_items = sorted(stack_dict[category], key=lambda x: x.title.lower())
        sorted_stack_dict[category] = sorted_items

    return sorted_stack_dict
