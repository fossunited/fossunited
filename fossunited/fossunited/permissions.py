import frappe
from frappe import _

from fossunited.api.chapter import is_chapter_member, is_event_member
from fossunited.doctype_ids import EVENT, EVENT_CFP, EVENT_RSVP

# Permission types that change a record. Read-type checks are left to the role permissions,
# so public pages, lists and dashboard reads are unaffected.
MANAGE_PTYPES = frozenset({"write", "create", "delete", "submit", "cancel", "amend"})


def _ctm_chapters(user: str) -> list[str]:
    """Return list of FOSS Chapter names where user is a Chapter Lead Team Member."""
    profile = frappe.db.get_value("FOSS User Profile", {"user": user}, "name")
    if not profile:
        return []
    return frappe.db.get_all(
        "FOSS Chapter Lead Team Member",
        filters={"chapter_member": profile, "parenttype": "FOSS Chapter"},
        pluck="parent",
    )


def cfp_submission_query(user: str) -> str:
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "CFP Reviewer" in roles:
        return ""

    escaped_user = frappe.db.escape(user)
    own = f"`tabFOSS Event CFP Submission`.submitted_by = {escaped_user}"

    chapters = _ctm_chapters(user)
    if not chapters:
        return own

    escaped_chapters = ", ".join(frappe.db.escape(c) for c in chapters)
    return f"`tabFOSS Event CFP Submission`.chapter IN ({escaped_chapters}) OR {own}"


def _chapter_in_query(table: str, user: str) -> str:
    chapters = _ctm_chapters(user)
    if not chapters:
        return "1=0"
    escaped_chapters = ", ".join(frappe.db.escape(c) for c in chapters)
    return f"`tab{table}`.chapter IN ({escaped_chapters})"


def rsvp_submission_query(user: str) -> str:
    if not user:
        user = frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""
    return _chapter_in_query("FOSS Event RSVP Submission", user)


def _is_privileged(user: str) -> bool:
    return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def _is_new(doc, ptype: str | None) -> bool:
    return ptype == "create" or bool(doc.get("__islocal")) or not doc.get("name")


def _can_manage_event(event: str | None, user: str) -> bool:
    if not event:
        return False
    chapter = frappe.db.get_value(EVENT, event, "chapter")
    return is_chapter_member(chapter, user) or is_event_member(event, user)


def _may_move_event(stored: str | None, new: str | None, user: str) -> bool:
    """Moving an event to another chapter needs membership of both chapters."""
    stored, new = stored or None, new or None
    return new == stored or (
        is_chapter_member(stored, user) and (new is None or is_chapter_member(new, user))
    )


def _may_move_form(stored: str | None, new: str | None, user: str) -> bool:
    """Moving an RSVP or CFP form to another event needs access to both events."""
    stored, new = stored or None, new or None
    return new == stored or (_can_manage_event(stored, user) and _can_manage_event(new, user))


# The field that places each record in a chapter or event, and the rule for changing it.
MOVE_RULES = {
    EVENT: ("chapter", _may_move_event),
    EVENT_RSVP: ("event", _may_move_form),
    EVENT_CFP: ("event", _may_move_form),
}


def _rows_belong_to(doc) -> bool:
    """False if the document carries existing child rows that are stored under another record.

    Frappe updates child rows by name, so saving a record with another record's row names
    would move those rows into it. New records get fresh row names on insert.
    """
    for df in doc.meta.get_table_fields():
        names = [row.name for row in doc.get(df.fieldname) or [] if row.get("name")]
        if not names:
            continue
        owners = frappe.get_all(df.options, {"name": ["in", names]}, ["parent", "parenttype"])
        if any((o.parent, o.parenttype) != (doc.name, doc.doctype) for o in owners):
            return False
    return True


def validate_child_rows(doc, method=None):
    """validate hook (see hooks.py). Runs on every save, including saves of a document shared
    with the user, which pass the has_permission hooks."""
    if not doc.is_new() and not _rows_belong_to(doc):
        frappe.throw(
            _("This record contains rows that belong to another record."), frappe.PermissionError
        )


def validate_move(doc, method=None):
    """validate hook (see hooks.py). Checks a change of chapter or event on every save,
    including saves of a document shared with the user, which pass the has_permission hooks."""
    user = frappe.session.user
    if doc.is_new() or _is_privileged(user):
        return
    field, may_move = MOVE_RULES[doc.doctype]
    before = doc.get_doc_before_save()
    stored = before.get(field) if before else frappe.db.get_value(doc.doctype, doc.name, field)
    if not may_move(stored, doc.get(field), user):
        frappe.throw(
            _("You can only move this record between chapters or events you manage."),
            frappe.PermissionError,
        )


def block_rename(doc, method=None, *args, **kwargs):
    """before_rename hook (see hooks.py). Renaming and merging rewrite links without a save, and
    leave fetched copies of the old name (such as a submission's event) in place, so only
    System Managers may rename these records."""
    if not _is_privileged(frappe.session.user):
        frappe.throw(_("Only a System Manager can rename this record."), frappe.PermissionError)


# has_permission hooks (see hooks.py) decide who may change a record. A falsy return removes
# the role permission, but Frappe still allows a document explicitly shared with the user, so
# what a save may change (moving the record, rows of other records) is checked in the validate
# hooks above, and renames in block_rename. Existing records are checked against the chapter
# or event stored in the database, because the document passed in may already carry the
# incoming values (frappe.client.set_value updates it before the check).


def chapter_has_permission(doc, ptype=None, user=None, debug=False) -> bool:
    user = user or frappe.session.user
    if ptype not in MANAGE_PTYPES or _is_new(doc, ptype) or _is_privileged(user):
        return True
    return is_chapter_member(doc.name, user)


def event_has_permission(doc, ptype=None, user=None, debug=False) -> bool:
    user = user or frappe.session.user
    if ptype not in MANAGE_PTYPES or _is_privileged(user):
        return True
    if _is_new(doc, ptype):
        return is_chapter_member(doc.get("chapter"), user)

    stored_chapter = frappe.db.get_value(EVENT, doc.name, "chapter")
    return is_chapter_member(stored_chapter, user) or is_event_member(doc.name, user)


def event_form_has_permission(doc, ptype=None, user=None, debug=False) -> bool:
    """FOSS Event RSVP and FOSS Event CFP follow the permissions of their event."""
    user = user or frappe.session.user
    if ptype not in MANAGE_PTYPES or _is_privileged(user):
        return True
    if _is_new(doc, ptype):
        return _can_manage_event(doc.get("event"), user)
    return _can_manage_event(frappe.db.get_value(doc.doctype, doc.name, "event"), user)
