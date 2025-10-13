import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fossunited.id.roles import (
    CHAPTER_MEMBER,
    HACKATHON_ORGANIZER,
    LOCALHOST_ORGANIZER,
    REVIEWER,
    WEBSITE_USER,
)


def before_install():
    click.secho("Creating app roles...", fg="cyan")
    create_custom_roles(get_custom_roles())


def after_install():
    click.secho("Creating custom fields...", fg="cyan")
    create_custom_fields(get_custom_fields(), ignore_validate=True)


def before_uninstall():
    delete_custom_fields(get_custom_fields())


def before_tests():
    click.secho("Setting up tests...", fg="cyan")
    set_default_email_account()


def set_default_email_account():
    if frappe.db.exists("Email Account", {"default_outgoing": 1}):
        return

    if not frappe.db.exists("Email Account", "_Test Email Account 1"):
        frappe.get_doc(
            {
                "doctype": "Email Account",
                "email_account_name": "_Test Email Account 1",
                "email_id": "test@example.com",
                "password": "test",
                "enable_outgoing": 1,
                "smtp_server": "smtp.example.com",
            }
        ).insert()

    email_account = frappe.get_doc("Email Account", "_Test Email Account 1")
    email_account.default_outgoing = 1
    email_account.save()


def delete_custom_fields(custom_fields: dict):
    """
    :param custom_fields: a dict like `{'Salary Slip': [{fieldname: 'loans', ...}]}`
    """
    for doctype, fields in custom_fields.items():
        frappe.db.delete(
            "Custom Field",
            {
                "fieldname": ("in", [field["fieldname"] for field in fields]),
                "dt": doctype,
            },
        )

        frappe.clear_cache(doctype=doctype)


def create_custom_roles(roles):
    for role in roles:
        if frappe.db.exists("Role", {"role_name": role}):
            continue

        role = frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": role,
                "desk_access": False,
            }
        )
        role.insert()


def get_custom_roles():
    """
    FOSSUnited app specific custom roles
    """

    return [
        WEBSITE_USER,
        CHAPTER_MEMBER,
        REVIEWER,
        HACKATHON_ORGANIZER,
        LOCALHOST_ORGANIZER,
    ]


def get_custom_fields():
    """
    FOSSUnited specific custom fields that need to be added to base Frappe doctypes
    """

    return {
        "Email Template": [
            {
                "fieldname": "linked_chapter_section",
                "fieldtype": "Section Break",
                "label": "Linked Chapter Details",
                "insert_after": "response",
            },
            {
                "fieldname": "chapter",
                "fieldtype": "Link",
                "label": "Chapter",
                "options": "FOSS Chapter",
                "insert_after": "linked_chapter_section",
            },
            {
                "fieldname": "event",
                "fieldtype": "Link",
                "label": "Event",
                "options": "FOSS Chapter Event",
                "insert_after": "chapter",
            },
            {
                "fieldname": "document_type",
                "fieldtype": "Link",
                "label": "Document Type",
                "options": "DocType",
                "default": "FOSS Chapter Event",
            },
            {
                "fieldname": "reference_document",
                "fieldtype": "Dynamic Link",
                "label": "Reference Document",
                "options": "document_type",
                "insert_after": "document_type",
            },
        ],
        "Email Group": [
            {
                "fieldname": "linked_chapter_section",
                "fieldtype": "Section Break",
                "label": "Linked Chapter Details",
                "insert_after": "total_subscribers",
            },
            {
                "fieldname": "chapter",
                "fieldtype": "Link",
                "label": "Chapter",
                "options": "FOSS Chapter",
                "insert_after": "linked_chapter_section",
            },
            {
                "fieldname": "event",
                "fieldtype": "Link",
                "label": "Event",
                "options": "FOSS Chapter Event",
                "insert_after": "chapter",
            },
            {
                "fieldname": "group_type",
                "fieldtype": "Select",
                "label": "Group Type",
                "options": "Chapter Event Participants\nChapter CFP Proposers\nEvent Participants\nCFP Proposers\nAccepted Proposers\nRejected Proposers\nOther",  # noqa: E501
                "default": "Other",
                "insert_after": "event",
            },
            {
                "fieldname": "document_type",
                "fieldtype": "Link",
                "label": "Document Type",
                "options": "DocType",
                "default": "FOSS Chapter Event",
            },
            {
                "fieldname": "reference_document",
                "fieldtype": "Dynamic Link",
                "label": "Reference Document",
                "options": "document_type",
                "insert_after": "document_type",
            },
        ],
        "Newsletter": [
            {
                "fieldname": "linked_chapter_section",
                "fieldtype": "Section Break",
                "label": "Linked Chapter Details",
                "insert_after": "send_from",
            },
            {
                "fieldname": "chapter",
                "fieldtype": "Link",
                "label": "Chapter",
                "options": "FOSS Chapter",
                "insert_after": "linked_chapter_section",
            },
            {
                "fieldname": "event",
                "fieldtype": "Link",
                "label": "Event",
                "options": "FOSS Chapter Event",
                "insert_after": "chapter",
            },
            {
                "fieldname": "document_type",
                "fieldtype": "Link",
                "label": "Document Type",
                "options": "DocType",
                "default": "FOSS Chapter Event",
            },
            {
                "fieldname": "reference_document",
                "fieldtype": "Dynamic Link",
                "label": "Reference Document",
                "options": "document_type",
                "insert_after": "document_type",
            },
        ],
    }
