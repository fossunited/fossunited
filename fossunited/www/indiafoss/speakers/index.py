from fossunited.fossunited.event_media import (
    get_editions,
    get_indiafoss_media,
    get_indiafoss_years,
    get_session_types,
    get_speakers_index,
)


def get_context(context):
    context.no_cache = 1
    context.hide_nav, context.hide_footer = True, True

    context.speakers = get_speakers_index()["speakers"]
    context.total = len(context.speakers)

    media = get_indiafoss_media()
    context.editions = get_editions(media)
    context.session_types = get_session_types(media)

    context.years = get_indiafoss_years()
    context.current_year = 2026

    context.pagetitle = "IndiaFOSS Speakers"
    context.description = (
        "Every speaker who has taken the stage at IndiaFOSS, the annual FOSS & Digital "
        "Commons Festival by the FOSS United community."
    )
    # context.image = "https://fossunited.org/files/indiafoss-2026-og.png"
