"""Atom feed of chapter upcoming events, served at rss.xml (template: templates/rss.xml)."""

import frappe
from frappe import _

from fossunited.doctype_ids import CHAPTER
from fossunited.utils.rss import event_entry, feed_context, public_url

no_cache = 1
base_template_path = "www/c/rss.xml"


def get_context(context):
    slug = frappe.form_dict.get("chapter")
    if not slug:
        frappe.throw(_("chapter parameter is required"), frappe.InvalidRequestException)

    try:
        doc = frappe.get_doc(CHAPTER, {"slug": slug})
    except frappe.DoesNotExistError:
        frappe.throw(_("Chapter not found"), frappe.DoesNotExistError)

    feed_path = f"/c/{doc.slug}/rss.xml"
    entries = [
        event_entry(event, doc.chapter_name, f"{public_url(feed_path)}#{event.name}")
        for event in doc.get_upcoming_events()
        if event.is_published
    ]
    return feed_context(
        f"{doc.chapter_name} | Upcoming Events",
        f"Upcoming events from {doc.chapter_name}",
        doc.route or "/",
        feed_path,
        entries,
    )
