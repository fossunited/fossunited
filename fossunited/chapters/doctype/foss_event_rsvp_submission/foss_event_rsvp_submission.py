import frappe
from frappe.model.document import Document
from frappe.utils import cint

from fossunited.api.chapter import check_if_chapter_member
from fossunited.api.emailing import (
    add_to_email_group,
    create_email_group,
    remove_from_email_group,
)
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_RSVP, RSVP_RESPONSE

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("rsvp_submission", allow_site=True, file_count=50)


class FOSSEventRSVPSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )

        chapter: DF.Data | None
        confirm_attendance: DF.Check
        custom_answers: DF.Table[FOSSCustomAnswer]
        email: DF.Data
        event: DF.Data
        event_name: DF.Data | None
        im_a: DF.Literal["", "Student", "Professional", "FOSS Enthusiast", "Other"]  # noqa: F722, F821
        linked_rsvp: DF.Link
        name1: DF.Data
        status: DF.Literal["Pending", "Accepted", "Rejected"]  # noqa: F722, F821
        submitted_by: DF.Link | None
        subscribe_chapter_mailing: DF.Check
    # end: auto-generated types

    def validate(self):
        self.validate_linked_rsvp_exists()

    def before_insert(self):
        self.validate_rsvp_is_published()
        self.handle_submission_status()

    def after_insert(self):
        self.close_rsvp_on_max_count()
        self.handle_add_to_email_group()

    def before_save(self):
        if self.has_value_changed("subscribe_chapter_mailing") and not self.is_new():
            self.handle_add_to_email_group()

    def validate_linked_rsvp_exists(self):
        if not frappe.db.exists(EVENT_RSVP, self.linked_rsvp):
            frappe.throw("Invalid RSVP", frappe.DoesNotExistError)

    def validate_rsvp_is_published(self):
        is_system_user = frappe.get_roles(frappe.session.user).count("System Manager")
        is_chapter_member = check_if_chapter_member(chapter=self.chapter, user=frappe.session.user)

        # If the user is system user or team member,
        # don't check for validation before rsvp submission creation
        if is_system_user or is_chapter_member:
            return

        rsvp_published = frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "is_published")
        if not rsvp_published:
            frappe.throw("RSVP is not published")

    def close_rsvp_on_max_count(self):
        max_count = self.get_max_count()
        submission_count = frappe.db.count(
            RSVP_RESPONSE,
            {"linked_rsvp": self.linked_rsvp},
        )

        if submission_count >= max_count:
            frappe.db.set_value(
                EVENT_RSVP,
                self.linked_rsvp,
                "is_published",
                False,
            )
            self.notify_organizers()

    def notify_organizers(self):
        # Notify the organizers that the RSVP has reached its maximum count
        # This can be done via email or any other notification system
        organizer_email = frappe.db.get_value(
            CHAPTER,
            filters={"name": self.chapter},
            fieldname="email",
        )

        message = f"""
        Dear Organizers,
        <br>
        The RSVP for {self.event_name} has reached its maximum count.<br>
        RSVP form is now closed.<br>
        Regards,<br>
        FOSS United Team
        """

        frappe.sendmail(
            recipients=organizer_email,
            subject="RSVP Maximum Count Reached",
            message=message,
        )

    def get_max_count(self):
        max_count = frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "max_rsvp_count")
        return max_count

    def handle_submission_status(self):
        if self.status:  # Respect what's set from the web form
            return

        requires_host_approval = bool(
            frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "requires_host_approval")
        )

        self.status = "Pending" if requires_host_approval else "Accepted"

    def handle_add_to_email_group(self):
        wants_subscription = cint(self.subscribe_chapter_mailing) == 1

        event_group = create_email_group(
            type="Event Participants",
            reference_document=self.event,
            document_type=EVENT,
        )
        chapter_group = create_email_group(
            type="Chapter Event Participants",
            reference_document=self.chapter,
            document_type=CHAPTER,
        )

        if wants_subscription:
            logger.info(f"[Email Group] Subscribing {self.email} to {event_group.name}")
            add_to_email_group(event_group.name, self.email)
            add_to_email_group(chapter_group.name, self.email)
        else:
            logger.info(f"[Email Group] Unsubscribing {self.email} from {event_group.name}")
            remove_from_email_group(event_group.name, self.email)
            remove_from_email_group(chapter_group.name, self.email)
