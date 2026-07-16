from typing import Literal

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from fossunited.api.chapter import check_if_chapter_member
from fossunited.doctype_ids import (
    CAMPAIGN,
    CHAPTER,
    CITY_COMMUNITY,
    EMAIL_GROUP,
    EMAIL_MEMBER,
    EVENT,
    HACKATHON,
    HACKATHON_LOCALHOST,
    STUDENT_CLUB,
)
from fossunited.utils.decorators import is_localhost_organizer, require_mailing_access

EMAIL_GROUP_TYPES = Literal[
    "Chapter Event Participants",
    "Chapter CFP Proposers",
    "Event Participants",
    "CFP Proposers",
    "Accepted Proposers",
    "Rejected Proposers",
    "Other",
]

EMAIL_GROUP_SUFFIX_BY_DOCTYPE = {
    CHAPTER: "",
    EVENT: "-Event",
    HACKATHON: "-Hackathon",
    HACKATHON_LOCALHOST: "-Localhost",
}

LISTMONK_MAILING_LIST_UUID = "7ca3f2e2-e5c9-4910-a19f-54d5590ca797"


def create_email_group(
    type: EMAIL_GROUP_TYPES,
    reference_document: str,
    document_type: str = EVENT,
    chapter: str | None = None,
    custom_title: str | None = None,
):
    """
    Ensure an email group exists for the given document.
    Returns the existing group or creates a new one.

    Args:
        type: type of email group
        reference_document: id of the reference document of type document_type
        document_type: type of reference document (default: "FOSS Chapter Event")
        custom_title: custom title to create email group
    """
    try:
        _doc = frappe.get_doc(document_type, reference_document)
        if not chapter:
            chapter = _doc.get("chapter") or _doc.get("name")
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "Error fetching reference document for email group"
        )
        return None

    suffix = EMAIL_GROUP_SUFFIX_BY_DOCTYPE.get(document_type)
    if suffix is None:
        frappe.throw(
            _(f"Unsupported document type: {document_type}"),
            frappe.ValidationError,
        )

    group_title = custom_title if custom_title else f"{type}-{reference_document}{suffix}"

    filters = {
        "reference_document": reference_document,
        "document_type": document_type,
        "group_type": type,
        "title": group_title,
    }
    if chapter:
        filters["chapter"] = chapter

    existing_group = frappe.get_value(EMAIL_GROUP, filters, "name")

    if existing_group:
        return frappe.get_doc(EMAIL_GROUP, existing_group)

    group = frappe.get_doc(
        {
            "doctype": EMAIL_GROUP,
            "title": group_title,
            "chapter": chapter,
            "reference_document": reference_document,
            "document_type": document_type,
            "group_type": type,
        }
    )

    try:
        group.insert(ignore_permissions=True)
        return group
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error while creating email group")
        return None


def add_to_email_group(email_group: str, email: str):
    """
    Add an email to an email group

    Args:
        email_group: id of email group
        email: email to be added to the group
    """
    logger = frappe.logger("email_group")

    if not frappe.db.exists(EMAIL_GROUP, email_group):
        frappe.throw(_("This email group does not exist"), frappe.DoesNotExistError)

    if frappe.db.exists(EMAIL_MEMBER, {"email_group": email_group, "email": email}):
        logger.info(f"Email '{email}' already exists in group '{email_group}'")
        return

    member = frappe.get_doc({"doctype": EMAIL_MEMBER, "email_group": email_group, "email": email})
    member.insert(ignore_permissions=True)
    logger.info(f"Email '{email}' added to group '{email_group}'")


def remove_from_email_group(email_group: str, email: str):
    """
    Remove an email from an email group.
    """
    logger = frappe.logger("email_group")

    if not frappe.db.exists(EMAIL_GROUP, email_group):
        frappe.throw(_("This email group does not exist"), frappe.DoesNotExistError)

    member_name = frappe.db.exists(EMAIL_MEMBER, {"email_group": email_group, "email": email})
    if not member_name:
        logger.info(f"Email '{email}' not found in group '{email_group}', nothing to remove")
        return

    frappe.delete_doc(EMAIL_MEMBER, member_name, ignore_permissions=True)
    logger.info(f"Email '{email}' removed from group '{email_group}'")


def handle_email_group_subscription(
    emails: list[str],
    chapter: str,
    event: str | None = None,
    event_type: str = "Event Participants",
    chapter_type: str = "Chapter Event Participants",
    subscribe_to_chapter: bool = True,
    subscribe_to_event: bool = True,
    document_type_event: str | None = None,
    document_type_chapter: str = CHAPTER,
    custom_group_title: str | None = None,
):
    """
    Sync email(s) to event and/or chapter email groups.

    Args:
        emails (list): List of email addresses to process.
        chapter (str): Chapter name.
        event (str, optional): Event reference.
        event_type (str): Event group type (e.g., "Accepted Participants").
        chapter_type (str): Chapter group type.
        subscribe_to_chapter (bool): Whether to add/remove from chapter group.
        subscribe_to_event (bool): Whether to add/remove from event group.
        document_type_event (str): DocType of the event (e.g. "Event", "Hackathon").
        document_type_chapter (str): DocType of the chapter (default: "Chapter").
    """

    if not emails or not chapter:
        return

    try:
        # Create/get chapter group
        chapter_group = create_email_group(
            type=chapter_type,
            reference_document=chapter,
            document_type=document_type_chapter,
            chapter=chapter,
        )

        if not chapter_group:
            return

        event_group = None
        if event and document_type_event:
            event_group = create_email_group(
                type=event_type,
                reference_document=event,
                document_type=document_type_event,
                chapter=chapter,
                custom_title=custom_group_title,
            )

        for email in emails:
            if not isinstance(email, str) or not email.strip():
                continue

            try:
                # Handle event group subscription
                if event_group:
                    if subscribe_to_event:
                        add_to_email_group(event_group.name, email)
                    else:
                        remove_from_email_group(event_group.name, email)

                # Handle chapter group subscription
                if subscribe_to_chapter:
                    add_to_email_group(chapter_group.name, email)
                else:
                    remove_from_email_group(chapter_group.name, email)

            except frappe.DuplicateEntryError:
                continue

    except Exception:
        frappe.log_error(frappe.get_traceback(), "handle_email_group_subscription failed")


@frappe.whitelist()
def create_newsletter_campaign(
    data: dict,
    reference_document: str | None = None,
    document_type: str = EVENT,
    chapter: str | None = None,
):
    """
    Create a newsletter document linked to the particular event / chapter

    Args:
        data(dict): data to be set in the doctype
        reference_document(str): if of the reference document of type `document_type`
        document_type(str): type of reference document linked. default: 'FOSS Chapter Event'
        chapter(str): id of chapter it is linked to
    """
    _reference_document = reference_document
    _chapter = chapter

    if not _reference_document and not _chapter:
        frappe.throw(_("Either reference_document or chapter need to be provided"))

    if not _chapter:
        # Get Chapter ID
        _chapter = frappe.db.get_value(document_type, _reference_document, ["chapter"])

    check_newsletter_permission(document_type, _reference_document, _chapter)
    chapter_dict = frappe.db.get_value(
        CHAPTER,
        _chapter,
        ["name", "chapter_type", "chapter_name", "email"],
        as_dict=1,
    )

    if chapter_dict.chapter_type == CITY_COMMUNITY:
        chapter_dict.chapter_name = f"FOSS United {chapter_dict.chapter_name}"
    if chapter_dict.chapter_type == STUDENT_CLUB:
        chapter_dict.chapter_name = f"FOSS Club {chapter_dict.chapter_name}"
    if document_type == HACKATHON_LOCALHOST:
        localhost_doc = frappe.db.get_value(
            HACKATHON_LOCALHOST,
            _reference_document,
            ["localhost_name", "email"],
            as_dict=1,
        )

        chapter_dict = {
            "chapter_name": f"LocalHost - {localhost_doc.localhost_name}",
            "email": localhost_doc.email or "fosshack@fossunited.org",
        }

    recipient_groups = get_formatted_email_group(data.get("email_group"))
    attachments = get_formatted_attachment_list(data.get("attachments"))

    newsletter_doc = frappe.get_doc(
        {
            "doctype": "Newsletter",
            "document_type": document_type,
            "reference_document": reference_document,
            "chapter": _chapter,
            "sender_name": chapter_dict["chapter_name"],
            "sender_email": chapter_dict["email"],
            "email_group": recipient_groups,
            "subject": data.get("subject"),
            "content_type": data.get("content_type"),
            "message": data.get("message"),
            "message_md": data.get("message_md"),
            "message_html": data.get("message_html"),
            "attachments": attachments,
        }
    )

    newsletter_doc.insert(ignore_permissions=True)
    newsletter_doc.reload()

    return newsletter_doc


@frappe.whitelist()
def get_newsletter_campaigns(
    reference_document: str | None = None, document_type: str = EVENT, chapter: str | None = None
):
    """
    Get all newsletter / email campaigns specific to an event or a chapter

    Args:
        reference_document: id of the document linked
        document_type: doctype of reference_document. default: FOSS Chapter Event
        chapter: id of the chapter

    Returns:
        list : of all the email campaigns
    """

    check_newsletter_permission(document_type, reference_document, chapter)
    campaigns = frappe.db.get_all(
        doctype=CAMPAIGN,
        filters={
            "reference_document": reference_document,
            "document_type": document_type,
            "chapter": chapter,
        },
        fields=[
            "total_recipients",
            "total_views",
            "email_sent",
            "subject",
            "schedule_sending",
            "schedule_send",
            "name",
            "modified",
        ],
        order_by="modified desc",
        page_length=99,
    )

    for campaign in campaigns:
        status = ""

        if campaign.email_sent:
            status = "Sent"
        elif campaign.schedule_sending:
            status = "Scheduled"
        else:
            status = "Not Sent"

        campaign["status"] = status

    return campaigns


@frappe.whitelist()
@require_mailing_access(campaign_param="id")
def get_campaign_detail(id: str) -> dict:
    """
    Get campaign details and return it as dict

    args:
        id: campaign/newsletter id

    returns:
        dict: with details of the campaign/newsletter
    """

    campaign = frappe.db.get_value(CAMPAIGN, id, ["*"], as_dict=1)

    # transform attachments
    attachments = frappe.db.get_all(
        doctype="Newsletter Attachment",
        filters={"parent": campaign.name},
        page_length=999,
        fields=["*"],
    )
    _attachments = []
    for item in attachments:
        file = frappe.db.get_value(
            "File",
            {
                "file_url": item["attachment"],
            },
            ["*"],
            as_dict=1,
        )
        _attachments.append(file)

    # transform email groups
    email_groups = frappe.db.get_all(
        doctype="Newsletter Email Group",
        filters={
            "parent": campaign.name,
        },
        page_length=999,
        fields=["*"],
    )
    _email_groups = []
    for item in email_groups:
        group = frappe.db.get_value(
            EMAIL_GROUP,
            item.email_group,
            ["*"],
            as_dict=1,
        )
        _email_groups.append(
            {
                "label": group.group_type,
                "value": group.name,
                "description": f"{group.total_subscribers} subscribers",
            }
        )

    campaign["attachments"] = _attachments
    campaign["email_group"] = _email_groups

    return campaign


@frappe.whitelist()
def get_email_groups(
    reference_document: str | None = None,
    document_type: str = EVENT,
    chapter: str | None = None,
) -> list:
    """
    Get email group for a specific event or chapter

    Args:
        reference_document: id of the document linked
        document_type: doctype of reference_document. default: FOSS Chapter Event
        chapter: id of the chapter

    Returns:
        list : of all the emails groups
    """

    email_groups = frappe.db.get_all(
        EMAIL_GROUP,
        {
            "chapter": chapter,
            "reference_document": reference_document,
            "document_type": document_type,
        },
        ["total_subscribers", "group_type", "name"],
    )

    return email_groups


@frappe.whitelist()
@require_mailing_access(campaign_param="campaign_id")
def update_campaign(campaign_id: str, data: dict):
    """
    Update an email campaign with new details(data)

    Args:
        campaign_id: campaign id
        data: updated data
    """

    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    for key, val in data.items():
        if key == "status":
            continue
        if getattr(campaign, key) == val:
            continue
        if key == "attachments":
            campaign.set(key, get_formatted_attachment_list(val))
        elif key == "email_group":
            campaign.set(key, get_formatted_email_group(val))
        else:
            campaign.set(key, val)

    campaign.save(ignore_permissions=True)


def get_formatted_email_group(groups: list) -> list:
    """
    Format the email group coming from frontend to backend compatible version

    oncoming:
    [
        {
            'label': 'Label XYZ',
            'value': 'xyz',
            'description': 'text',
        }
    ]

    format to:
    [
        {
            'email_group': value (from incoming),
        }
    ]

    args:
        groups: list of email groups

    returns:
        list: of formatted email groups
    """
    formatted_groups = []

    for group in groups:
        formatted_groups.append({"email_group": group.get("value")})

    return formatted_groups


def get_formatted_attachment_list(attachments: list) -> list:
    """
    Format a list of attachments coming from frontend to backend compatible version

    oncoming:
    [
        {
            file_name: '...',
            file_url: '...',
            type: '...',
            ...,
        }
    ]

    format to:
    [
        {
            attachment: file_url,
        }
    ]

    args:
        attachments: list of attachments

    returns:
        list: of formatted attachments
    """

    formatted_attachments = []

    for attachment in attachments:
        formatted_attachments.append({"attachment": attachment.get("file_url")})

    return formatted_attachments


@frappe.whitelist()
@require_mailing_access(campaign_param="campaign_id")
def send_campaign(campaign_id: str):
    """
    Send the campaigns

    args:
        campaign: id of campaign / newsletter doctype
    """
    frappe.enqueue_doc(
        CAMPAIGN,
        campaign_id,
        "send_emails",
        queue="long",
        enqueue_after_commit=True,
    )


@frappe.whitelist()
@require_mailing_access(campaign_param="campaign_id")
def send_test_email(campaign_id: str, email: str):
    """
    Send out a test email for a campaign

    args:
        campaign_id : campaign / newsletter id
        email: email to send test email to
    """
    campaign = frappe.get_doc(CAMPAIGN, campaign_id)
    campaign.flags.ignore_permissions = 1
    try:
        campaign.send_test_email(email)
        campaign.save()
    except frappe.InvalidEmailAddressError as e:
        frappe.throw(_(str(e)))


@frappe.whitelist()
@require_mailing_access(campaign_param="campaign_id")
def get_sending_status(campaign_id: str) -> dict:
    """
    Get sending stats related to a campaign

    args:
        campaign_id: id of campaign for which stats are required

    returns:
        dict: of stats of format
        ```
        {
            "sent": int,
            "error": int,
            "total": int,
            "emails_queued": int,
        }
        ```
    """
    campaign = frappe.get_doc(CAMPAIGN, campaign_id)
    campaign.flags.ignore_permissions = 1

    stats = campaign.get_sending_status()

    return stats


# nosemgrep: guest-whitelisted-method
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=2, seconds=60 * 60 * 12)
def listmonk_subscribe(email: str, name: str = ""):
    """
    Subscribe an email to the FOSS United newsletter via Listmonk's public API.
    Failure is logged but never raised — must not block the user action that triggered it.
    """
    import requests

    if not email or not isinstance(email, str):
        return

    listmonk_url = "https://listmonk.fossunited.org"

    try:
        resp = requests.post(
            f"{listmonk_url}/api/public/subscription",
            json={
                "email": email.strip(),
                "name": name.strip() if name else email.strip(),
                "list_uuids": [LISTMONK_MAILING_LIST_UUID],
            },
            timeout=5,
        )
        resp.raise_for_status()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Listmonk newsletter subscription failed")


def check_newsletter_permission(document_type, reference_document, chapter):
    """Check if user has permission to create newsletter"""
    user = frappe.session.user

    # Check if localhost organizer
    if document_type == HACKATHON_LOCALHOST and reference_document:
        if is_localhost_organizer(reference_document, user):
            return

    # Otherwise check chapter membership
    if not chapter:
        frappe.throw(_("Cannot determine chapter for permission check"), frappe.PermissionError)

    if not check_if_chapter_member(chapter, user):
        frappe.throw(
            _("You are not authorized to create newsletters for this chapter"),
            frappe.PermissionError,
        )
