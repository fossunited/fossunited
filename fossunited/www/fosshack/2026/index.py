import frappe

from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_PARTNER_PROJECT,
)
from fossunited.fossunited.utils import get_event_sponsors

# TODO: Make this into template to serve data for future hackathon pages?
# same for Indiafoss if we are not using builder for it


def get_context(context):
    """Context for FOSS Hack 2026 page"""

    hackathon_id = frappe.db.get_value(HACKATHON, {"hackathon_name": "FOSS Hack 2026"})

    # Fetch hackathon details
    hackathon = frappe.get_doc(HACKATHON, hackathon_id)
    cities_dict = hackathon.get_localhosts()
    hackathon_stats = hackathon.get_hackathon_stats()

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
        "projects_idea_url": "https://forum.fossunited.org/t/problem-statements-and-ideas-fosshack-2026/7186",
        "status": "Registrations Open"
        if hackathon.is_registration_live
        else "Registrations Closed",
    }

    # Timeline
    context.timeline = [
        {
            "date": "28 February",
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

    context.localhosts_by_city = [
        {"city": city, "localhosts": hosts} for city, hosts in sorted(cities_dict.items())
    ]

    # Fetch Sponsors
    context.sponsors = [
        {"tier": tier, "sponsor_list": sponsor_list}
        for tier, sponsor_list in get_event_sponsors(hackathon.sponsor_list).items()
    ]

    # Fetch Partners
    context.partners = hackathon.community_partners

    context.partner_projects = frappe.get_all(
        HACKATHON_PARTNER_PROJECT,
        {"hackathon": hackathon_id},
        ["repo_link as link", "project_name as sponsor_name", "logo as image"],
        limit_page_length=7,
    )

    # Volunteers
    context.volunteers = hackathon.get_volunteers()

    # Stats
    context.stats = {
        "prize_pool": "₹ 5,00,000",
        "local_hosts": sum(len(hosts) for hosts in cities_dict.values()),
        "participants": hackathon_stats["members"],
        "teams": hackathon_stats["teams"],
        "projects": hackathon_stats["projects"],
        "projects_url": f"/{hackathon.route}/projects/all",
    }

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

    context.rules = hackathon.hackathon_rules

    context.carousel_items = [
        {
            "image": "/assets/fossunited/images/fosshack/doc-img.svg",
            "title": "Documentation",
            "desc": """Help improve documentation for open-source projects — write guides,
            tutorials, READMEs, or API references.""",
        },
        {
            "image": "/assets/fossunited/images/fosshack/data-img.svg",
            "title": "Data",
            "desc": """Contribute datasets (OSMaps), data pipelines, or data analysis
            to open-source projects.""",
        },
        {
            "image": "/assets/fossunited/images/fosshack/design-img.svg",
            "title": "Design",
            "desc": """Improve the user experience and visual design of open-source projects —
            create logos, UI/UX improvements, or design systems.""",
        },
        {
            "image": "/assets/fossunited/images/fosshack/code-img.svg",
            "title": "Code",
            "desc": """Solve issues and make PRs contribution to OSS repositories.""",
        },
    ]

    context.hide_nav = True
    context.hide_footer = True
    context.no_cache = 1

    return context
