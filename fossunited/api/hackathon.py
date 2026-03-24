"""
APIs used for Hackathon based operations
"""

import frappe
from frappe.rate_limiter import rate_limit

from fossunited.doctype_ids import (
    EVENT_CHECKIN,
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    HACKATHON_PROJECT,
    HACKATHON_TEAM,
    HACKATHON_TEAM_MEMBER,
    LOCALHOST_ORGANIZER,
    USER_PROFILE,
)
from fossunited.integrations.github import GithubHelper
from fossunited.utils.decorators import (
    require_hackathon_participant,
    require_hackathon_team,
    require_localhost_organizer,
)


@frappe.whitelist(allow_guest=True)
def get_hackathon(name: str) -> dict:
    """
    Get hackathon details

    Args:
        name (str): ID of the hackathon

    Returns:
        dict: Hackathon document as a dictionary
    """
    return frappe.get_doc(HACKATHON, name)


@frappe.whitelist(allow_guest=True)
def get_hackathon_from_permalink(permalink: str) -> dict:
    """
    Get hackathon details

    Args:
        permalink (str): Permalink of the hackathon

    Returns:
        dict: Hackathon document as a dictionary
    """
    return frappe.get_doc(HACKATHON, {"permalink": permalink})


@frappe.whitelist()
def create_participant(hackathon: dict, participant: dict) -> dict:
    """
    This method is used to create a participant for a hackathon.

    args:
        hackathon(dict): hackathon details
        participant(dict): participant details dict

    return:
        dict: participant doc object
    """
    current_user = frappe.session.user
    if current_user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)

    hackathon_name = hackathon.get("data", {}).get("name")
    if not hackathon_name:
        frappe.throw("Invalid hackathon")

    if frappe.db.exists(
        HACKATHON_PARTICIPANT, {"hackathon": hackathon_name, "user": current_user}
    ):
        frappe.throw("You have already registered for this hackathon")

    user_profile_data = frappe.db.get_value(
        USER_PROFILE,
        {"user": current_user},
        ["name", "full_name"],
        as_dict=True,
    )

    participant_doc = frappe.get_doc(
        {
            "doctype": HACKATHON_PARTICIPANT,
            "hackathon": hackathon_name,
            "user": current_user,
            "user_profile": user_profile_data.get("name"),
            "full_name": participant.get("full_name") or (user_profile_data.get("full_name")),
            "email": current_user,
            "is_student": participant.get("is_student", 0),
            "organization": participant.get("organization", ""),
            "git_profile": participant.get("git_profile", ""),
            "wants_to_attend_locally": participant.get("wants_to_attend_locally", 0),
            "localhost": participant.get("localhost", ""),
            "subscribe_chapter_mailing": 1,
        }
    )
    participant_doc.insert(ignore_permissions=True)

    return participant_doc


@frappe.whitelist()
def get_participant(hackathon: str) -> dict:
    """
    Get participant details

    Args:
        hackathon (str): Hackathon ID

    Returns:
        dict: Participant document as a dictionary
    """
    return frappe.get_doc(
        HACKATHON_PARTICIPANT,
        {"hackathon": hackathon, "user": frappe.session.user},
    )


@frappe.whitelist()
@require_hackathon_participant(hackathon_id="hackathon")
@rate_limit(limit=5, seconds=60 * 60)
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
            "doctype": HACKATHON_TEAM,
            "team_name": team.get("team_name"),
            "hackathon": hackathon,
            "members": team.get("members", []),
        }
    )
    team_doc.insert()
    return team_doc


@frappe.whitelist()
def get_team_by_member_email(hackathon: str) -> dict:
    """
    Get team details

    Args:
        hackathon (str): Hackathon ID
        email (str): Email of the team lead

    Returns:
        dict: Team document as a dictionary
    """
    participant = get_participant(hackathon)

    try:
        team = frappe.get_doc(
            HACKATHON_TEAM,
            [
                [
                    HACKATHON_TEAM_MEMBER,
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
            HACKATHON_TEAM,
            [
                [
                    HACKATHON_TEAM_MEMBER,
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
@require_hackathon_team(team_id="team", hackathon_id="hackathon")
@rate_limit(limit=5, seconds=60 * 60)
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
            "doctype": HACKATHON_PROJECT,
            "hackathon": hackathon,
            "team": team,
            "title": project.get("title"),
            "short_description": project.get("short_description"),
            "description": project.get("description"),
            "repo_link": project.get("repo_link"),
            "demo_link": project.get("demo_link"),
            "is_contribution_project": project.get("is_contribution_project"),
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
            HACKATHON_PROJECT,
            {"hackathon": hackathon, "team": team},
        )
    except frappe.DoesNotExistError:
        return None


@frappe.whitelist()
def get_project_by_email(hackathon: str):
    """
    Get project details by email

    Args:
        hackathon (str): Hackathon ID

    Returns:
        dict: Project document as a dictionary
    """
    team = get_team_by_member_email(hackathon)
    if not team:
        return None
    return get_project_by_team(hackathon, team.get("name"))


@frappe.whitelist()
@require_localhost_organizer(localhost_param="localhost")
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
    Get requests for a particular localhost with team and project info.
    Returns a flat list.
    """
    requests = frappe.get_all(
        doctype=HACKATHON_PARTICIPANT,
        filters={
            "hackathon": hackathon,
            "localhost": localhost,
            "localhost_request_status": ["in", status],
        },
        fields=[
            "name",
            "email",
            "full_name",
            "hackathon",
            "user_profile",
            "is_student",
            "organization",
            "git_profile",
            "wants_to_attend_locally",
            "localhost",
            "localhost_request_status",
        ],
        page_length=99999,
        order_by="creation",
    )

    # Enrich each request with profile, team, and project data
    for request in requests:
        # Profile data
        if request.user_profile:
            profile = (
                frappe.db.get_value(
                    USER_PROFILE,
                    request.user_profile,
                    ["route", "profile_photo", "username"],
                    as_dict=True,
                )
                or {}
            )
            request["profile_route"] = profile.get("route")
            request["profile_photo"] = (
                profile.get("profile_photo")
                or "/assets/fossunited/images/defaults/user_profile_image.png"
            )
            request["profile_username"] = profile.get("username")
        else:
            request["profile_route"] = None
            request["profile_photo"] = "/assets/fossunited/images/defaults/user_profile_image.png"
            request["profile_username"] = None

        # Team data
        team = get_team_from_participant_id(hackathon, request.get("name"))
        if team:
            request["team_id"] = team.name
            request["team_name"] = team.team_name

            # Project data
            project = get_project_by_team(hackathon, team.name)
            if project:
                request["project_title"] = project.title
                request["project_route"] = project.route
            else:
                request["project_title"] = None
                request["project_route"] = None
        else:
            request["team_id"] = "individual"
            request["team_name"] = "Individual Participants"
            request["project_title"] = None
            request["project_route"] = None

    return requests


@frappe.whitelist()
@require_hackathon_participant(hackathon_id="hackathon")
@rate_limit(limit=5, seconds=60 * 60)
def join_team_via_code(team_code: str, hackathon: str):
    """
    Join a team - validation happens in controller.
    """
    current_user = frappe.session.user

    team = frappe.get_doc(HACKATHON_TEAM, team_code)

    # Verify team belongs to hackathon
    if team.hackathon != hackathon:
        frappe.throw("Team does not belong to this hackathon")

    participant = frappe.get_doc(
        HACKATHON_PARTICIPANT, {"hackathon": hackathon, "user": current_user}
    )

    # Add member - controller will validate everything
    team.append("members", {"member": participant.name})
    team.save(ignore_permissions=True)

    return team


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
        HACKATHON_PARTICIPANT,
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

    profile = frappe.db.get_value(USER_PROFILE, {"user": frappe.session.user}, "name")

    localhosts = frappe.db.get_all(
        HACKATHON_LOCALHOST,
        filters=[
            [
                LOCALHOST_ORGANIZER,
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
        HACKATHON_PARTICIPANT,
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
@require_hackathon_team(team_id="team", hackathon_id="hackathon")
def delete_project(hackathon: str, team: str):
    """
    Delete team project

    Args:
        hackathon (str): Hackathon ID
        team (str): Team ID
    """
    project = frappe.get_doc(HACKATHON_PROJECT, {"hackathon": hackathon, "team": team})
    frappe.db.set_value(HACKATHON_TEAM, team, "project", None)
    project.delete()  # controller has_permission checks authorization
    return True


@frappe.whitelist()
def is_valid_hackathon(hackathon_id: str):
    """
    Checks if the the hackathon is valid and exists in the db.

    Returns:
        Boolean True or False
    """
    return bool(frappe.db.exists(HACKATHON, hackathon_id))


@frappe.whitelist()
def is_valid_localhost(localhost_id: str):
    """
    Checks if the localhost is valid and exists in the db.

    Returns:
        Boolean True or False
    """

    return bool(frappe.db.exists(HACKATHON_LOCALHOST, localhost_id))


@frappe.whitelist()
def validate_participant_for_localhost(participant_id: str):
    """
    Validates if the participant is valid and exists in the db.
    Also, validates that the participant is valid to make request for localhost.
    """
    if not frappe.db.exists(HACKATHON_PARTICIPANT, participant_id):
        frappe.throw("Participant does not exist")

    participant = frappe.db.get(
        HACKATHON_PARTICIPANT,
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
        frappe.throw("Participant has already been accepted for local attendance")

    if not participant.localhost_request_status == "Pending Confirmation":
        frappe.throw("Participant has not been accepted for local attendance")

    return True


@frappe.whitelist()
def get_issue_pr_title(url: str) -> dict:
    """
    Get title of the issue/PR/Discussion from the URL

    Args:
        url (str): URL of the issue/PR/Discussion

    Returns:
        dict: Issue/PR title
    """
    if "https://github.com" not in url:
        frappe.throw("Not a Github URL.")

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


@frappe.whitelist()
def get_count_team_members_and_max_count(hackathon: str, team: str):
    """
    Get count of team members and maximum count of team members allowed

    Args:
        hackathon (str): Hackathon ID
        team (str): Team ID

    Returns:
        dict: Team members count and maximum count
    """

    max_team_size = frappe.db.get_value(HACKATHON, hackathon, "max_team_members")
    team_members_count = len(frappe.get_doc(HACKATHON_TEAM, team).members)
    return {"team_members_count": team_members_count, "max_team_size": max_team_size}


@frappe.whitelist()
@require_localhost_organizer(localhost_param="localhost_id")
def get_localhost_checkins(localhost_id: str):
    """Get all check-ins for a localhost"""
    from frappe.query_builder import DocType, Order

    Participant = DocType(HACKATHON_PARTICIPANT)
    CheckIn = DocType(EVENT_CHECKIN)

    checkins = (
        frappe.qb.from_(CheckIn)
        .join(Participant)
        .on(CheckIn.parent == Participant.name)
        .select(
            Participant.full_name,
            Participant.email,
            Participant.organization,
            Participant.is_student,
            CheckIn.check_in_time,
            CheckIn.parent,
        )
        .where(Participant.localhost == localhost_id)
        .where(CheckIn.parenttype == HACKATHON_PARTICIPANT)
        .where(CheckIn.parentfield == "check_ins")
        .orderby(CheckIn.check_in_time, order=Order.desc)
        .run(as_dict=True)
    )

    return checkins


@frappe.whitelist()
@require_localhost_organizer(localhost_param="localhost_id")
def get_localhost_checkin_stats(localhost_id: str):
    """Get localhost statistics"""
    total_accepted = frappe.db.count(
        HACKATHON_PARTICIPANT,
        filters={"localhost": localhost_id, "localhost_request_status": "Accepted"},
    )

    return {"total_accepted": total_accepted}


@frappe.whitelist()
def check_participant_disqualification(hackathon_permalink: str):
    """
    Check if current user is disqualified from a hackathon.

    Returns:
        dict: {
            'is_disqualified': bool,
            'hackathon_name': str,
            'rules': str (HTML/markdown),
        }
    """
    user = frappe.session.user
    hackathon = frappe.db.get_value(
        HACKATHON,
        {"permalink": hackathon_permalink},
        ["name", "hackathon_name", "hackathon_rules"],
        as_dict=True,
    )

    if not hackathon:
        frappe.throw(frappe._("Hackathon not found"))

    participant = frappe.db.get_value(
        HACKATHON_PARTICIPANT,
        {"hackathon": hackathon.name, "user": user},
        ["disqualified", "name"],
        as_dict=True,
    )

    if not participant:
        return {"is_disqualified": False, "registered": False}

    return {
        "is_disqualified": bool(participant.disqualified),
        "registered": True,
        "hackathon_name": hackathon.hackathon_name,
        "rules": hackathon.hackathon_rules or "",
    }
