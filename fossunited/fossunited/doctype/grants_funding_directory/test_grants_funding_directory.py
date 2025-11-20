"""
Tests for robust validation check on funding.json schema via dir.floss.fund/api/validate
"""

import copy
import json
import os
import tempfile

import frappe
import requests
from frappe.tests.utils import FrappeTestCase


def upload_json(file_path):
    """
    Upload JSON file to 0x0.st or paste.rs and return the public URL.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }

    # Try 0x0.st first
    try:
        with open(file_path, "rb") as f:
            r = requests.post("https://0x0.st", files={"file": f}, headers=headers, timeout=20)
        if r.status_code == 200 and r.text.startswith("https://0x0.st"):
            return r.text.strip()
    except Exception as e:
        frappe.log_error(f"0x0.st upload failed: {str(e)}")

    # Fallback: paste.rs
    with open(file_path, "rb") as f:
        r = requests.post("https://paste.rs", data=f, headers=headers, timeout=20)
        if r.status_code in (200, 201) and r.text.startswith("http"):
            return r.text.strip()

    raise Exception("Upload failed on both 0x0.st and paste.rs")


class TestGrantsFundingDirectoryRealValidation(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")

        # VALID JSON
        self.valid_json = {
            "$schema": "https://fundingjson.org/schema/v1.1.0.json",
            "version": "v1.0.0",
            "entity": {
                "type": "organisation",
                "role": "contributor",
                "name": "FOSS United",
                "email": "contact@fossunited.org",
                "phone": "+91-00000-00000",
                "description": "FOSS United.",
                "webpageUrl": {"url": "https://fossunited.org", "wellKnown": ""},
            },
            "projects": [
                {
                    "guid": "fossunited-platform",
                    "name": "FOSS United Platform",
                    "description": "Platform.",
                    "webpageUrl": {"url": "https://fossunited.org"},
                    "repositoryUrl": {
                        "url": "https://github.com/fossunited",
                        "wellKnown": "https://github.com/fossunited/.well-known/funding-manifest-urls",
                    },
                    "licenses": ["spdx:MIT"],
                    "tags": ["foss", "community", "platform", "foundation"],
                }
            ],
            "funding": {
                "channels": [
                    {
                        "guid": "forum-fossunited-org",
                        "type": "cash",
                        "address": "https://fossunited.org/rss",
                        "description": "We welcome Code contributions!",
                    },
                ],
                "plans": [
                    {
                        "guid": "community-support-monthly",
                        "status": "active",
                        "name": "Community Support (Monthly)",
                        "description": "Stay active with community!",
                        "amount": 500,
                        "currency": "INR",
                        "frequency": "monthly",
                        "channels": ["forum-fossunited-org"],
                    },
                ],
                "history": [
                    {
                        "year": 2025,
                        "income": 1200000,
                        "expenses": 1199999,
                        "taxes": 1,
                        "currency": "INR",
                        "description": "Growth of city chapters and launch of FOSS Hack events.",
                    },
                ],
            },
        }

        # INVALID JSON (missing entity)
        self.invalid_json = {
            "version": "v1.0.0",
            "projects": [],
        }

    def upload_temp(self, data):
        """Write a JSON to a temp file and upload it."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        try:
            tmp.write(json.dumps(data, indent=2).encode())
            tmp.flush()
        finally:
            tmp.close()

        url = upload_json(tmp.name)
        os.remove(tmp.name)

        return url

    def test_valid_json_api_validation(self):
        """floss.fund validate API using uploaded valid JSON."""
        url = self.upload_temp(self.valid_json)

        doc = frappe.get_doc(
            {
                "doctype": "Grants Funding Directory",
                "funding_json": url,
                "name": "Real Valid FundingTest",
            }
        )

        # THIS triggers the real validator via HTTPS
        doc.insert()

        self.assertIsNotNone(doc.json_data)
        parsed = json.loads(doc.json_data)
        self.assertEqual(parsed["entity"]["email"], "contact@fossunited.org")

        frappe.delete_doc("Grants Funding Directory", doc.name, force=True)

    def test_invalid_json_api_validation(self):
        """Real validation MUST reject this invalid JSON."""
        bad = copy.deepcopy(self.valid_json)
        bad["projects"] = []

        url = self.upload_temp(bad)

        doc = frappe.get_doc(
            {
                "doctype": "Grants Funding Directory",
                "funding_json": url,
                "name": "Real Invalid FundingTest",
            }
        )

        # The real API should reject this
        with self.assertRaises(Exception):
            doc.insert()

        self.assertFalse(frappe.db.exists("Grants Funding Directory", "Real Invalid FundingTest"))

    def test_missing_entity_name_fails(self):
        """simple test to check if entity name is missing"""
        bad = copy.deepcopy(self.valid_json)
        bad["entity"]["name"] = None

        url = self.upload_temp(bad)

        doc = frappe.get_doc(
            {
                "doctype": "Grants Funding Directory",
                "funding_json": url,
                "name": "Missing Entity Name Test",
            }
        )

        with self.assertRaises(Exception):
            doc.insert()

    def test_missing_email_fails(self):
        """simple test if no email is given, api validation should raise error"""
        bad = copy.deepcopy(self.valid_json)
        bad["entity"]["email"] = ""

        url = self.upload_temp(bad)

        doc = frappe.get_doc(
            {
                "doctype": "Grants Funding Directory",
                "funding_json": url,
                "name": "Missing Email Test",
            }
        )

        with self.assertRaises(Exception):
            doc.insert()
