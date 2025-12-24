# Copyright (c) 2025, Frappe x FOSSUnited and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestJobBoard(FrappeTestCase):
    def setUp(self):
        self.test_job_data = {
            "doctype": "Job Board",
            "job_title": "Senior Python Developer",
            "company_name": "Test Company",
            "company_website": "https://testcompany.com",
            "email": "hr@testcompany.com",
            "job_location": "Remote",
            "job_type": "Full Time",
            "application_link": "https://testcompany.com/apply",
            "job_description": "Test job description",
            "status": "Received",
        }

    def tearDown(self):
        frappe.db.rollback()

    def test_route_generation(self):
        """Test that route is auto-generated"""
        job = frappe.get_doc(self.test_job_data)
        job.insert()

        self.assertTrue(job.route)
        self.assertTrue(job.route.startswith("jobs/"))
        self.assertIn(job.name, job.route)

    def test_publish_on_approved_status(self):
        """Test that job is published when status changes to Approved"""
        job = frappe.get_doc(self.test_job_data)
        job.is_published = 0
        job.insert()

        job.status = "Approved"
        job.save()

        self.assertEqual(job.is_published, 1)

    def test_unpublish_on_rejected_status(self):
        """Test that job is unpublished when status changes to Rejected"""
        job = frappe.get_doc(self.test_job_data)
        job.status = "Approved"
        job.is_published = 1
        job.insert()

        job.status = "Rejected"
        job.save()

        self.assertEqual(job.is_published, 0)

    def test_publish_on_expired_status(self):
        """Test that job still is published when status changes to Expired"""
        job = frappe.get_doc(self.test_job_data)
        job.status = "Approved"
        job.is_published = 1
        job.insert()

        job.status = "Expired"
        job.save()

        self.assertEqual(job.is_published, 1)
