import json

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import EVENT, RAZORPAY_PAYMENT

fake = Faker()


class TestRazorpayPayment(IntegrationTestCase):
    def setUp(self):
        self.admin_user = frappe.get_doc("User", "Administrator")
        self.normal_user = frappe.get_doc("User", "test1@example.com")
        self.event = self.create_dummy_event()

    def tearDown(self):
        frappe.set_user("Administrator")

        # Delete any created Razorpay Payment documents
        payments = frappe.get_all(RAZORPAY_PAYMENT, filters={"document_name": self.event})
        for payment in payments:
            frappe.delete_doc(RAZORPAY_PAYMENT, payment.name)

        # Delete created event
        frappe.delete_doc(EVENT, self.event)

        frappe.db.commit()

    def create_dummy_event(self):
        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "event_name": fake.catch_phrase(),
                "event_permalink": fake.slug().replace("-", "_"),
                "status": "Live",
                "event_type": "CityFOSS Conference",
                "event_start_date": "2024-09-05 10:00:00",
                "event_end_date": "2024-09-05 13:00:00",
                "event_description": fake.paragraph(),
                "t_shirt_price": 100,  # Set t-shirt price
                "is_paid_event": 1,
                "tiers": [{"title": "General", "price": 200}],
            }
        ).insert(ignore_permissions=True)
        return event.name

    def create_payment_document(self, user):
        frappe.set_user(user.name)
        tier = frappe.get_doc(EVENT, self.event).tiers[0]

        # Have taken this metadata to mimic the razorpay payment metadata
        meta_data = {
            "attendees": [
                {
                    "designation": fake.job(),
                    "email": fake.email(),
                    "full_name": fake.name(),
                    "organization": fake.company(),
                    "placeholder": fake.name(),
                    "wants_tshirt": 0,
                },
                {
                    "designation": fake.job(),
                    "email": fake.email(),
                    "full_name": fake.name(),
                    "organization": fake.company(),
                    "placeholder": fake.name(),
                    "wants_tshirt": 0,
                },
            ],
            "custom_fields": {
                "food_preference": fake.random_element(elements=("Veg", "Non-Veg", "Vegan"))
            },
            "event": self.event,
            "num_seats": "2",
            "tier": {
                "creation": str(tier.creation),
                "currency": tier.currency,
                "description": tier.description,
                "docstatus": tier.docstatus,
                "doctype": "FOSS Ticket Tier",
                "enabled": tier.enabled,
                "idx": tier.idx,
                "maximum_tickets": tier.maximum_tickets,
                "modified": str(tier.modified),
                "modified_by": tier.modified_by,
                "name": tier.name,
                "owner": tier.owner,
                "parent": tier.parent,
                "parentfield": "tiers",
                "parenttype": EVENT,
                "price": tier.price,
                "title": tier.title,
                "valid_till": str(tier.valid_till),
            },
        }

        invoice = frappe.get_doc(
            {
                "doctype": RAZORPAY_PAYMENT,
                "document_type": EVENT,
                "document_name": self.event,
                "email": user.email,
                "amount": tier.price * 2,  # 2 attendees
                "currency": "INR",
                "status": "Pending",
                "meta_data": json.dumps(meta_data),
            }
        )

        try:
            invoice.insert()
            frappe.db.commit()
            return invoice
        except Exception:
            frappe.db.rollback()
            raise

    def test_admin_can_create_invoice(self):
        invoice = self.create_payment_document(self.admin_user)
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.doctype, RAZORPAY_PAYMENT)
        self.assertEqual(invoice.owner, self.admin_user.name)

    def test_normal_user_cannot_create_invoice(self):
        with self.assertRaises(frappe.PermissionError):
            self.create_payment_document(self.normal_user)
