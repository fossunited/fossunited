# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import json
import re
from email.utils import parsedate_to_datetime
from typing import Dict, List, Tuple

import frappe
import requests
from frappe.utils import add_days, get_datetime, now_datetime
from frappe.website.website_generator import WebsiteGenerator

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class GrantsFundingDirectory(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data | None
        funding_json: DF.Data
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
        self.set_route()

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
        validation_data = {"url": url, "body": json_content}

        try:
            validation_response = requests.post(
                "https://dir.floss.fund/api/validate",
                data=validation_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )

            # If API returned non-200, raise immediately
            if validation_response.status_code != 200:
                result = validation_response.json()
                error_msg = result.get("message", "Invalid Funding JSON")
                frappe.throw(f"Validation failed: {error_msg}")

            # API returned 200 → parse JSON
            result = validation_response.json()

            # Must contain validated data
            if "data" not in result:
                frappe.throw("Validation failed: API returned no data")

            return result["data"]

        except Exception as e:
            frappe.throw(
                f"Validation error. Please verify with https://dir.floss.fund/validate: {str(e)}"
            )

    def set_route(self):
        """route based on entity name."""
        data = json.loads(self.json_data or "{}")
        entity_name = data.get("entity", {}).get("name", self.name)
        slug = frappe.scrub(entity_name)
        self.route = f"grants/directory/{slug}"

    def extract_email_from_json(self):
        """Extract email from JSON data if available."""
        data = json.loads(self.json_data or "{}")
        entity = data.get("entity", {})
        self.email = entity["email"]

    def get_context(self, context):
        """Prepare context for rendering the page."""
        self.refresh_manifest_json()
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

    def refresh_manifest_json(self):
        """
        Alternative to scheduler, so every page visit leads to re-fetching of data within a week.
        """
        if not self.last_updated:
            return

        if get_datetime(self.last_updated) > add_days(now_datetime(), -7):
            return

        try:
            r = requests.head(self.funding_json, timeout=5, allow_redirects=True)
            if not r.ok:
                return

            last_modified = r.headers.get("last-modified")
            local_dt = get_datetime(self.last_updated)

            if not last_modified:
                self.fetch_and_validate_json()
                self.save(ignore_permissions=True)
            else:
                remote_dt = parsedate_to_datetime(last_modified)

                if remote_dt > local_dt:
                    self.fetch_and_validate_json()
                    self.save(ignore_permissions=True)

            # Update timestamp so we don't recheck for another week
            self.last_updated = now_datetime()
            self.save(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(
                title="Manifest refresh failed",
                message=(f"URL: {self.funding_json}\n{repr(e)}"),
            )


@frappe.whitelist()
def refresh_funding_data(docname: str) -> dict:
    """Refresh funding data by re-fetching and validating JSON."""
    try:
        doc = frappe.get_doc("Grants Funding Directory", docname)
        doc.fetch_and_validate_json()
        doc.save()
        return {"success": True, "message": "Funding data refreshed successfully"}
    except Exception as e:
        frappe.log_error(f"Error refreshing funding data: {str(e)}")
        return {"success": False, "message": str(e)}
