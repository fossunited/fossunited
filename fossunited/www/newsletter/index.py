import frappe
import datetime


def get_context(context):
    newsletters = frappe.get_all(
        "Newsletter",
        filters={"published": 1},
        fields=["name", "subject", "route", "email_sent_at"],
        order_by="creation desc",
    )

    for newsletter in newsletters:
        if newsletter["email_sent_at"]:
            newsletter["email_sent_at"] = newsletter["email_sent_at"].strftime("%d %B, %Y")            
            print(newsletter["email_sent_at"])
            
    context.newsletters = newsletters

