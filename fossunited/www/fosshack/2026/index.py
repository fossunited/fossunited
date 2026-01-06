import frappe

from fossunited.fossunited.utils import get_event_sponsors


def get_context(context):
    """Context for FOSS Hack 2026 page"""

    hackathon_id = frappe.db.get_value("FOSS Hackathon", {"hackathon_name": "FOSS Hack 2026"})

    # Fetch hackathon details
    hackathon = frappe.get_doc("FOSS Hackathon", hackathon_id)

    context.doc = hackathon
    context.pagetitle, context.description, context.image = hackathon.get_meta()

    context.hackathon = {
        "name": hackathon.hackathon_name,
        "tagline": "India's Largest FOSS Hackathon",
        "date": "March 2026",
        "mode": "Hybrid",
        "description": """
        FOSS Hack 2026 is the sixth edition of FOSS Hack, a hybrid hackathon to promote
        Free and Open Source Software by bringing together students and professionals
        to build or extend FOSS projects""",
        "prize_pool": "₹5,00,000",
        "register_url": f"/dashboard/register-for-hackathon?id={hackathon_id}",
        "event_page_url": "https://forum.fossunited.org/t/hackathon-ideas/159",
        "status": "Registrations Open"
        if hackathon.is_registration_live
        else "Opening on Jan 2026",
    }

    # Timeline
    context.timeline = [
        {"date": "TBA", "event": "Registrations Closing"},
        {"date": "TBA", "event": "Planning and team formation"},
        {"date": "TBA", "event": "Development"},
        {"date": "TBA", "event": "Wrapping up"},
        {"date": "TBA", "event": "Results"},
    ]

    teams = frappe.get_all(
        "FOSS Hackathon Team",
        filters={"hackathon": hackathon_id},
        pluck="name",
    )

    teams_count = len(teams)

    member_count = frappe.db.count(
        "FOSS Hackathon Team Member",
        {
            "parenttype": "FOSS Hackathon Team",
            "parent": ["in", teams],
        },
    )

    # Stats
    context.stats = {
        "prize_pool": "₹ 5,00,000",
        "local_hosts": "10",
        "participants": member_count,
        "teams": teams_count,
    }

    # Get all LocalHosts
    localhosts = frappe.db.get_all(
        "FOSS Hackathon LocalHost",
        filters={"parent_hackathon": hackathon_id},
        fields=["name", "localhost_name", "route", "city", "state", "location"],
        order_by="city, localhost_name",
        page_length=99,
    )

    # Bulk Fetch Counts
    attending_counts = frappe.db.get_all(
        "FOSS Hackathon Participant",
        filters={"localhost_request_status": "Accepted"},
        fields=["localhost", "count(name) as count"],
        group_by="localhost",
    )
    pending_counts = frappe.db.get_all(
        "FOSS Hackathon Participant",
        filters={"localhost_request_status": "Pending"},
        fields=["localhost", "count(name) as count"],
        group_by="localhost",
    )
    likes_counts = frappe.db.get_all(
        "Comment",
        filters={
            "comment_type": "Like",
            "reference_doctype": "FOSS Hackathon LocalHost",
        },
        fields=["reference_name as localhost", "count(name) as count"],
        group_by="reference_name",
    )

    # Convert to dicts
    attending_dict = {item["localhost"]: item["count"] for item in attending_counts}
    pending_dict = {item["localhost"]: item["count"] for item in pending_counts}
    likes_dict = {item["localhost"]: item["count"] for item in likes_counts}

    # Process LocalHosts and group by city
    cities_dict = {}
    for host in localhosts:
        host["route"] = f"/{host.route}"
        host["attending"] = attending_dict.get(host.name, 0)
        host["interested"] = pending_dict.get(host.name, 0) + likes_dict.get(host.name, 0)

        city = host.get("city", "Other")
        if city not in cities_dict:
            cities_dict[city] = []
        cities_dict[city].append(host)

    context.localhosts_by_city = [
        {"city": city, "localhosts": hosts} for city, hosts in sorted(cities_dict.items())
    ]

    # Fetch Sponsors
    context.sponsors = [
        {"tier": tier, "sponsor_list": sponsor_list}
        for tier, sponsor_list in get_event_sponsors(hackathon).items()
    ]

    # Fetch Partners
    context.partners = hackathon.community_partners

    # Volunteers
    context.volunteers = hackathon.get_volunteers()

    # Previous editions (for archive links)
    context.previous_editions = [
        {"year": "2025", "route": "/fosshack/2025"},
        {"year": "2024", "route": "/fosshack/2024"},
        {"year": "2023", "route": "/fosshack/2023"},
        {"year": "2021", "route": "/fosshack/2021"},
        {"year": "2020", "route": "/fosshack/2020"},
    ]

    context.why_participate = [
        "Win up to ₹5,00,000 in cash",
        "Build your reputation as a hacker",
        "Get recognized by recruiters",
        "Grants for your FOSS project",
    ]

    context.rules = [
        "Evaluation based on code commits during the event",
        "No external APIs as core feature",
        "Must have valid FOSS license",
        "Cash prize split at jury's discretion",
        "No blockchain/web3/crypto projects",
    ]

    context.hide_nav = True
    context.hide_footer = True
    context.no_cache = 1

    return context
