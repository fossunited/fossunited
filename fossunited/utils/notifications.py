import frappe
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)

from fossunited.doctype_ids import (
    CAMPAIGN,
    CHAPTER,
    EMAIL_GROUP,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
)


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

    frappe.db.set_value(EVENT, event_id, "feedback_sent", 1)
    frappe.log_error(
        title=f"Feedback email sent: {event_id}",
        message=f"Campaign {newsletter.name} sent to groups: {email_groups}",
    )


def send_event_rsvp_reminder(event_id):
    doc = frappe.get_doc(EVENT, event_id)

    email_groups = frappe.db.get_all(
        EMAIL_GROUP,
        filters={
            "reference_document": event_id,
            "document_type": EVENT,
            "group_type": "Event Participants",
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

    event_url = f"https://fossunited.org/{doc.route}"
    start_date_display = doc.event_start_date.strftime("%A, %-d %B %Y")
    start_time_display = doc.event_start_date.strftime("%-I:%M %p")

    location_html = ""
    if doc.event_location:
        if doc.map_link:
            location_html = (
                f'<li><span>Location: </span><a href="{doc.map_link}">'
                f"{doc.event_location}</a></li>"
            )
        else:
            location_html = f"<li><span>Location: </span>{doc.event_location}</li>"

    subject = f"Reminder: {doc.event_name} is tomorrow!"
    message = f"""<p>This is a friendly reminder that <a href="{event_url}"><strong>{doc.event_name}</strong></a> is happening tomorrow!</p>

<ul>
  <li><span>Date: </span>{start_date_display}</li>
  <li><span>Time: </span>{start_time_display}</li>
  {location_html}
</ul>

<p>We look forward to seeing you there. Check the
<a href="{event_url}">event page</a> for the latest schedule and updates.</p>

<p>Regards,<br>Team {doc.event_name}</p>"""

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

    frappe.db.set_value(EVENT, event_id, "reminder_sent", 1)


def notify_cfp_reviewer_assignment(doc, method=None) -> None:
    """
    doc_events hook: ToDo → after_insert.
    Sends in-app + email notification when a CFP submission is assigned to a reviewer,
    sending URL to the reviewer dashboard instead of the Frappe desk form.
    """
    if doc.reference_type != PROPOSAL:
        return

    assigned_by = doc.assigned_by or frappe.session.user
    if assigned_by == doc.allocated_to:
        return

    submission = frappe.db.get_value(
        PROPOSAL, doc.reference_name, ["linked_cfp", "talk_title"], as_dict=True
    )
    if not submission:
        return

    event_id = frappe.db.get_value(EVENT_CFP, submission.linked_cfp, "event")
    if not event_id:
        return

    event_name = frappe.db.get_value(EVENT, event_id, "event_name") or event_id
    dashboard_url = (
        f"{frappe.utils.get_url()}/dashboard/review/{event_id}?submission={doc.reference_name}"
    )

    subject = f'New proposal to review: "{submission.talk_title}"'
    email_content = f"""
        <p style="margin: 0 0 8px;">
          You have been assigned a proposal to review for <b>{event_name}</b>:
        </p>
        <p style="margin: 0 0 16px; font-size: 15px;"><b>{submission.talk_title}</b></p>
        <a href="{dashboard_url}" style="display:inline-block; padding: 8px 16px; background:#2d6a4f; color:#fff; border-radius:6px; text-decoration:none; font-size:14px;">
          Open Reviewer Dashboard
        </a>
    """

    enqueue_create_notification(
        doc.allocated_to,
        {
            "type": "Assignment",
            "document_type": PROPOSAL,
            "document_name": doc.reference_name,
            "subject": subject,
            "from_user": assigned_by,
            "email_content": email_content,
            "link": dashboard_url,
        },
    )
