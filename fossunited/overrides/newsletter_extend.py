import frappe
from frappe.utils import random_string


def autoname(doc, method=None):
    """Give Newsletter a random name instead of the default subject-based name, avoiding conflicts."""
    doc.name = generate_unique_newsletter_code()


def generate_unique_newsletter_code():
    code = random_string(10).lower()
    while frappe.db.exists("Newsletter", code):
        code = random_string(10).lower()
    return code
