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

            if not check_if_chapter_member(chapter_id, frappe.session.user):
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

            if not check_if_event_member(event_id):
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
