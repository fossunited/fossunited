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


@frappe.whitelist(allow_guest=True)
def get_hackathon_from_permalink(permalink: str) -> dict:
    """
    Get hackathon details

    Args:
        permalink (str): Permalink of the hackathon

    Returns:
        dict: Hackathon document as a dictionary
    """
    return frappe.get_doc("FOSS Hackathon", {"permalink": permalink})


@frappe.whitelist(allow_guest=True)
def create_participant(hackathon, participant):
    """
    This method is used to create a participant for a hackathon.

    args:
        hackathon(dict): hackathon details
        participant(dict): participant details dict

    return:
        dict: participant doc object
    """

    participant_doc = frappe.get_doc(
        {
            "doctype": "FOSS Hackathon Participant",
            "hackathon": hackathon.get("data").get("name"),
            "user": participant.get("user"),
            "user_profile": participant.get("user_profile"),
            "full_name": participant.get("full_name"),
            "email": participant.get("email"),
            "is_student": participant.get("is_student"),
            "organization": participant.get("organization"),
            "github": participant.get("github"),
            "gitlab": participant.get("gitlab"),
            "wants_to_attend_locally": participant.get(
                "wants_to_attend_locally"
            ),
            "localhost": participant.get("localhost"),
        }
    )
    participant_doc.insert(ignore_permissions=True)

    return participant_doc


@frappe.whitelist(allow_guest=True)
def get_participant(hackathon: str, user: str) -> dict:
    """
    Get participant details

    Args:
        hackathon (str): Hackathon ID
        user (str): User email

    Returns:
        dict: Participant document as a dictionary
    """
    return frappe.get_doc(
        "FOSS Hackathon Participant",
        {"hackathon": hackathon, "user": user},
    )


@frappe.whitelist()
def create_team(hackathon: str, team: dict) -> dict:
    """
    Create a team document

    Args:
        hackathon (str): Hackathon ID
        team (dict): Team details

    Returns:
        dict: Team document as a dictionary
    """
    team_doc = frappe.get_doc(
        {
            "doctype": "FOSS Hackathon Team",
            "team_name": team.get("team_name"),
            "hackathon": hackathon,
            "team_lead": team.get("team_lead"),
            "members": team.get("members"),
        }
    )
    team_doc.insert(ignore_permissions=True)
    return team_doc


@frappe.whitelist()
def get_team_by_member_email(hackathon: str, email: str) -> dict:
    """
    Get team details

    Args:
        hackathon (str): Hackathon ID
        email (str): Email of the team lead

    Returns:
        dict: Team document as a dictionary
    """
    participant = get_participant(hackathon, email)

    try:
        team = frappe.get_doc(
            "FOSS Hackathon Team",
            [
                [
                    "FOSS Hackathon Team Member",
                    "member",
                    "=",
                    participant.get("name"),
                ],
                ["hackathon", "=", hackathon],
            ],
        )
        return team
    except frappe.exceptions.DoesNotExistError:
        frappe.msgprint("Team not found")

    return None


@frappe.whitelist(allow_guest=True)
def create_project(hackathon: str, team: str, project: dict) -> dict:
    """
    Create a project document

    Args:
        hackathon (str): Hackathon ID
        team (str): Team ID
        project (dict): Project details

    Returns:
        dict: Project document as a dictionary
    """
    project_doc = frappe.get_doc(
        {
            "doctype": "FOSS Hackathon Project",
            "hackathon": hackathon,
            "team": team,
            "title": project.get("title"),
            "short_description": project.get("short_description"),
            "description": project.get("description"),
            "repo_link": project.get("repo_link"),
            "demo_link": project.get("demo_link"),
            "is_contribution_project": project.get(
                "is_contribution_project"
            ),
            "is_partner_project": project.get("is_partner_project"),
            "partner_project": project.get("partner_project"),
        }
    )
    project_doc.insert(ignore_permissions=True)
    return project_doc


def get_project_by_team(hackathon: str, team: str) -> dict:
    """
    Get project details

    Args:
        hackathon (str): Hackathon ID
        team (str): Team ID

    Returns:
        dict: Project document as a dictionary
    """
    return frappe.get_doc(
        "FOSS Hackathon Project",
        {"hackathon": hackathon, "team": team},
    )
