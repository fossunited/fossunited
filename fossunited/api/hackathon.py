"""
APIs used for Hackathon based operations
"""

import frappe


@frappe.whitelist(allow_guest=True)
def get_hackathon(name: str) -> dict:
    """
    Get hackathon details

    Args:
        name (str): Name of the hackathon

    Returns:
        dict: Hackathon document as a dictionary
    """
    return frappe.get_doc("FOSS Hackathon", name)


@frappe.whitelist()
def register_for_hackathon(hackathon, team, project):
    """
    This method is used for registering a team for a hackathon.
    It creates a team and project document and links them together.

    Args:
        hackathon (dict): Hackathon details
        team (dict): Team details
        project (dict): Project details

    Returns:
        dict: Returns a dictionary with team_doc and project_doc
    """

    team_doc = create_team(hackathon, team)

    # If team is working on a partner project, then no need to create a project
    if (
        team_doc.working_on_partner_project
        and team_doc.partner_project != ""
    ):
        return {"team_doc": team_doc, "project_doc": None}

    # If team is not working on a partner project, then create a project
    if not team_doc.working_on_partner_project:
        project_doc = create_project(hackathon, team_doc, project)
        print(project_doc)
        team_doc.reload()
        team_doc.project = project_doc.name
        team_doc.save(ignore_permissions=True)

    return {"team_doc": team_doc, "project_doc": project_doc}


def create_team(hackathon, team):
    """
    Create a team document

    Args:
        hackathon (dict): Hackathon details
        team (dict): Team details

    Returns:
        FOSS Hackathon Team: Returns the created team document
    """

    team_doc = frappe.get_doc(
        {
            "doctype": "FOSS Hackathon Team",
            "team_name": team.get("team_name"),
            "hackathon": hackathon.get("data").get("name"),
            "working_on_partner_project": team.get(
                "working_on_partner_project"
            ),
            "partner_project": team.get("partner_project"),
            "wants_to_attend_locally": team.get(
                "wants_to_attend_locally"
            ),
            "localhost": team.get("localhost"),
        }
    )
    team_doc.insert(ignore_permissions=True)
    return team_doc


def create_project(hackathon, team, project):
    """
    Create a project document

    Args:
        hackathon (dict): Hackathon details
        team (dict): Team details
        project (dict): Project details

    Returns:
        FOSS Hackathon Project: Returns the created project document
    """

    project_doc = frappe.get_doc(
        {
            "doctype": "FOSS Hackathon Project",
            "title": project.get("title"),
            "team": team.get("name"),
            "hackathon": hackathon.get("data").get("name"),
            "description": project.get("description"),
            "repo_link": project.get("repo_link"),
            "short_description": project.get("short_description"),
        }
    )
    project_doc.insert(ignore_permissions=True)
    return project_doc
