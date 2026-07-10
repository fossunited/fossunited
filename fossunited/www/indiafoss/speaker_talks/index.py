import frappe

from fossunited.fossunited.event_media import get_indiafoss_years, get_speaker_talks


def get_context(context):
    context.no_cache = 1
    context.hide_nav, context.hide_footer = True, True

    slug = frappe.form_dict.slug
    data = get_speaker_talks(slug) if slug else None
    if not data:
        raise frappe.DoesNotExistError

    context.speaker = data["speaker"]
    context.talks = data["talks"]
    context.years = get_indiafoss_years()
    context.current_year = 2026

    context.pagetitle = context.speaker["name"] + " — IndiaFOSS talks"
    context.description = (
        context.speaker["name"]
        + " has spoken at IndiaFOSS. Watch their talks and read the details."
    )
    # context.image = "https://fossunited.org/files/indiafoss-2026-og.png"
