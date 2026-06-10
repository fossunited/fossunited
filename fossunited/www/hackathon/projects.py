from collections import Counter

import frappe

from fossunited.doctype_ids import HACKATHON, HACKATHON_PROJECT


def get_context(context):
    context.no_cache = 1
    context.hackathon = frappe.get_doc(HACKATHON, {"permalink": frappe.form_dict.permalink})
    context.projects = frappe.get_all(
        HACKATHON_PROJECT,
        {"hackathon": context.hackathon.name, "is_published": 1},
        ["*", "partner_project.project_name as partner_project_name"],
        page_length=9999,
    )

    project_names = [p.name for p in context.projects]

    result_map = {r.project: r.status for r in context.hackathon.results}

    issue_counts = (
        Counter(
            r.parent
            for r in frappe.get_all(
                "Hackathon Project Issue PR",
                filters={"parent": ["in", project_names]},
                fields=["parent"],
            )
        )
        if project_names
        else Counter()
    )

    for project in context.projects:
        project.winner_status = result_map.get(project.name)
        project.issue_pr_count = issue_counts.get(project.name, 0)
