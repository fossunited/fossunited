from typing import Literal, Optional

import frappe

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


def create_email_group(
    type: EMAIL_GROUP_TYPES,
    reference_document: str,
    document_type: str = EVENT,
    chapter: Optional[str] = None,
):
    """
    Ensure an email group exists for the given document.
    Returns the existing group or creates a new one.

    Args:
        type: type of email group
        reference_document: id of the reference document of type document_type
        document_type: type of reference document (default: "FOSS Chapter Event")
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

    filters = {
        "reference_document": reference_document,
        "document_type": document_type,
        "group_type": type,
    }
    if chapter:
        filters["chapter"] = chapter

    existing_group = frappe.get_value(EMAIL_GROUP, filters, "name")

    if existing_group:
        return frappe.get_doc(EMAIL_GROUP, existing_group)

    suffix = EMAIL_GROUP_SUFFIX_BY_DOCTYPE.get(document_type)
    if suffix is None:
        frappe.throw(
            f"Unsupported document type: {document_type}",
            frappe.ValidationError,
        )

    group_title = f"{type}-{reference_document}{suffix}"

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
    logger = frappe.logger("email_group")  # Logs to logs/email_group.log

    if not frappe.db.exists(EMAIL_GROUP, email_group):
        frappe.throw("This email group does not exist", frappe.DoesNotExistError)

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
        frappe.throw("This email group does not exist", frappe.DoesNotExistError)

    member_name = frappe.db.exists(EMAIL_MEMBER, {"email_group": email_group, "email": email})
    if not member_name:
        logger.info(f"Email '{email}' not found in group '{email_group}', nothing to remove")
        return

    frappe.delete_doc(EMAIL_MEMBER, member_name, ignore_permissions=True)
    logger.info(f"Email '{email}' removed from group '{email_group}'")


def handle_email_group_subscription(
    emails: list[str],
    chapter: str,
    event: Optional[str] = None,
    event_type: str = "Event Participants",
    chapter_type: str = "Chapter Event Participants",
    subscribe_to_chapter: bool = True,
    subscribe_to_event: bool = True,
    document_type_event: Optional[str] = None,
    document_type_chapter: str = CHAPTER,
):
    """
    Sync email(s) to event and/or chapter email groups.

    Always adds to event group. Chapter group is conditional.

    Args:
        emails (list): List of email addresses to process.
        chapter (str): Chapter name.
        event (str, optional): Event reference.
        event_type (str): Event group type.
        chapter_type (str): Chapter group type.
        subscribe_to_chapter (bool): Whether to add/remove from chapter group.
        subscribe_to_event (bool): Whether to add/remove from event group.
        document_type_event (str): DocType of the event (e.g. "Event", "Hackathon").
        document_type_chapter (str): DocType of the chapter (default: "Chapter").
    """

    if not emails or not chapter:
        return

    try:
        # Always create chapter group
        chapter_group = create_email_group(
            type=chapter_type,
            reference_document=chapter,
            document_type=document_type_chapter,
            chapter=chapter,
        )

        if not chapter_group:
            return  # skip silently

        event_group = None
        if event and document_type_event:
            event_group = create_email_group(
                type=event_type,
                reference_document=event,
                document_type=document_type_event,
                chapter=chapter,
            )

        for email in emails:
            if not isinstance(email, str) or not email.strip():
                continue

            try:
                if subscribe_to_event:
                    add_to_email_group(event_group.name, email)
                else:
                    remove_from_email_group(event_group.name, email)

                if subscribe_to_chapter:
                    add_to_email_group(chapter_group.name, email)
                else:
                    remove_from_email_group(chapter_group.name, email)
            except frappe.DuplicateEntryError:
                continue

    except Exception:
        frappe.log_error(frappe.get_traceback(), "sync_email_group_subscription failed")


@frappe.whitelist()
def create_newsletter_campaign(
    data: dict,
    reference_document: str = None,
    document_type: str = EVENT,
    chapter: str = None,
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
        frappe.throw("Either reference_document or chapter need to be provided")

    if not _chapter:
        # Get Chapter ID
        _chapter = frappe.db.get_value(document_type, _reference_document, ["chapter"])

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

    recipient_groups = get_formatted_email_group(data.get("email_group"))
    attachments = get_formatted_attachment_list(data.get("attachments"))

    newsletter_doc = frappe.get_doc(
        {
            "doctype": "Newsletter",
            "document_type": document_type,
            "reference_document": reference_document,
            "chapter": _chapter,
            "sender_name": chapter_dict.chapter_name,
            "sender_email": chapter_dict.email,
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
    reference_document: str = None, document_type: str = EVENT, chapter: str = None
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
    reference_document: str = None,
    document_type: str = EVENT,
    chapter: str = None,
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
def send_campaign(campaign_id: str):
    """
    Send the campaigns

    args:
        campaign: id of campaign / newsletter doctype
    """
    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    if not campaign.chapter:
        chapter = frappe.db.get_value(EVENT, campaign.event, ["chapter"])
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1
    campaign.send_emails()
    campaign.save()


@frappe.whitelist()
def send_test_email(campaign_id: str, email: str):
    """
    Send out a test email for a campaign

    args:
        campaign_id : campaign / newsletter id
        email: email to send test email to
    """

    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    if not campaign.chapter:
        chapter = frappe.db.get_value(
            campaign.document_type,
            campaign.reference_document,
            ["chapter"],
        )
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1
    try:
        campaign.send_test_email(email)
        campaign.save()
    except frappe.InvalidEmailAddressError as e:
        frappe.throw(str(e))


@frappe.whitelist()
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

    if not campaign.chapter:
        chapter = frappe.db.get_value(
            campaign.document_type,
            campaign.reference_document,
            ["chapter"],
        )
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1

    stats = campaign.get_sending_status()

    return stats
