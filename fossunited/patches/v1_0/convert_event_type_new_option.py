import frappe

from fossunited.doctype_ids import EVENT


def execute():
    doctype = EVENT
    fieldname = "event_type"

    # map old values to new ones
    mapping = {
        "City Meetup": "Meet Up",
        "FOSS Meetup": "Meet Up",
        "CityFOSS Conference": "Conference",
        "FOSS Hack": "Hackathon",
    }

    print("\n--- Starting Event Type Migration ---\n")
    # update documents with new values
    for old_value, new_value in mapping.items():
        frappe.db.set_value(
            doctype,
            {"event_type": old_value},
            fieldname,
            new_value,
            update_modified=False,
        )
        print(f"Updated '{old_value}' → '{new_value}'")
    # change fieldtype from Link to Select and set new options
    docfield = frappe.get_doc("DocField", {"parent": doctype, "fieldname": fieldname})

    docfield.fieldtype = "Select"
    docfield.options = "\n".join(
        [
            "Meet Up",
            "Conference",
            "Workshop",
            "Birds Of Feathers",
            "Hackathon",
            "Linux Installation Party",
        ]
    )
    docfield.save()
    print("Updated fieldtype to 'Select' with new options")

    # rebuild schema and clear cache
    frappe.clear_cache(doctype=doctype)
    frappe.db.commit()
    print("\nEvent Type migration completed.\n")
