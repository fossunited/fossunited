"""
Permission check decorators for hackathon and chapter operations
"""

from functools import wraps

import frappe

from fossunited.api.chapter import (
    check_if_chapter_member,
    check_if_chapter_or_event_core_member,
    check_if_event_member,
)
from fossunited.doctype_ids import (
    HACKATHON_PARTICIPANT,
    HACKATHON_TEAM,
    LOCALHOST_ORGANIZER,
    USER_PROFILE,
)


def require_hackathon_participant(hackathon_id="hackathon"):
    """
    Decorator to ensure the current user is a participant of the hackathon.

    Args:
        hackathon_id (str): Name of the parameter containing hackathon ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.PermissionError)

            hackathon = kwargs.get(hackathon_id)
            if not hackathon:
                frappe.throw("Hackathon data is required", frappe.ValidationError)

            if not frappe.db.exists(
                HACKATHON_PARTICIPANT,
                {"hackathon": hackathon, "user": frappe.session.user},
            ):
                frappe.throw(
                    "You are not a participant of this hackathon",
                    frappe.PermissionError,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_hackathon_team(team_id="team", hackathon_id="hackathon"):
    """
    Decorator to ensure the current user is a member of the specified team.

    Args:
        team_id (str): Name of the parameter containing team ID
        hackathon_id (str): Name of the parameter containing hackathon ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.PermissionError)

            team = kwargs.get(team_id)
            hackathon = kwargs.get(hackathon_id)

            if not team:
                frappe.throw("Team data is not provided", frappe.ValidationError)

            team_doc = frappe.get_doc(HACKATHON_TEAM, team)

            # Check if hackathon matches if provided
            if hackathon and team_doc.hackathon != hackathon:
                frappe.throw("Team does not belong to this hackathon", frappe.ValidationError)

            # Check if user is a member
            is_member = False
            user_email = frappe.session.user

            for member in team_doc.members:
                if member.email == user_email:
                    is_member = True
                    break

                if member.member:
                    participant_email = frappe.db.get_value(
                        HACKATHON_PARTICIPANT, member.member, "user"
                    )
                    if participant_email == user_email:
                        is_member = True
                        break

            if not is_member:
                frappe.throw("You are not a member of this team", frappe.PermissionError)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_chapter_member(chapter_id="chapter"):
    """
    Decorator to ensure the current user is a member of the chapter.

    Args:
        chapter_id (str): Name of the parameter containing chapter ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.PermissionError)

            chapter = kwargs.get(chapter_id)
            if not chapter:
                frappe.throw("Chapter data is required", frappe.ValidationError)

            if not check_if_chapter_member(chapter, frappe.session.user):
                frappe.throw("You are not a member of this chapter", frappe.PermissionError)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_event_member(event_id="event"):
    """
    Decorator to ensure the current user is an event volunteer.

    Args:
        event_id (str): Name of the parameter containing event ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.PermissionError)

            event = kwargs.get(event_id)
            if not event:
                frappe.throw("Event data is required", frappe.ValidationError)

            if not check_if_event_member(event):
                frappe.throw("You are not an event volunteer", frappe.PermissionError)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_chapter_or_event_member(event_id="event"):
    """
    Simplest decorator - directly wraps existing check function.

    Args:
        event_id (str): Name of the parameter containing event ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.PermissionError)

            event = kwargs.get(event_id)
            if not event:
                frappe.throw("Event ID is not provided", frappe.ValidationError)

            # Reuse existing function directly
            if not check_if_chapter_or_event_core_member(event):
                frappe.throw(
                    "You must be either a chapter member or event member",
                    frappe.PermissionError,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def is_localhost_organizer(localhost_id, user=None):
    """Check if user is a localhost organizer"""
    if not user:
        user = frappe.session.user

    # System Manager bypass
    if "System Manager" in frappe.get_roles(user):
        return True

    # Get user's profile
    profile = frappe.db.get_value(USER_PROFILE, {"user": user}, "name")
    if not profile:
        return False

    # Check if profile exists in localhost organizers
    return frappe.db.exists(
        LOCALHOST_ORGANIZER,
        {
            "parent": localhost_id,
            "parenttype": HACKATHON_LOCALHOST,
            "profile": profile,
            "parentfield": "organizers",
        },
    )


def require_localhost_organizer(localhost_param="localhost_id"):
    """Decorator to check if user is a localhost organizer or system manager"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            localhost_id = kwargs.get(localhost_param)
            if not localhost_id:
                frappe.throw("Localhost ID not provided", frappe.PermissionError)

            if not is_localhost_organizer(localhost_id):
                frappe.throw(
                    "Only localhost organizers can access this resource",
                    frappe.PermissionError,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_mailing_access(campaign_param="campaign_id"):
    """Decorator to check if user has mailing access (chapter member or localhost organizer)"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            campaign_id = kwargs.get(campaign_param)
            if not campaign_id:
                frappe.throw("Campaign ID not provided", frappe.PermissionError)

            user = frappe.session.user
            campaign = frappe.get_doc(CAMPAIGN, campaign_id)

            # Check if localhost organizer
            if campaign.document_type == HACKATHON_LOCALHOST:
                if is_localhost_organizer(campaign.reference_document, user):
                    return func(*args, **kwargs)

            # Otherwise check chapter membership
            chapter = campaign.chapter
            if not chapter:
                chapter = frappe.db.get_value(
                    campaign.document_type,
                    campaign.reference_document,
                    "chapter",
                )

            if not check_if_chapter_member(chapter, user):
                frappe.throw(
                    "You are not authorized organizer to send emails for this campaign",
                    frappe.PermissionError,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
