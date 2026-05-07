import frappe

from fossunited.doctype_ids import CAMPAIGN, CHAPTER, EMAIL_GROUP, EVENT


def send_event_feedback_request(event_id):
    """Enqueued after event status -> Concluded. Sends feedback request via Newsletter campaign."""
    doc = frappe.get_doc(EVENT, event_id)

    feedback_url = (
        f"https://fossunited.org/main-events-feedback/new?event={event_id}"
        if doc.is_paid_event
        else f"https://fossunited.org/chapter-events-feedback/new?event={event_id}"
    )

    # Include attendees + speakers. Speakers live in "Accepted Proposers" group.
    email_groups = frappe.db.get_all(
        EMAIL_GROUP,
        filters={
            "reference_document": event_id,
            "document_type": EVENT,
            "group_type": ["in", ["Event Participants", "Accepted Proposers"]],
            "total_subscribers": [">", 0],
        },
        pluck="name",
    )

    if not email_groups:
        return

    chapter_name, chapter_email = frappe.db.get_value(
        CHAPTER, doc.chapter, ["chapter_name", "email"]
    )
    chapter_email = chapter_email or "noreply@fossunited.org"

    subject = f"Feedback for {doc.event_name}"
    message = f"""<p>Thank you for attending <strong>{doc.event_name}</strong>.</p><br/>
<p>Whether you were able to join us or missed out this time, we would love to hear
your thoughts. Please take a moment to complete our
<a href="{feedback_url}">Feedback Survey</a> as it helps us improve our programs
for the broader community.</p><br/>
<p>Team {doc.event_name}</p>"""

    newsletter = frappe.get_doc(
        {
            "doctype": CAMPAIGN,
            "reference_document": event_id,
            "document_type": EVENT,
            "chapter": doc.chapter,
            "sender_name": chapter_name,
            "sender_email": chapter_email,
            "email_group": [{"email_group": g} for g in email_groups],
            "subject": subject,
            "content_type": "Rich Text",
            "message": message,
        }
    )
    newsletter.flags.ignore_permissions = True
    newsletter.insert(ignore_permissions=True)
    newsletter.send_emails()
    newsletter.save(ignore_permissions=True)

    frappe.db.set_value(EVENT, event_id, "feedback_sent", 1)
    frappe.log_error(
        title=f"Feedback email sent: {event_id}",
        message=f"Campaign {newsletter.name} sent to groups: {email_groups}",
    )
