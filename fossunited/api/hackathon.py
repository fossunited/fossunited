"""
APIs used for Hackathon based operations
"""

import frappe


@frappe.whitelist(allow_guest=True)
def get_hackathon(name: str) -> dict:
    """
    Get hackathon details

    Args:
        name (str): ID of the hackathon

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
            "git_profile": participant.get("git_profile"),
            "wants_to_attend_locally": participant.get(
                "wants_to_attend_locally"
            ),
            "localhost": participant.get("localhost"),
        }
    )
    participant_doc.insert(ignore_permissions=True)

    return participant_doc


@frappe.whitelist()
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
        frappe.log("Team not found")

    return None


def get_team_from_participant_id(hackathon: str, id: str) -> dict:
    """
    Get team details

    Args:
        hackathon (str): Hackathon ID
        id (str): Participant ID

    Returns:
        dict: Team document as a dictionary
    """
    try:
        team = frappe.get_doc(
            "FOSS Hackathon Team",
            [
                [
                    "FOSS Hackathon Team Member",
                    "member",
                    "=",
                    id,
                ],
                ["hackathon", "=", hackathon],
            ],
        )
        return team
    except frappe.exceptions.DoesNotExistError:
        frappe.log("Team not found")

    return None


@frappe.whitelist()
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


@frappe.whitelist()
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


@frappe.whitelist()
def get_project_by_email(hackathon: str, email: str):
    """
    Get project details by email

    Args:
        hackathon (str): Hackathon ID
        email (str): Email of the person

    Returns:
        dict: Project document as a dictionary
    """
    team = get_team_by_member_email(hackathon, email)
    return get_project_by_team(hackathon, team.get("name"))


@frappe.whitelist()
def get_localhost_requests_by_team(
    hackathon: str,
    localhost: str,
    status: list[str] = ["Pending", "Accepted", "Rejected"],
):
    """
    Get requests for a particular localhost grouped by team.

    params:
        hackathon(str): hackathon name
        localhost(str): localhost name
        status(list): status of the request

    return:
        dict: requests grouped by team
    """

    requests = frappe.get_all(
        doctype="FOSS Hackathon Participant",
        filters={
            "hackathon": hackathon,
            "wants_to_attend_locally": 1,
            "localhost": localhost,
            "localhost_request_status": ["in", status],
        },
        fields=["*"],
        page_length=99999,
        order_by="creation",
    )

    for request in requests:
        request["profile_route"] = frappe.db.get_value(
            "FOSS User Profile", request.user_profile, "route"
        )
        profile_photo = frappe.db.get_value(
            "FOSS User Profile", request.user_profile, "profile_photo"
        )
        request["profile_photo"] = (
            profile_photo
            if profile_photo
            else "/assets/fossunited/images/defaults/user_profile_image.png"
        )
        request["profile_username"] = frappe.db.get_value(
            "FOSS User Profile", request.user_profile, "username"
        )

    requests_by_team = {}

    for request in requests:
        team = get_team_from_participant_id(
            hackathon, request.get("name")
        )
        if team:
            project = get_project_by_team(hackathon, team.name)
            if project:
                request["project_title"] = project.title
                request["project_route"] = project.route
            if not team.name in requests_by_team:
                requests_by_team[team.name] = []
            request["team"] = team
            requests_by_team[team.name].append(request)
        else:
            request["team"] = {"team_name": "Individual Participants"}
            if not "Individual Participants" in requests_by_team:
                requests_by_team["Individual Participants"] = []
            requests_by_team["Individual Participants"].append(
                request
            )

    return requests_by_team or None


@frappe.whitelist()
def join_team_via_code(team_code: str, user: str):
    """
    Join a team using a team code

    Args:
        code (str): Team code
        user (str): User email

    Returns:
        dict: Team document as a dictionary
    """
    try:
        team = frappe.get_doc("FOSS Hackathon Team", team_code)
    except frappe.exceptions.DoesNotExistError:
        frappe.throw("Team not found")
        return "Invalid Code. Team with this code does not exist."

    participant = get_participant(team.hackathon, user)
    if not participant:
        frappe.throw("Participant not found")
        return "Participant not found."

    team.append("members", {"member": participant.name})
    team.save()


@frappe.whitelist()
def get_session_participant(hackathon: str) -> dict:
    """
    Get participant details of the current session user

    Args:
        hackathon (str): Hackathon ID

    Returns:
        dict: Participant document as a dictionary
    """
    participant = frappe.db.get_value(
        "FOSS Hackathon Participant",
        {"hackathon": hackathon, "user": frappe.session.user},
        [
            "name",
            "user_profile",
            "full_name",
            "email",
            "is_student",
            "git_profile",
            "organization",
            "hackathon",
            "wants_to_attend_locally",
            "localhost",
            "localhost_request_status",
        ],
        as_dict=1,
    )
    return participant
