import frappe


def get_context(context):
    """Context for FOSS Hack 2026 page"""

    hackathon_id = frappe.db.get_value("FOSS Hackathon", {"hackathon_name": "FOSS Hack 2026"})

    # Fetch hackathon details
    hackathon = frappe.get_doc("FOSS Hackathon", hackathon_id)

    context.doc = hackathon

    context.hackathon = {
        "name": hackathon.hackathon_name,
        "tagline": "India's Largest FOSS Hackathon",
        "date": "March 2026",
        "mode": "Hybrid",
        "description": """
        FOSS Hack 2026 is the sixth edition of FOSS Hack, a hybrid hackathon to promote
        Free and Open Source Software by bringing together students and professionals
        to build or extend FOSS projects""",
        "prize_pool": "₹10,00,000+",
        "register_url": f"/dashboard/register-for-hackathon?id={hackathon_id}",
        "event_page_url": f"/hack/{hackathon.route}",
        "status": "Registrations Open" if hackathon.is_registration_live else "CLosed",
    }

    # Timeline
    context.timeline = [
        {"date": "TBA", "event": "Registrations Closing"},
        {"date": "TBA", "event": "Planning and team formation"},
        {"date": "TBA", "event": "Development"},
        {"date": "TBA", "event": "Wrapping up"},
        {"date": "TBA", "event": "Results"},
    ]

    # Stats
    context.stats = {
        "prize_pool": "₹ TBA",
        "local_hosts": "10",
        "participants": "...",
        "teams": "...",
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
        host["route"] = f"/{l.route}"
        host["attending"] = attending_dict.get(host.name, 0)
        host["interested"] = pending_dict.get(host.name, 0) + likes_dict.get(host.name, 0)

        city = host.get("city", "Other")
        if city not in cities_dict:
            cities_dict[city] = []
        cities_dict[city].append(l)

    context.localhosts_by_city = [
        {"city": city, "localhosts": hosts} for city, hosts in sorted(cities_dict.items())
    ]

    # Fetch Sponsors
    sponsors = frappe.db.get_all(
        "FOSS Event Sponsor",
        filters={"parent": hackathon_id, "parenttype": "FOSS Hackathon"},
        fields=["tier", "custom_tier", "sponsor_name", "link", "image"],
        page_length=99,
    )

    # Organize Sponsors by Tier
    sort_order = {"Platinum": 0, "Gold": 1, "Silver": 2, "Bronze": 3}
    sponsors_dict = {}
    for sponsor in sponsors:
        tier = sponsor.custom_tier if sponsor.tier == "Custom" else sponsor.tier
        sponsors_dict.setdefault(tier, []).append(sponsor)

    context.sponsors = [
        {"tier": tier, "sponsor_list": sponsors_list}
        for tier, sponsors_list in sorted(
            sponsors_dict.items(), key=lambda x: sort_order.get(x[0], float("inf"))
        )
    ]

    # Fetch Partners
    context.partners = frappe.db.get_all(
        "FOSS Event Community Partner",
        filters={"parent": hackathon_id, "parenttype": "FOSS Hackathon"},
        fields=["org_name", "link", "logo"],
        page_length=99,
    )

    # Volunteers
    volunteers = frappe.db.get_all(
        "FOSS Chapter Event Member",
        filters={"parent": hackathon_id, "parenttype": "FOSS Hackathon"},
        pluck="member",
        page_length=999,
    )

    volunteer_profiles = frappe.db.get_all(
        "FOSS User Profile",
        filters={"name": ["in", volunteers]},
        fields=["name", "profile_photo", "bio", "full_name", "route"],
    )

    profile_dict = {profile["name"]: profile for profile in volunteer_profiles}

    context.volunteers = [
        {
            "full_name": profile.get("full_name"),
            "profile_photo": profile.get("profile_photo"),
            "bio": profile.get("bio"),
            "route": f"/{profile.get('route')}",
        }
        for member in volunteers
        if (profile := profile_dict.get(member))
    ]

    # Previous editions (for archive links)
    context.previous_editions = [
        {"year": "2025", "route": "/fosshack/2025"},
        {"year": "2024", "route": "/fosshack/2024"},
        {"year": "2022", "route": "/fosshack/2022"},
        {"year": "2021", "route": "/fosshack/2021"},
        {"year": "2020", "route": "/fosshack/2020"},
    ]

    context.why_participate = [
        "Win up to ₹10 lakhs in cash",
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

    return context
