import frappe


def execute():
    """Migrate existing participants to status-based groups"""

    # Get ALL participants to ensure proper email group sync
    participants = frappe.get_all(
        "FOSS Hackathon Participant",
        fields=[
            "name",
            "localhost",
            "localhost_request_status",
            "wants_to_attend_locally",
        ],
        filters={
            "hackathon": "1hdcnkbtmk",  # FOSS Hack 2026
            "localhost": ["is", "set"],
        },
    )

    total = len(participants)
    print(f"Starting migration for {total} participants")

    success_count = 0
    error_count = 0

    for p in participants:
        try:
            doc = frappe.get_doc("FOSS Hackathon Participant", p.name)

            # Sync localhost groups only if applicable
            if p.wants_to_attend_locally and p.localhost:
                doc.sync_localhost_status_groups()

            # Always sync chapter/hackathon groups
            doc.handle_add_to_email_group()

            success_count += 1
            if success_count % 100 == 0:
                frappe.db.commit()
                print(f"Progress: {success_count}/{total}")

        except Exception as e:
            error_count += 1
            print(f"Error migrating participant {p.name}: {e!s}")
            frappe.logger().error(f"Error migrating participant {p.name}: {e!s}")
            continue

    # Single commit at the end
    frappe.db.commit()

    print(f"Migration complete! Success: {success_count}, Errors: {error_count}")
    frappe.logger().info(f"Migration complete! Success: {success_count}, Errors: {error_count}")
