# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import json
import re
from typing import Dict, List, Optional, Tuple

import frappe
import requests
from frappe.utils import now_datetime
from frappe.website.website_generator import WebsiteGenerator

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class GrantsFundingDirectory(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data | None
        funding_json: DF.Data | None
        is_published: DF.Check
        json_data: DF.Code | None
        last_updated: DF.Datetime | None
        route: DF.Data | None
    # end: auto-generated types

    def before_save(self):
        """called before saving the document."""
        if self.is_new() or self.has_value_changed("funding_json"):
            self.fetch_and_validate_json()

        # auto-set route based on entity name
        if not self.route:
            self.set_route()

        # auto-extract email if not provided
        if not self.email:
            self.extract_email_from_json()

    def fetch_and_validate_json(self):
        """Fetch and validate funding JSON from URL."""
        if not self.funding_json:
            frappe.throw("Please enter a Funding JSON Link before saving.")

        try:
            # Fetch JSON content
            json_content = self._fetch_json_from_url(self.funding_json)

            # Validate using official API
            validated_data = self._validate_json_with_api(self.funding_json, json_content)

            # Store validated JSON
            self.json_data = json.dumps(validated_data, indent=2)
            self.last_updated = now_datetime()

        except requests.exceptions.RequestException as e:
            frappe.log_error(
                f"Error fetching funding JSON for {self.name or 'new'}: {str(e)}",
                "Grants Funding Directory Error",
            )
            frappe.throw(f"Failed to fetch JSON from URL: {str(e)}")
        except json.JSONDecodeError as e:
            frappe.throw(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            frappe.log_error(
                f"Unexpected error processing funding JSON: {str(e)}",
                "Grants Funding Directory Error",
            )
            frappe.throw(f"Error processing JSON: {str(e)}")

    def _fetch_json_from_url(self, url: str) -> str:
        """Fetch JSON content from URL."""
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text

    def _validate_json_with_api(self, url: str, json_content: str) -> dict:
        """Validate JSON using dir.floss.fund API."""
        # First try with just the body (some URLs might fail with url parameter)
        validation_data = {"body": json_content}

        try:
            validation_response = requests.post(
                "https://dir.floss.fund/api/validate",
                data=validation_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )

            validation_result = validation_response.json()

            # Check if validation failed
            if validation_response.status_code != 200:
                error_msg = validation_result.get("message", "Invalid Funding JSON")
                frappe.throw(f"Validation failed: {error_msg}")

            return validation_result.get("data", json.loads(json_content))

        except Exception as e:
            # Fallback: if validation API fails, do basic JSON parsing
            frappe.log_error(
                f"Validation API failed, falling back to basic parsing: {str(e)}",
                "Grants Funding Directory Warning",
            )
            return json.loads(json_content)

    def set_route(self):
        """route based on entity name."""
        try:
            data = json.loads(self.json_data or "{}")
            entity_name = data.get("entity", {}).get("name", self.name)
            slug = frappe.scrub(entity_name)
            self.route = f"grants/directory/{slug}"
        except Exception as e:
            frappe.log_error(f"Error setting route: {str(e)}")
            # Fallback to default
            self.route = f"grants/directory/{frappe.scrub(self.name)}"

    def extract_email_from_json(self):
        """Extract email from JSON data if available."""
        try:
            data = json.loads(self.json_data or "{}")

            # Try multiple places for email
            email = None

            # Check entity email
            entity = data.get("entity", {})
            if entity.get("email"):
                email = entity["email"]

            if email:
                self.email = email

        except Exception as e:
            frappe.log_error(f"Error extracting email: {str(e)}")

    def get_context(self, context):
        """Prepare context for rendering the page."""
        try:
            data = json.loads(self.json_data or "{}")
        except json.JSONDecodeError:
            frappe.throw("Invalid JSON data stored in document")

        # extract top-level parts
        context.entity = data.get("entity", {})
        context.projects = data.get("projects", [])
        context.funding = data.get("funding", {})

        # normalize funding channels
        channels, channels_dict = self._normalize_channels(context.funding.get("channels", []))
        context.funding_channels_list = channels
        context.funding_channels = channels_dict

        # page metadata
        entity_name = context.entity.get("name") or self.name
        context.page_title = f"{entity_name} – Funding Profile"
        context.doctype_name = self.doctype
        context.doc_name = self.name

        return context

    def _normalize_channels(self, channels: List[dict]) -> Tuple[List[dict], Dict[str, dict]]:
        """Normalize funding channel addresses."""
        site_url = frappe.utils.get_url()
        normalized_channels = []

        for ch in channels:
            addr = ch.get("address", "")

            # If address is present and not absolute, prepend base URL
            if addr:
                # Detect raw emails
                if EMAIL_REGEX.match(addr):
                    ch["address"] = f"mailto:{addr}"
                # Detect relative paths (neither http nor mailto)
                elif not addr.startswith("http") and not addr.startswith("mailto:"):
                    ch["address"] = f"{site_url.rstrip('/')}/{addr.lstrip('/')}"

            normalized_channels.append(ch)

        # Create dictionary for quick lookup
        channels_dict = {ch["guid"]: ch for ch in normalized_channels if ch.get("guid")}

        return normalized_channels, channels_dict


@frappe.whitelist(allow_guest=True)
def validate_json(url: Optional[str] = None, body: Optional[str] = None) -> dict:
    """
    API endpoint to validate funding JSON.
    Proxies to official dir.floss.fund/api/validate
    """
    try:
        # Prepare data for validation
        data = {}
        if body:
            data["body"] = body
        if url and not body:  # Only send URL if no body provided
            data["url"] = url

        if not data:
            return {
                "error": True,
                "message": "Either 'url' or 'body' parameter required",
            }

        # Call official validation API
        response = requests.post(
            "https://dir.floss.fund/api/validate",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )

        result = response.json()

        # Return result in consistent format
        if response.status_code == 200:
            return {
                "error": False,
                "message": result.get("message", "Valid funding JSON"),
                "data": result.get("data"),
            }
        else:
            return {
                "error": True,
                "message": result.get("message", "Validation failed"),
            }

    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"Failed to connect to validation service: {str(e)}",
        }
    except json.JSONDecodeError as e:
        return {"error": True, "message": f"Invalid JSON response: {str(e)}"}
    except Exception as e:
        frappe.log_error(f"Validation error: {e}")
        return {"error": True, "message": f"Validation error: {str(e)}"}


@frappe.whitelist()
def refresh_funding_data(docname: str) -> dict:
    """Refresh funding data by re-fetching and validating JSON."""
    try:
        doc = frappe.get_doc("Grants Funding Directory", docname)
        doc._fetch_and_validate_json()
        doc.save()
        return {"success": True, "message": "Funding data refreshed successfully"}
    except Exception as e:
        frappe.log_error(f"Error refreshing funding data: {str(e)}")
        return {"success": False, "message": str(e)}
