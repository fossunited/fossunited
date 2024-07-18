import frappe


def get_event_cfp_submissions(event: str):
    submissions = frappe.db.get_list(
        "FOSS Event CFP Submission",
        filters={"event": event},
        fields=["*"],
        order_by="creation desc",
    )

    return submissions


@frappe.whitelist()
def get_cfp_submissions_by_reviewer_status(
    event: str,
    status_filter: list = ["Reviewed", "Not Reviewed"],
    to_approve_filter: list = ["Yes", "No", "Maybe"],
):
    if not has_reviewer_role():
        frappe.throw("Unauthorized Access")

    submissions_list = []

    submissions = get_event_cfp_submissions(event)

    reviewer = frappe.db.get_value(
        "FOSS User Profile", {"user": frappe.session.user}, "name"
    )

    for submission in submissions:
        if not frappe.db.exists(
            "FOSS Event CFP Review",
            {
                "parent": submission.name,
                "reviewer": reviewer,
                "parenttype": "FOSS Event CFP Submission",
            },
        ):
            if "Not Reviewed" in status_filter:
                submission["review_status"] = "Not Reviewed"
                submission["status"] = "-"
                submission["remarks"] = "-"
                submissions_list.append(submission)
            continue

        if "Reviewed" in status_filter:
            review = frappe.get_doc(
                "FOSS Event CFP Review",
                {
                    "parent": submission.name,
                    "reviewer": reviewer,
                    "parenttype": "FOSS Event CFP Submission",
                },
            )
            if review.to_approve in to_approve_filter:
                submission["review_status"] = "Reviewed"
                submission["reviewer_status"] = review.to_approve
                submission["reviewer_remarks"] = review.remarks
                submissions_list.append(submission)

    return submissions_list


def has_reviewer_role():
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "CFP Reviewer", "parent": frappe.session.user},
        )
    )
