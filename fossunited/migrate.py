import json

import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fossunited.setup import create_custom_roles, get_custom_fields, get_custom_roles


def before_migrate():
    try:
        handle_custom_fields()
        handle_custom_roles()
        ensure_app_priority()
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Before migration failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e


def ensure_app_priority():
    """
    Keep "fossunited" last in the installed-apps order.

    Frappe resolves same-named www/ pages (e.g. 404.html) by walking installed
    apps in reverse install order, first match wins. Frappe Builder ships its
    own www/404.html, and when it's installed after fossunited it silently
    wins, so our custom 404 (and custom_404_page_context hook) never runs.
    Re-asserted on every migrate since a site restore can reset the order.
    """
    installed_apps = frappe.get_installed_apps()
    if "fossunited" not in installed_apps or installed_apps[-1] == "fossunited":
        return

    installed_apps.remove("fossunited")
    installed_apps.append("fossunited")
    frappe.db.set_global("installed_apps", json.dumps(installed_apps))
    click.secho(
        "Re-asserted fossunited as highest-priority app for www page resolution.", fg="cyan"
    )


def handle_custom_fields():
    """
    Get all the required custom fields and add them to the app
    """
    missing_custom_fields = has_custom_fields()
    if not missing_custom_fields:
        click.secho("All custom fields are already added.", fg="blue", bold=True)
        return

    # Add missing custom fields
    click.secho("Adding custom fields...", fg="cyan")
    create_custom_fields(missing_custom_fields, ignore_validate=True)
    click.secho("Custom fields added!", fg="green", bold=True)


def has_custom_fields():
    """
    Check which custom fields from get_custom_fields() are not yet in the database.

    :return: A dictionary of doctype:fields that are missing from the database
    """
    custom_fields = get_custom_fields()
    missing_fields = {}

    for doctype, fields in custom_fields.items():
        # Check each field for this doctype
        doctype_missing_fields = []
        for field in fields:
            # Check if the field already exists in the database
            exists = frappe.db.exists(
                "Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}
            )

            if not exists:
                doctype_missing_fields.append(field)

        # If there are missing fields for this doctype, add to the result
        if doctype_missing_fields:
            missing_fields[doctype] = doctype_missing_fields

    return missing_fields


def handle_custom_roles():
    """
    Get all the required roles and add them to the app
    """
    roles = get_custom_roles()

    click.secho("Adding custom roles...", fg="cyan")
    create_custom_roles(roles)
    click.secho("Custom roles added!", fg="green", bold=True)
