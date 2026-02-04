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
        FOSS Hack is back for its sixth edition! With the month-long hybrid hackathon,
        we bring together students, professionals and communities to contribute better
        to Free and Open Source software projects. Dive right in!
        """,
        "prize_pool": "₹5,00,000",
        "register_url": f"/dashboard/register-for-hackathon?id={hackathon_id}",
        "event_page_url": f"/{hackathon.route}",
        "projects_idea_url": "https://forum.fossunited.org/t/hackathon-ideas/159",
        "status": "Registrations Open"
        if hackathon.is_registration_live
        else "Opening on Jan 2026",
    }

    # Timeline
    context.timeline = [
        {
            "date": "20 February",
            "event": "Registration",
            "desc": """Register now to express your interest in participating!
            If you are interested in hacking at a localhost, hurry up, because limited spots!""",
        },
        {
            "date": "1-31 March",
            "event": "Create. Contribute. Hack",
            "desc": """Make progress towards your project,
            whether it's a project you're building or an existing project you're contributing to,
            whether you're coding, designing, documenting, testing, etc.<br>
            During this time,
            you can also seek out mentorship and expert advice regarding your work!""",
        },
        {
            "date": "31 March",
            "event": "Last Call",
            "desc": """Wrap up your work in a neat bow - make sure that your project
            has an appropriate description and a demo video.
            If you're writing code,
            make sure to add a link to the source code repository, e.g., GitHub repo.""",
        },
        {
            "date": "4 May",
            "event": "Results",
            "desc": """After multiple rounds of elimination,
            we will be sharing the results on Monday, the 4th of May. Projects will be evaluated
            for novelty, completeness, and relevance. For additional details, please see FAQs.""",
        },
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
    projects_count = frappe.db.count(
        "FOSS Hackathon Project",
        filters={"hackathon": hackathon_id, "is_published": 1},
    )

    # Stats
    context.stats = {
        "prize_pool": "₹ 5,00,000",
        "local_hosts": "10",
        "participants": member_count,
        "teams": teams_count,
        "projects": projects_count,
        "projects_url": f"/{hackathon.route}/projects/all",
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
        "Kickstart your journey into the FOSS ecosystem.",
        "Figure out how you can contribute to the Digital Commons",
        "Access meaningful mentorship and support as you try to solve real-world problems.",
        "All this with a chance to win upto 5 Lakh INR in cash prizes :)",
    ]

    context.rules = [
        "Evaluation based on contributions made during the event duration",
        "Core functionality shouldn't depend on closed-source software or closed/proprietary APIs",
        "Must have valid FOSS license",
        "Cash prize split at jury's discretion",
        "No blockchain/web3/crypto projects",
    ]

    context.hide_nav = True
    context.hide_footer = True
    context.no_cache = 1

    return context
