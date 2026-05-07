import frappe

from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET, RSVP_RESPONSE


def send_event_feedback_request(event_id):
    """Enqueued after event status -> Concluded. Sends feedback request to all participants."""
    doc = frappe.get_doc(EVENT, event_id)

    if doc.is_paid_event:
        emails = frappe.db.get_all(EVENT_TICKET, filters={"event": event_id}, pluck="email")
        feedback_url = f"https://fossunited.org/main-events-feedback/new?event={event_id}"
    else:
        emails = frappe.db.get_all(
            RSVP_RESPONSE,
            filters={"event": event_id, "status": "Accepted"},
            pluck="email",
        )
        feedback_url = f"https://fossunited.org/chapter-events-feedback/new?event={event_id}"

    emails = list({e.strip().lower() for e in emails if e and e.strip()})
    if not emails:
        return

    chapter_email = frappe.db.get_value(CHAPTER, doc.chapter, "email")
    sender = chapter_email or None

    subject = f"Feedback for {doc.event_name}"
    message = f"""<p>Thank you for RSVPing to <strong>{doc.event_name}</strong>.</p>
<p>Whether you were able to join us or missed out this time, we would love to hear
your thoughts. Please take a moment to complete our
<a href="{feedback_url}">Feedback Survey</a> as it helps us improve our programs
for the broader community.</p>
<p>— Team {doc.event_name}</p>"""

    for email in emails:
        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message,
            sender=sender,
            reference_doctype=EVENT,
            reference_name=event_id,
        )

    frappe.db.set_value(EVENT, event_id, "feedback_sent", 1)
    frappe.log_error(
        title=f"Feedback email sent: {event_id}",
        message=f"Sent to {len(emails)} participants.",
    )
