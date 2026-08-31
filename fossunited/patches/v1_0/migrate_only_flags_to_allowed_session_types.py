import frappe

from fossunited.doctype_ids import EVENT_CFP

# Mirrors the "no Workshop" filter dashboard/src/helpers/cfp.js used to apply
# for only_talk_proposals, before allowed_session_types replaced both flags.
NON_WORKSHOP_TYPES = "Talk\nLightning Talk\nBirds of Feather(BoF)\nPanel Discussion"


def execute():
    """Backfill allowed_session_types from only_workshops/only_talk_proposals
    before those two Check fields are removed from FOSS Event CFP.

    Must run pre_model_sync: it reads the old columns, which this same
    deploy's schema sync would otherwise drop before this patch gets a chance
    to run.
    """
    cfps = frappe.get_all(
        EVENT_CFP,
        or_filters={"only_workshops": 1, "only_talk_proposals": 1},
        fields=[
            "name",
            "only_workshops",
            "only_talk_proposals",
            "allowed_session_types",
        ],
        page_length=999,
    )

    for cfp in cfps:
        if cfp.allowed_session_types:
            continue

        allowed = "Workshop" if cfp.only_workshops else NON_WORKSHOP_TYPES

        try:
            frappe.db.set_value(
                EVENT_CFP,
                cfp.name,
                "allowed_session_types",
                allowed,
                update_modified=False,
            )
        except Exception:
            frappe.log_error(
                title="migrate_only_flags_to_allowed_session_types:failed",
                message=f"CFP: {cfp.name}\n{frappe.get_traceback()}",
            )
