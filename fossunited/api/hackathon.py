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
        dict: Project document as a dictionary or None if the team has no project created.
    """

    try:
        return frappe.get_doc(
            "FOSS Hackathon Project",
            {"hackathon": hackathon, "team": team},
        )
    except frappe.DoesNotExistError:
        return None


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
    status: list[str] = [
        "Pending",
        "Accepted",
        "Rejected",
        "Pending Confirmation",
    ],
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
def get_session_user_hackathons():
    """
    Get hackathons for a user
    Args:
        user (str): User email
    Returns:
        list: List of hackathons
    """
    participant_docs = frappe.db.get_all(
        "FOSS Hackathon Participant",
        filters={"user": frappe.session.user},
        fields=["hackathon"],
        page_length=9999,
    )

    hackathons = []
    for participant in participant_docs:
        hackathons.append(get_hackathon(participant.get("hackathon")))

    return hackathons


@frappe.whitelist()
def get_session_user_localhosts():
    """
    Get localhosts managed by the user
    Args:
        user (str): User email
    Returns:
        list: List of localhosts
    """

    profile = frappe.db.get_value(
        "FOSS User Profile", {"user": frappe.session.user}, "name"
    )

    localhosts = frappe.db.get_all(
        "FOSS Hackathon LocalHost",
        filters=[
            [
                "FOSS Hackathon LocalHost Organizer",
                "profile",
                "=",
                profile,
            ]
        ],
        fields=["*"],
        page_length=9999,
    )

    return localhosts


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


@frappe.whitelist()
def delete_project(hackathon: str, team: str):
    """
    Delete team project

    Args:
        hackathon (str): Hackathon ID
        team (str): Team ID
    """
    team_doc = frappe.get_doc("FOSS Hackathon Team", team)
    if frappe.session.user not in [
        member.email for member in team_doc.members
    ]:
        frappe.throw("You are not authorized to delete this project")

    project = get_project_by_team(hackathon, team)

    try:
        frappe.db.set_value(
            "FOSS Hackathon Team", team, "project", None
        )
        frappe.db.delete("FOSS Hackathon Project", project.name)
        return True
    except Exception as e:
        frappe.throw("Error deleting project")


@frappe.whitelist()
def is_valid_hackathon(hackathon_id: str):
    """
    Checks if the the hackathon is valid and exists in the db.

    Returns:
        Boolean True or False
    """
    return bool(frappe.db.exists("FOSS Hackathon", hackathon_id))


@frappe.whitelist()
def is_valid_localhost(localhost_id: str):
    """
    Checks if the localhost is valid and exists in the db.

    Returns:
        Boolean True or False
    """

    return bool(
        frappe.db.exists("FOSS Hackathon LocalHost", localhost_id)
    )


@frappe.whitelist()
def validate_participant_for_localhost(participant_id: str):
    """
    Validates if the participant is valid and exists in the db.
    Also, validates that the participant is valid to make request for localhost.
    """
    if not frappe.db.exists(
        "FOSS Hackathon Participant", participant_id
    ):
        frappe.throw("Participant does not exist")

    participant = frappe.db.get(
        "FOSS Hackathon Participant",
        participant_id,
        [
            "user",
            "wants_to_attend_locally",
            "localhost",
            "localhost_request_status",
        ],
    )
    if participant.user != frappe.session.user:
        frappe.throw("You are not authorized to perform this action")

    if not participant.wants_to_attend_locally:
        frappe.throw("Participant has not opted for local attendance")

    if not participant.localhost:
        frappe.throw("Participant has not selected a localhost")

    if participant.localhost_request_status == "Accepted":
        frappe.throw(
            "Participant has already been accepted for local attendance"
        )

    if (
        not participant.localhost_request_status
        == "Pending Confirmation"
    ):
        frappe.throw(
            "Participant has not been accepted for local attendance"
        )

    return True


@frappe.whitelist()
def validate_user_as_localhost_member(localhost_id: str):
    if not frappe.db.exists(
        "Has Role",
        {
            "parent": frappe.session.user,
            "role": "Localhost Organizer",
        },
    ):
        frappe.throw(
            "You are not a Localhost Organizer. You are not authorized to view this page"
        )

    if not frappe.db.exists(
        "FOSS Hackathon LocalHost Organizer",
        {
            "parent": localhost_id,
            "profile": frappe.db.get_value(
                "FOSS User Profile",
                {"user": frappe.session.user},
                "name",
            ),
        },
    ):
        frappe.throw(
            "You are not a member of this Localhost. You are not authorized to view this page"
        )

    return True


@frappe.whitelist()
def add_pr_issue_to_project(project: str, details: dict) -> None:
    """
    Add a PR/Issue to a project

    Args:
        project (str): Project ID
        details (dict): PR/Issue details
    """
    if not frappe.db.exists("FOSS Hackathon Project", project):
        frappe.throw("Project does not exist")

    issue_pr = frappe.get_doc(
        {
            "doctype": "Hackathon Project Issue PR",
            "parent": project,
            "parenttype": "FOSS Hackathon Project",
            "parentfield": "issue_pr_table",
            "title": details["title"],
            "link": details["link"],
            "type": details["type"],
        }
    )
    issue_pr.insert()


@frappe.whitelist()
def remove_pr_issue_from_project(project: str, issue_pr: str) -> None:
    """
    Remove a PR/Issue from a project

    Args:
        project (str): Project ID
        issue_pr (str): Issue/PR ID
    """
    if not frappe.db.exists("FOSS Hackathon Project", project):
        frappe.throw("Project does not exist")

    if not frappe.db.exists("Hackathon Project Issue PR", issue_pr):
        frappe.throw("Issue/PR does not exist")

    frappe.db.delete("Hackathon Project Issue PR", issue_pr)


@frappe.whitelist()
def get_issue_pr_title(url: str) -> dict:
    """
    Get title of the issue/PR/Discussion from the URL

    Args:
        url (str): URL of the issue/PR/Discussion

    Returns:
        dict: Issue/PR title
    """
    if not "https://github.com" in url:
        frappe.throw("Invalid URL")

    from fossunited.integrations.github import GithubHelper

    gh = GithubHelper()

    parts = url.split("/")
    if len(parts) < 5:
        frappe.throw("Invalid URL")

    if parts[5] == "issues":
        issue = gh.get_issue_info("/".join(parts[3:5]), parts[-1])
        return {"title": issue.title, "type": "Issue"}
    elif parts[5] == "pull":
        pr = gh.get_pr_info("/".join(parts[3:5]), parts[-1])
        return {"title": pr.title, "type": "Pull Request"}
    elif parts[5] == "discussions":
        return {"title": "", "type": "Discussion"}
    else:
        frappe.throw("Invalid URL")
