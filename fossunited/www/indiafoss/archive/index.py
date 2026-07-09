from fossunited.fossunited.event_media import (
    get_archive_media,
    get_editions,
    get_indiafoss_years,
    get_session_types,
)


def get_context(context):
    context.no_cache = 1
    # Custom IndiaFOSS header + footer (if_header/if_footer); suppress the site defaults.
    context.hide_nav, context.hide_footer = True, True

    media = get_archive_media()
    context.media = media
    context.total = len(media)
    context.editions = get_editions(media)
    context.session_types = get_session_types(media)

    context.years = get_indiafoss_years()
    context.current_year = 2026

    context.pagetitle = "IndiaFOSS Archive"
    context.description = (
        "Browse every talk from IndiaFOSS, the annual Free and Open Source Software "
        "conference by the FOSS United community."
    )
    context.image = "https://fossunited.org/files/indiafoss-2026-og.png"
