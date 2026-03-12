"""
FOSSHACK Results Data Structure
Manual data for 2020, 2021, 2023
Fetched data for 2024, 2025, 2026 and ++
"""

import frappe
from frappe.utils import formatdate

from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_PARTICIPANT,
    HACKATHON_PARTNER_PROJECT,
    HACKATHON_PROJECT,
    HACKATHON_TEAM,
)

ARCHIVE_HACKATHONS = {
    "2020": {
        "id": "2020",
        "name": "FOSS Hack 2020",
        "date": "12-13 September 2020",
        "year": "2020",
        "mode": "Virtual",
        "total_teams": 150,
        "total_participants": None,
        "project_submissions": 147,
        "partner_projects": None,
        "route": "/fosshack/2020",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2020-results/424",
        "projects": [
            {
                "name": "Fika",
                "url": "https://github.com/fika-lang/fika",
                "description": "A statically typed, web-first programming language that runs on BEAM (Erlang VM). Aims to lower the entry barrier to the Erlang ecosystem with simplified syntax.",
                "cash_prize": "₹5,00,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Emil Soman", "avatar": ""},
                ],
            },
            {
                "name": "Untab",
                "url": "https://github.com/blenderskool/untab",
                "description": "A productivity tool that's immediately useful to a wide audience. Well designed and feature-complete with good UX and UI.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Akash Hamirwasia", "avatar": ""},
                ],
            },
            {
                "name": "MergePro",
                "url": "https://github.com/abinator-1308/MergePRo",
                "description": "A developer productivity tool that helps manage GitHub PRs inside a browser extension widget. Immediately useful and feature-complete.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Abhinav Singh", "avatar": ""},
                    {"name": "Arjita Chaurasia", "avatar": ""},
                ],
            },
            {
                "name": "BrainTree",
                "url": "https://github.com/gargakshit/braintree",
                "description": "A stand-alone, local, note taking and mind-map tool with a clean UI and good UX, packaged nicely as an MVP.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Akshit Garg", "avatar": ""},
                ],
            },
            {
                "name": "ebb",
                "url": "https://github.com/liyasthomas/ebb",
                "description": "An app that aims at helping manage stress and anxiety via personal tasks and goals. An interesting hypothesis presented as a polished, complete product.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Liyas Thomas", "avatar": ""},
                    {"name": "Andrew Bastin", "avatar": ""},
                ],
            },
            {
                "name": "Privacy Indicator App",
                "url": "https://github.com/NitishGadangi/Privacy-Indicator-App",
                "description": "An app that notifies the user of camera and microphone use on Android. Immediately useful, and addresses an important privacy and security issue.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Nitish Gadangi", "avatar": ""},
                ],
            },
            {
                "name": "Dalal",
                "url": "https://github.com/ghostwriternr/dalal",
                "description": "An app for receiving, transforming, and forwarding HTTP requests with a simple UI, and a publicly hosted live version.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Naresh Ramesh", "avatar": ""},
                    {"name": "Mukul Chaware", "avatar": ""},
                    {"name": "Shubham Jain", "avatar": ""},
                ],
            },
            {
                "name": "Rumqtt",
                "url": "https://github.com/bytebeamio/rumqtt/tree/mqtt5",
                "description": "Added MQTT5 support to the Rust MQTT library, a great value addition to the Rust ecosystem.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Ravi Teja", "avatar": ""},
                ],
            },
            {
                "name": "lazykubernetes",
                "url": "https://github.com/yolossn/lazykubernetes",
                "description": "A developer productivity CUI tool for managing K8s clusters. Solves a specific DevOps UX problem with a nice command line UI.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Santhosh Nagaraj", "avatar": ""},
                    {"name": "Nityananda Gohain", "avatar": ""},
                    {"name": "Gnanesh Kunal", "avatar": ""},
                ],
            },
            {
                "name": "Userly",
                "url": "https://github.com/userly-tools/userly-tools",
                "description": "A self-hosted app for conducting and managing user surveys and research.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Rohan Rajpal", "avatar": ""},
                    {"name": "Avi Garg", "avatar": ""},
                    {"name": "Royal Tomar", "avatar": ""},
                    {"name": "Srijan Jain", "avatar": ""},
                ],
            },
            {
                "name": "Zettel",
                "url": "https://github.com/hackstream/zettel",
                "description": "A self-hosted note taking and publishing tool.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Karan Sharma", "avatar": ""},
                    {"name": "Sarat Chandra", "avatar": ""},
                ],
            },
            {
                "name": "Yet Another Chess Engine",
                "url": "https://github.com/adityahase/chess",
                "description": "A clever, tiny chess engine that lets humans win. Comes with a nice playable UI.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Aditya Hase", "avatar": ""},
                    {"name": "Saqib Ansari", "avatar": ""},
                ],
            },
            {
                "name": "ScanIn",
                "url": "https://github.com/hackyguru/ScanIn",
                "description": "A fully local Android application for scanning and managing documents.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Kumaraguru", "avatar": ""},
                    {"name": "Emma Thomas", "avatar": ""},
                    {"name": "Dhanush Vardhan Kalaiselvan", "avatar": ""},
                    {"name": "Mridula Kalaiselvan", "avatar": ""},
                ],
            },
            {
                "name": "Markd",
                "url": "https://github.com/scmmishra/markd",
                "description": "A self-hosted bookmarking app with a nice UI.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Shivam Mishra", "avatar": ""},
                ],
            },
        ],
    },
    "2021": {
        "id": "2021",
        "name": "FOSS Hack 2021",
        "date": "13-14 November 2021",
        "year": "2021",
        "mode": "Virtual",
        "total_teams": 120,
        "total_participants": None,
        "project_submissions": 120,
        "partner_projects": None,
        "route": "/fosshack/2021",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2021-results/957",
        "projects": [
            {
                "name": "mquictt",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=grpc-quick-rs",
                "description": "A Rust library for MQTT over QUIC, leveraging the concurrent streams of QUIC to multiplex the MQTT publishes and subscribes within separate streams per topic.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Abhik Jain", "avatar": ""},
                    {"name": "Devdutt Shenoi", "avatar": ""},
                ],
            },
            {
                "name": "Varnam Input Method for Mac",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Type%20Indian%20Languages%20natively%20on%20Mac",
                "description": "Easily type Indian languages on any app in Mac natively using the Varnam transliteration engine.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Subin Siby", "avatar": ""},
                ],
            },
            {
                "name": "Diode",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Diode%20%F0%9F%94%8C",
                "description": "An easy to use API proxy to hide your API secrets and add common middlewares without implementing a backend.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Akash Hamirwasia", "avatar": ""},
                ],
            },
            {
                "name": "DigiStore",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=DigiStore",
                "description": "A self-hostable platform to list and sell digital assets like e-books, audio etc. Open Source Gumroad!",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Hussain Nagaria", "avatar": ""},
                ],
            },
            {
                "name": "OpenAuthenticator",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=OpenAuthenticator",
                "description": "A simple open-source, cross-platform, TOTP-based Authenticator for desktop.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Pranit Chadda", "avatar": ""},
                    {"name": "Aaryak Garg", "avatar": ""},
                    {"name": "Arsh Kohli", "avatar": ""},
                    {"name": "Paarth Chhabra", "avatar": ""},
                ],
            },
            {
                "name": "KnowledgeBase.Tech",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Knowledge+Base",
                "description": "Modern open-source knowledge base using markdown.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Gigin Chandy George", "avatar": ""},
                    {"name": "Vinu TV", "avatar": ""},
                    {"name": "Vignesh Hari", "avatar": ""},
                    {"name": "Bodhish Thomas", "avatar": ""},
                ],
            },
            {
                "name": "epub2sphinx",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=epub2sphinx",
                "description": "Tool to convert epub file to ReST files for Sphinx.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Allwin Raju", "avatar": ""},
                    {"name": "Nihaal", "avatar": ""},
                    {"name": "Aswin C", "avatar": ""},
                    {"name": "Aravindhan Pugazhendhi", "avatar": ""},
                ],
            },
            {
                "name": "Planarity",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Planarity",
                "description": "A puzzle: Arrange the given graph such that the edges intersect only at the vertices.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Asmita Hase", "avatar": ""},
                ],
            },
            {
                "name": "Canned Analytics in Avni",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Canned+Analytics+in+Avni",
                "description": "Introduce canned analytics in the field work and data collection platform Avni so that users get some basic reports and insights out of the box.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Vinod Deolal", "avatar": ""},
                    {"name": "Vinay Venu", "avatar": ""},
                    {"name": "Arjun Khandelwal", "avatar": ""},
                ],
            },
            {
                "name": "Joy(x)p5js",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Joy(x)p5js",
                "description": "Providing joy, a tiny creative coding library, as a port to p5.js.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Anushka Trivedi", "avatar": ""},
                ],
            },
            {
                "name": "GramUp",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=GramUp",
                "description": "A lightweight python program to backup your files using unlimited cloud backup via Telegram.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "sunithvs", "avatar": ""},
                    {"name": "SANU MUHAMMED C", "avatar": ""},
                    {"name": "Rohit T P", "avatar": ""},
                ],
            },
            {
                "name": "Certificates Ninja",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Certificates+Ninja",
                "description": "A free and open-source web application for event organizers to easily create immutable and tamper resistant certificates powered by Blockchain and NFTs.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Adithya Menon S", "avatar": ""},
                    {"name": "Bhuvanesh T G", "avatar": ""},
                    {"name": "Kumaraguru", "avatar": ""},
                ],
            },
            {
                "name": "Cuckoo Dooku",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Count+Cuckoo",
                "description": "A browser alert extension that helps you develop a healthy work routine. Reminds you to chill out, stretch, drink water and be the best version of yourself.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Vignesh Palanisamy", "avatar": ""},
                    {"name": "Omkar Pote", "avatar": ""},
                    {"name": "Raghav Singhal", "avatar": ""},
                ],
            },
            {
                "name": "Rabbit Hole v2",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Rabbit+Hole+v2",
                "description": "A browser extension that tracks your journey through Wikipedia to create a map of your knowledge base.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Anirudh Varma", "avatar": ""},
                ],
            },
            {
                "name": "dtcalc",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=dtdiff",
                "description": "A command line tool written in Python to find the difference between dates.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"name": "Julin Shaji", "avatar": ""},
                ],
            },
        ],
    },
    "2023": {
        "id": "2023",
        "name": "FOSS Hack 3.0",
        "date": "4th-5th March 2023",
        "year": "2023",
        "mode": "Hybrid",
        "total_teams": 196,
        "total_participants": None,
        "project_submissions": 187,
        "partner_projects": 12,
        "route": "/fosshack/2023",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-3-0-results/1882",
        "projects": [
            {
                "name": "Helios",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Helios",
                "description": "A 6-degree-of-freedom rocket model simulation that accurately models the motion of a rocket in flight, taking into account atmospheric conditions, turbulence, and aerodynamic parameters.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Ronan", "avatar": ""},
                    {"name": "Darpan", "avatar": ""},
                    {"name": "Ashwin", "avatar": ""},
                ],
            },
            {
                "name": "Raven",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Raven",
                "description": "A simple, open-source team messaging platform similar to Slack. Built using the Frappe framework and can be installed in existing Frappe/ERPNext instances.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Nikhil", "avatar": ""},
                    {"name": "Aditya", "avatar": ""},
                    {"name": "Janhvi", "avatar": ""},
                ],
            },
            {
                "name": "API Dash",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=API%20Dash",
                "description": "A cross-platform HTTP Client that can help you explore APIs.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Ankit", "avatar": ""},
                    {"name": "Ashita", "avatar": ""},
                ],
            },
            {
                "name": "DISS-lexia",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=DISS-LEXIA",
                "description": "A Chrome extension for those suffering from Dyslexia to read websites easily.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Maheswaran", "avatar": ""},
                    {"name": "Avinash", "avatar": ""},
                    {"name": "Joel", "avatar": ""},
                ],
            },
            {
                "name": "VSCode Advanced Search",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=VS%20Code%20Advanced%20Search",
                "description": "A VS Code extension that allows users to do a structured search on the code and replace it.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Shivendu", "avatar": ""},
                    {"name": "Abhinav", "avatar": ""},
                    {"name": "Ambar", "avatar": ""},
                ],
            },
            {
                "name": "Quick-Wictionary",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Quick-Wiktionary",
                "description": "Browser extension to get the meaning of a selected word from Wiktionary.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Keerthana", "avatar": ""},
                    {"name": "Prabakaran", "avatar": ""},
                    {"name": "Ram", "avatar": ""},
                    {"name": "Soundarya", "avatar": ""},
                ],
            },
            {
                "name": "Open Assistant Safety Team",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=OpenAssistant%20-%20Safety%20Team",
                "description": "Datasets to build a safety model for OpenAssistant (an open-source alternative to ChatGPT). Flags potentially malicious user requests.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Jithin", "avatar": ""},
                    {"name": "Shahul", "avatar": ""},
                ],
            },
            {
                "name": "Kukkee",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Kukkee",
                "description": "A meeting poll tool.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Anand", "avatar": ""},
                ],
            },
            {
                "name": "Snipd",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=snipd",
                "description": "Browser extension to annotate and organize notes, articles, and PDF files across multiple web pages.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Alaap", "avatar": ""},
                    {"name": "Chanakya", "avatar": ""},
                    {"name": "Yathin", "avatar": ""},
                    {"name": "Aditya", "avatar": ""},
                ],
            },
            {
                "name": "Waymond",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=waymond",
                "description": "Monitors the number of docker containers running for a given spec and manages containers similar to Kubernetes. Implemented in Go.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Vishnu", "avatar": ""},
                ],
            },
            {
                "name": "Spell4wiki",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Spell4Wiki",
                "description": "Mobile app for uploading audio files to Wikimedia commons and Wiktionary-based multilingual dictionary.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Manimaran", "avatar": ""},
                    {"name": "Kanagasabapathy", "avatar": ""},
                    {"name": "Seenuvasan", "avatar": ""},
                ],
            },
            {
                "name": "Vizhi Tamil",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=VizhiTamil",
                "description": "Android application for visually impaired individuals.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Khaleel", "avatar": ""},
                    {"name": "Hari", "avatar": ""},
                    {"name": "Vignesh", "avatar": ""},
                    {"name": "Ponneelan", "avatar": ""},
                ],
            },
            {
                "name": "Wiki-Bulky",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Wiki-Bulky",
                "description": "Bulk download of media files from Wikimedia commons & Bulk upload of words with meaning to Wiktionary.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Viji", "avatar": ""},
                    {"name": "Kowsalya", "avatar": ""},
                    {"name": "Deepak", "avatar": ""},
                    {"name": "Dilip", "avatar": ""},
                ],
            },
            {
                "name": "DNArchery",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=DNArchery",
                "description": "A DNA Sequencing/Visualization software for bioinformatics research.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Mufeed", "avatar": ""},
                    {"name": "Vivek", "avatar": ""},
                    {"name": "Vishal", "avatar": ""},
                ],
            },
            {
                "name": "Cherava",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Cherava",
                "description": "Zero code web scraping automation tool.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Roshan", "avatar": ""},
                    {"name": "Sudev", "avatar": ""},
                    {"name": "Ajay", "avatar": ""},
                ],
            },
            {
                "name": "Adding QUIC as transport for rumqtt",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Adding%20QUIC%20as%20transport%20for%20rumqtt",
                "description": "The MQTT ecosystem in rust with QUIC transport support.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"name": "Devdutt Shenoi", "avatar": ""},
                ],
            },
        ],
    },
}

# Forum post URLs for each year
ANNOUNCEMENTS = {
    "2020": "https://forum.fossunited.org/t/foss-hack-2020-results/424",
    "2021": "https://forum.fossunited.org/t/foss-hack-2021-results/957",
    "2023": "https://forum.fossunited.org/t/foss-hack-3-0-results/1882",
    "2024": "https://forum.fossunited.org/t/foss-hack-2024-results/3964",
    "2025": "https://forum.fossunited.org/t/foss-hack-2025-results/5541",
}


def get_hackathon_results(hackathon_id, year):
    """
    Fetch hackathon data from database for a specific year
    """
    # Fetch hackathon details
    hackathon = frappe.get_doc(HACKATHON, hackathon_id)

    if not hackathon:
        return None

    # Get results from child table
    results = hackathon.get("results", [])

    # Build projects list
    projects = []
    for result in results:
        # Fetch project details
        if not result.project or not frappe.db.exists(HACKATHON_PROJECT, result.project):
            continue
        project_doc = frappe.get_doc(HACKATHON_PROJECT, result.project) if result.project else None
        team_doc = frappe.get_doc(HACKATHON_TEAM, result.team) if result.team else None

        # Get team members
        team_members = []
        if team_doc:
            team_members = project_doc.get_team_members(team_doc)

        # Build project dict
        project = {
            "name": project_doc.title or project_doc.name,
            "url": project_doc.route,
            "description": project_doc.short_description or "",
            "cash_prize": frappe.format_value(result.cash_prize, {"fieldtype": "Currency"})
            if result.cash_prize
            else None,
            "status": result.status,
            "team_members": team_members,
            "repo_link": project_doc.repo_link,
        }

        projects.append(project)

    # Build hackathon dict
    hackathon_data = {
        "id": year,
        "year": year,
        "name": hackathon.hackathon_name or f"FOSS Hack {year}",
        "date": f"{formatdate(hackathon.start_date, 'd')} – {formatdate(hackathon.end_date, 'd MMM yyyy')}",
        "mode": hackathon.hackathon_type or "Hybrid",
        "total_teams": frappe.db.count(HACKATHON_TEAM, {"hackathon": hackathon_id}),
        "total_participants": frappe.db.count(HACKATHON_PARTICIPANT, {"hackathon": hackathon_id}),
        "project_submissions": frappe.db.count(HACKATHON_PROJECT, {"hackathon": hackathon_id}),
        "partner_projects": frappe.db.count(
            HACKATHON_PARTNER_PROJECT, {"hackathon": hackathon_id}
        ),
        "route": hackathon.external_website_url or f"/fosshack/{year}",
        "projects": projects,
        "forum_post": ANNOUNCEMENTS.get(year),
    }

    return hackathon_data


def get_all_hackathon_results():
    """
    Get all hackathon results - manual data for 2020, 2021, 2023
    and fetched data for 2024, 2025, 2026
    """
    hackathons = []

    # Add manual data
    for year in ["2020", "2021", "2023"]:
        hackathons.append(ARCHIVE_HACKATHONS[year])

    # # Fetch from database
    for hack in frappe.get_all(HACKATHON, ["name", "start_date"]):
        event_year = str(hack.start_date.year)
        hackathon_data = get_hackathon_results(hack.name, event_year)
        if hackathon_data:
            hackathons.append(hackathon_data)

    # Sort by year descending
    hackathons.sort(key=lambda x: x["id"], reverse=True)

    return hackathons


def get_context(context):
    """
    Context for the results page
    """
    context.hackathons = get_all_hackathon_results()
    context.hide_nav = True

    return context
