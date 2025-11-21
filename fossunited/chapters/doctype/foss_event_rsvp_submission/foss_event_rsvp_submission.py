import frappe
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, getdate, now_datetime

from fossunited.api.chapter import check_if_chapter_member
from fossunited.api.emailing import handle_email_group_subscription
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_RSVP, RSVP_RESPONSE

logger = frappe.logger("rsvp_submission", allow_site=True, file_count=50)


class FOSSEventRSVPSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.event_check_in.event_check_in import (
            EventCheckIn,
        )
        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )

        chapter: DF.Data | None
        check_ins: DF.Table[EventCheckIn]
        confirm_attendance: DF.Check
        custom_answers: DF.Table[FOSSCustomAnswer]
        email: DF.Data
        event: DF.Data
        event_name: DF.Data | None
        im_a: DF.Literal["", "Student", "Professional", "FOSS Enthusiast", "Other"]
        linked_rsvp: DF.Link
        name1: DF.Data
        status: DF.Literal["Pending", "Accepted", "Rejected"]
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
        if (
            self.has_value_changed("subscribe_chapter_mailing")
            or self.has_value_changed("status")
            or self.has_value_changed("confirm_attendance")
        ):
            self.handle_add_to_email_group()

    def on_trash(self):
        # Remove from both event and chapter groups on delete
        try:
            if self.email:
                handle_email_group_subscription(
                    emails=[self.email],
                    chapter=self.chapter,
                    event=self.event,
                    subscribe_to_chapter=False,
                    subscribe_to_event=False,
                    document_type_event=EVENT,
                )
        except frappe.ValidationError as e:
            frappe.log_error(frappe.get_traceback(), f"on_trash unsubscribe failed: {e}")

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
        # If requires_host_approval == True, but the status is accepted at time of creation,
        # Throw a frappe.PermissionError
        requires_host_approval = bool(
            frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "requires_host_approval")
        )

        if requires_host_approval and self.status == "Accepted":
            frappe.throw("Invalid action. Status cannot be `Accepted`.", frappe.PermissionError)

        # If the RSVP requires host approval, set the status to Pending
        if requires_host_approval:
            self.status = "Pending"
            return

        # If the RSVP does not require host approval, set the status to Accepted
        self.status = "Accepted"

    def handle_add_to_email_group(self):
        wants_subscription = cint(self.subscribe_chapter_mailing) == 1
        is_accepted = self.status == "Accepted"
        is_attending = cint(self.confirm_attendance) == 1
        if not self.email:
            return

        handle_email_group_subscription(
            emails=[self.email],
            chapter=self.chapter,
            event=self.event,
            subscribe_to_chapter=wants_subscription,
            subscribe_to_event=is_accepted and is_attending,
            document_type_event=EVENT,
        )

    @frappe.whitelist()
    def add_check_in(self):
        """Add a check-in record for this submission"""
        # Check if event allows check-in (between start and end date)
        event_start, event_end = frappe.db.get_value(
            EVENT, self.event, ["event_start_date", "event_end_date"]
        )
        if not self.can_check_in(event_start, event_end):
            frappe.throw("Check-in is only available during the event dates")

        # Check if already checked in today
        if self.has_checked_in_today():
            frappe.throw("You have already checked in today")

        # Add check-in record
        self.append("check_ins", {"check_in_time": now_datetime()})
        self.save(ignore_permissions=True)

        return {"success": True, "message": "Checked in successfully"}

    def can_check_in(self, event_start_date, event_end_date):
        """Check if check-in is allowed (between event start and end dates)"""
        if not event_start_date or not event_end_date:
            return False

        now = get_datetime()
        start = get_datetime(event_start_date)
        end = get_datetime(event_end_date)

        return start <= now <= end

    def has_checked_in_today(self):
        """Check if user has already checked in today"""

        today = getdate()
        for check_in in self.check_ins:
            if getdate(check_in.check_in_time) == today:
                return True
        return False


@frappe.whitelist()
def self_check_in(submission_name):
    """API endpoint for self check-in"""
    doc = frappe.get_doc(RSVP_RESPONSE, submission_name)
    return doc.add_check_in()
