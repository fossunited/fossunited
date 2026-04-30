import frappe


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
