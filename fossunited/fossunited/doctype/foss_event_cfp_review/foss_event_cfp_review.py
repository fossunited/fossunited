# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSEventCFPReview(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        remarks: DF.SmallText | None
        reviewer: DF.Data | None
        reviewer_profile: DF.Link | None
        to_approve: DF.Literal["", "Yes", "No", "Maybe"]
    # end: auto-generated types
    def before_save(self):
        self.calculate_total_score()

    def on_update(self):
        self.update_submission_scores()
        self.notify_proposer_on_review()

    def after_insert(self):
        self.update_submission_scores()
        self.notify_proposer_on_review()

    def update_submission_scores(self):
        if not self.proposal:
            return
        reviews = frappe.get_all("FOSS Event CFP Review", {"proposal": self.proposal}, ["to_approve"])
        
        total = len(reviews) or 1
        yes = sum(1 for r in reviews if r.to_approve == "Yes")
        no = sum(1 for r in reviews if r.to_approve == "No")
        maybe = sum(1 for r in reviews if r.to_approve == "Maybe")
        
        frappe.db.set_value("FOSS Event CFP Submission", self.proposal, {
            "positive_reviews": int((yes / total) * 100),
            "negative_reviews": int((no / total) * 100),
            "unsure_reviews": int((maybe / total) * 100)
        })
        
    def notify_proposer_on_review(self):
        if not self.proposal:
            return
        proposal_doc = frappe.get_doc("FOSS Event CFP Submission", self.proposal)
        old_doc = self.get_doc_before_save()
        
        change_type = None
        if self.is_new() or not old_doc:
            change_type = "new"
        elif self.remarks != old_doc.remarks:
            change_type = "remarks_changed"
            
        if not change_type:
            return
            
        if not proposal_doc.email:
            return
            
        speaker_emails = [s.email for s in proposal_doc.speakers if s.email]
        sub_prefix = "New review" if change_type == "new" else "Review remarks updated"
        
        try:
            frappe.sendmail(
                recipients=proposal_doc.email,
                cc=speaker_emails,
                subject=f"{sub_prefix} on your proposal for {proposal_doc.event_name}",
                message=proposal_doc._build_review_message(self, change_type, old_doc),
                reference_doctype="FOSS Event CFP Submission",
                reference_name=self.proposal,
            )
        except Exception:
            frappe.log_error(
                title="review_notification:send_failed",
                message=frappe.get_traceback(),
            )

    def calculate_total_score(self):
        if not self.scores:
            self.total_score = 0
            return

        total = 0
        import frappe
        for score_row in self.scores:
            if not score_row.category or not score_row.score:
                continue
            weight = frappe.db.get_value("CFP Score Category", score_row.category, "weight") or 1.0
            total += float(score_row.score) * float(weight)
        
        self.total_score = total
