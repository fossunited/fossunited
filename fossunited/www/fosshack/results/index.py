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
    HACKATHON_TEAM_MEMBER,
)

ARCHIVE_HACKATHONS = {
    "2020": {
        "id": "2020",
        "name": "FOSS Hack 2020",
        "date": "12-13 September 2020",
        "year": "2020",
        "mode": "Virtual",
        "total_teams": 150,
        "total_participants": 3384,
        "project_submissions": 147,
        "partner_projects": None,
        "community_partners": 22,
        "route": "https://fossunited.org/fosshack/2020",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2020-results/424",
        "partner_project_url": None,
        "projects_url": "https://archive.fossunited.org/fosshack/2020/projects",
        "projects": [
            {
                "name": "Fika",
                "url": "https://github.com/fika-lang/fika",
                "description": "A statically typed, web-first programming language that runs on BEAM (Erlang VM). Aims to lower the entry barrier to the Erlang ecosystem with simplified syntax.",
                "cash_prize": "₹5,00,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Emil Soman", "profile_photo": ""},
                ],
            },
            {
                "name": "Untab",
                "url": "https://github.com/blenderskool/untab",
                "description": "A productivity tool that's immediately useful to a wide audience. Well designed and feature-complete with good UX and UI.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Akash Hamirwasia", "profile_photo": ""},
                ],
            },
            {
                "name": "MergePro",
                "url": "https://github.com/abinator-1308/MergePRo",
                "description": "A developer productivity tool that helps manage GitHub PRs inside a browser extension widget. Immediately useful and feature-complete.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Abhinav Singh", "profile_photo": ""},
                    {"full_name": "Arjita Chaurasia", "profile_photo": ""},
                ],
            },
            {
                "name": "BrainTree",
                "url": "https://github.com/gargakshit/braintree",
                "description": "A stand-alone, local, note taking and mind-map tool with a clean UI and good UX, packaged nicely as an MVP.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Akshit Garg", "profile_photo": ""},
                ],
            },
            {
                "name": "ebb",
                "url": "https://github.com/liyasthomas/ebb",
                "description": "An app that aims at helping manage stress and anxiety via personal tasks and goals. An interesting hypothesis presented as a polished, complete product.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Liyas Thomas", "profile_photo": ""},
                    {"full_name": "Andrew Bastin", "profile_photo": ""},
                ],
            },
            {
                "name": "Privacy Indicator App",
                "url": "https://github.com/NitishGadangi/Privacy-Indicator-App",
                "description": "An app that notifies the user of camera and microphone use on Android. Immediately useful, and addresses an important privacy and security issue.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Nitish Gadangi", "profile_photo": ""},
                ],
            },
            {
                "name": "Dalal",
                "url": "https://github.com/ghostwriternr/dalal",
                "description": "An app for receiving, transforming, and forwarding HTTP requests with a simple UI, and a publicly hosted live version.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Naresh Ramesh", "profile_photo": ""},
                    {"full_name": "Mukul Chaware", "profile_photo": ""},
                    {"full_name": "Shubham Jain", "profile_photo": ""},
                ],
            },
            {
                "name": "Rumqtt",
                "url": "https://github.com/bytebeamio/rumqtt/tree/mqtt5",
                "description": "Added MQTT5 support to the Rust MQTT library, a great value addition to the Rust ecosystem.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Ravi Teja", "profile_photo": ""},
                ],
            },
            {
                "name": "lazykubernetes",
                "url": "https://github.com/yolossn/lazykubernetes",
                "description": "A developer productivity CUI tool for managing K8s clusters. Solves a specific DevOps UX problem with a nice command line UI.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Santhosh Nagaraj", "profile_photo": ""},
                    {"full_name": "Nityananda Gohain", "profile_photo": ""},
                    {"full_name": "Gnanesh Kunal", "profile_photo": ""},
                ],
            },
            {
                "name": "Userly",
                "url": "https://github.com/userly-tools/userly-tools",
                "description": "A self-hosted app for conducting and managing user surveys and research.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Rohan Rajpal", "profile_photo": ""},
                    {"full_name": "Avi Garg", "profile_photo": ""},
                    {"full_name": "Royal Tomar", "profile_photo": ""},
                    {"full_name": "Srijan Jain", "profile_photo": ""},
                ],
            },
            {
                "name": "Zettel",
                "url": "https://github.com/hackstream/zettel",
                "description": "A self-hosted note taking and publishing tool.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Karan Sharma", "profile_photo": ""},
                    {"full_name": "Sarat Chandra", "profile_photo": ""},
                ],
            },
            {
                "name": "Yet Another Chess Engine",
                "url": "https://github.com/adityahase/chess",
                "description": "A clever, tiny chess engine that lets humans win. Comes with a nice playable UI.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Aditya Hase", "profile_photo": ""},
                    {"full_name": "Saqib Ansari", "profile_photo": ""},
                ],
            },
            {
                "name": "ScanIn",
                "url": "https://github.com/hackyguru/ScanIn",
                "description": "A fully local Android application for scanning and managing documents.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Kumaraguru", "profile_photo": ""},
                    {"full_name": "Emma Thomas", "profile_photo": ""},
                    {"full_name": "Dhanush Vardhan Kalaiselvan", "profile_photo": ""},
                    {"full_name": "Mridula Kalaiselvan", "profile_photo": ""},
                ],
            },
            {
                "name": "Markd",
                "url": "https://github.com/scmmishra/markd",
                "description": "A self-hosted bookmarking app with a nice UI.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Shivam Mishra", "profile_photo": ""},
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
        "total_participants": 1302,
        "project_submissions": 120,
        "partner_projects": None,
        "route": "https://fossunited.org/fosshack/2021",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2021-results/957",
        "partner_project_url": None,
        "projects_url": "https://archive.fossunited.org/fosshack/2021/projects",
        "projects": [
            {
                "name": "mquictt",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=grpc-quick-rs",
                "description": "A Rust library for MQTT over QUIC, leveraging the concurrent streams of QUIC to multiplex the MQTT publishes and subscribes within separate streams per topic.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Abhik Jain", "profile_photo": ""},
                    {"full_name": "Devdutt Shenoi", "profile_photo": ""},
                ],
            },
            {
                "name": "Varnam Input Method for Mac",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Type%20Indian%20Languages%20natively%20on%20Mac",
                "description": "Easily type Indian languages on any app in Mac natively using the Varnam transliteration engine.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Subin Siby", "profile_photo": ""},
                ],
            },
            {
                "name": "Diode",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Diode%20%F0%9F%94%8C",
                "description": "An easy to use API proxy to hide your API secrets and add common middlewares without implementing a backend.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Akash Hamirwasia", "profile_photo": ""},
                ],
            },
            {
                "name": "DigiStore",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=DigiStore",
                "description": "A self-hostable platform to list and sell digital assets like e-books, audio etc. Open Source Gumroad!",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Hussain Nagaria", "profile_photo": ""},
                ],
            },
            {
                "name": "OpenAuthenticator",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=OpenAuthenticator",
                "description": "A simple open-source, cross-platform, TOTP-based Authenticator for desktop.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Pranit Chadda", "profile_photo": ""},
                    {"full_name": "Aaryak Garg", "profile_photo": ""},
                    {"full_name": "Arsh Kohli", "profile_photo": ""},
                    {"full_name": "Paarth Chhabra", "profile_photo": ""},
                ],
            },
            {
                "name": "KnowledgeBase.Tech",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Knowledge+Base",
                "description": "Modern open-source knowledge base using markdown.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Gigin Chandy George", "profile_photo": ""},
                    {"full_name": "Vinu TV", "profile_photo": ""},
                    {"full_name": "Vignesh Hari", "profile_photo": ""},
                    {"full_name": "Bodhish Thomas", "profile_photo": ""},
                ],
            },
            {
                "name": "epub2sphinx",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=epub2sphinx",
                "description": "Tool to convert epub file to ReST files for Sphinx.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Allwin Raju", "profile_photo": ""},
                    {"full_name": "Nihaal", "profile_photo": ""},
                    {"full_name": "Aswin C", "profile_photo": ""},
                    {"full_name": "Aravindhan Pugazhendhi", "profile_photo": ""},
                ],
            },
            {
                "name": "Planarity",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Planarity",
                "description": "A puzzle: Arrange the given graph such that the edges intersect only at the vertices.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Asmita Hase", "profile_photo": ""},
                ],
            },
            {
                "name": "Canned Analytics in Avni",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Canned+Analytics+in+Avni",
                "description": "Introduce canned analytics in the field work and data collection platform Avni so that users get some basic reports and insights out of the box.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Vinod Deolal", "profile_photo": ""},
                    {"full_name": "Vinay Venu", "profile_photo": ""},
                    {"full_name": "Arjun Khandelwal", "profile_photo": ""},
                ],
            },
            {
                "name": "Joy(x)p5js",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Joy(x)p5js",
                "description": "Providing joy, a tiny creative coding library, as a port to p5.js.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Anushka Trivedi", "profile_photo": ""},
                ],
            },
            {
                "name": "GramUp",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=GramUp",
                "description": "A lightweight python program to backup your files using unlimited cloud backup via Telegram.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "sunithvs", "profile_photo": ""},
                    {"full_name": "SANU MUHAMMED C", "profile_photo": ""},
                    {"full_name": "Rohit T P", "profile_photo": ""},
                ],
            },
            {
                "name": "Certificates Ninja",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Certificates+Ninja",
                "description": "A free and open-source web application for event organizers to easily create immutable and tamper resistant certificates powered by Blockchain and NFTs.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Adithya Menon S", "profile_photo": ""},
                    {"full_name": "Bhuvanesh T G", "profile_photo": ""},
                    {"full_name": "Kumaraguru", "profile_photo": ""},
                ],
            },
            {
                "name": "Cuckoo Dooku",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Count+Cuckoo",
                "description": "A browser alert extension that helps you develop a healthy work routine. Reminds you to chill out, stretch, drink water and be the best version of yourself.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Vignesh Palanisamy", "profile_photo": ""},
                    {"full_name": "Omkar Pote", "profile_photo": ""},
                    {"full_name": "Raghav Singhal", "profile_photo": ""},
                ],
            },
            {
                "name": "Rabbit Hole v2",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=Rabbit+Hole+v2",
                "description": "A browser extension that tracks your journey through Wikipedia to create a map of your knowledge base.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Anirudh Varma", "profile_photo": ""},
                ],
            },
            {
                "name": "dtcalc",
                "url": "https://archive.fossunited.org/fosshack/2021/project?project=dtdiff",
                "description": "A command line tool written in Python to find the difference between dates.",
                "cash_prize": None,
                "status": "Commendation",
                "team_members": [
                    {"full_name": "Julin Shaji", "profile_photo": ""},
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
        "total_participants": 1014,
        "project_submissions": 187,
        "partner_projects": 12,
        "community_partners": 30,
        "route": "https://fossunited.org/fosshack/2023",
        "forum_post": "https://forum.fossunited.org/t/foss-hack-3-0-results/1882",
        "partner_project_url": "https://archive.fossunited.org/fosshack/2023/partner-projects-list",
        "projects_url": "https://archive.fossunited.org/fosshack/2023/projects",
        "projects": [
            {
                "name": "Helios",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Helios",
                "description": "A 6-degree-of-freedom rocket model simulation that accurately models the motion of a rocket in flight, taking into account atmospheric conditions, turbulence, and aerodynamic parameters.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Ronan", "profile_photo": ""},
                    {"full_name": "Darpan", "profile_photo": ""},
                    {"full_name": "Ashwin", "profile_photo": ""},
                ],
            },
            {
                "name": "Raven",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Raven",
                "description": "A simple, open-source team messaging platform similar to Slack. Built using the Frappe framework and can be installed in existing Frappe/ERPNext instances.",
                "cash_prize": "₹1,00,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Nikhil", "profile_photo": ""},
                    {"full_name": "Aditya", "profile_photo": ""},
                    {"full_name": "Janhvi", "profile_photo": ""},
                ],
            },
            {
                "name": "API Dash",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=API%20Dash",
                "description": "A cross-platform HTTP Client that can help you explore APIs.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Ankit", "profile_photo": ""},
                    {"full_name": "Ashita", "profile_photo": ""},
                ],
            },
            {
                "name": "DISS-lexia",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=DISS-LEXIA",
                "description": "A Chrome extension for those suffering from Dyslexia to read websites easily.",
                "cash_prize": "₹50,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Maheswaran", "profile_photo": ""},
                    {"full_name": "Avinash", "profile_photo": ""},
                    {"full_name": "Joel", "profile_photo": ""},
                ],
            },
            {
                "name": "VSCode Advanced Search",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=VS%20Code%20Advanced%20Search",
                "description": "A VS Code extension that allows users to do a structured search on the code and replace it.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Shivendu", "profile_photo": ""},
                    {"full_name": "Abhinav", "profile_photo": ""},
                    {"full_name": "Ambar", "profile_photo": ""},
                ],
            },
            {
                "name": "Quick-Wictionary",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Quick-Wiktionary",
                "description": "Browser extension to get the meaning of a selected word from Wiktionary.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Keerthana", "profile_photo": ""},
                    {"full_name": "Prabakaran", "profile_photo": ""},
                    {"full_name": "Ram", "profile_photo": ""},
                    {"full_name": "Soundarya", "profile_photo": ""},
                ],
            },
            {
                "name": "Open Assistant Safety Team",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=OpenAssistant%20-%20Safety%20Team",
                "description": "Datasets to build a safety model for OpenAssistant (an open-source alternative to ChatGPT). Flags potentially malicious user requests.",
                "cash_prize": "₹25,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Jithin", "profile_photo": ""},
                    {"full_name": "Shahul", "profile_photo": ""},
                ],
            },
            {
                "name": "Kukkee",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Kukkee",
                "description": "A meeting poll tool.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Anand", "profile_photo": ""},
                ],
            },
            {
                "name": "Snipd",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=snipd",
                "description": "Browser extension to annotate and organize notes, articles, and PDF files across multiple web pages.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Alaap", "profile_photo": ""},
                    {"full_name": "Chanakya", "profile_photo": ""},
                    {"full_name": "Yathin", "profile_photo": ""},
                    {"full_name": "Aditya", "profile_photo": ""},
                ],
            },
            {
                "name": "Waymond",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=waymond",
                "description": "Monitors the number of docker containers running for a given spec and manages containers similar to Kubernetes. Implemented in Go.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Vishnu", "profile_photo": ""},
                ],
            },
            {
                "name": "Spell4wiki",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Spell4Wiki",
                "description": "Mobile app for uploading audio files to Wikimedia commons and Wiktionary-based multilingual dictionary.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Manimaran", "profile_photo": ""},
                    {"full_name": "Kanagasabapathy", "profile_photo": ""},
                    {"full_name": "Seenuvasan", "profile_photo": ""},
                ],
            },
            {
                "name": "Vizhi Tamil",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=VizhiTamil",
                "description": "Android application for visually impaired individuals.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Khaleel", "profile_photo": ""},
                    {"full_name": "Hari", "profile_photo": ""},
                    {"full_name": "Vignesh", "profile_photo": ""},
                    {"full_name": "Ponneelan", "profile_photo": ""},
                ],
            },
            {
                "name": "Wiki-Bulky",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Wiki-Bulky",
                "description": "Bulk download of media files from Wikimedia commons & Bulk upload of words with meaning to Wiktionary.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Viji", "profile_photo": ""},
                    {"full_name": "Kowsalya", "profile_photo": ""},
                    {"full_name": "Deepak", "profile_photo": ""},
                    {"full_name": "Dilip", "profile_photo": ""},
                ],
            },
            {
                "name": "DNArchery",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=DNArchery",
                "description": "A DNA Sequencing/Visualization software for bioinformatics research.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Mufeed", "profile_photo": ""},
                    {"full_name": "Vivek", "profile_photo": ""},
                    {"full_name": "Vishal", "profile_photo": ""},
                ],
            },
            {
                "name": "Cherava",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Cherava",
                "description": "Zero code web scraping automation tool.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Roshan", "profile_photo": ""},
                    {"full_name": "Sudev", "profile_photo": ""},
                    {"full_name": "Ajay", "profile_photo": ""},
                ],
            },
            {
                "name": "Adding QUIC as transport for rumqtt",
                "url": "https://archive.fossunited.org/fosshack/2023/project?project=Adding%20QUIC%20as%20transport%20for%20rumqtt",
                "description": "The MQTT ecosystem in rust with QUIC transport support.",
                "cash_prize": "₹10,000",
                "status": "Winner",
                "team_members": [
                    {"full_name": "Devdutt Shenoi", "profile_photo": ""},
                ],
            },
        ],
    },
}

HACKATHON_URLS = {
    "2024": {
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2024-results/3964",
        "partner_project_url": "https://fossunited.org/fh24/partner-projects",
        "projects_url": "https://fossunited.org/hack/fosshack24/projects/all",
    },
    "2025": {
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2025-results/5541",
        "partner_project_url": "https://fossunited.org/fosshack/2025/partner-projects",
        "projects_url": "https://fossunited.org/hack/fosshack25/projects/all",
    },
    "2026": {
        "forum_post": "https://forum.fossunited.org/t/foss-hack-2026-results/8094",
        "partner_project_url": "https://fossunited.org/fosshack/2026/partner-projects",
        "projects_url": "https://fossunited.org/hack/fosshack26/projects/all",
    },
}


def get_hackathon_results(hackathon_id, year):
    hackathon = frappe.get_doc(HACKATHON, hackathon_id)

    if not hackathon:
        return None

    results = hackathon.get("results", [])
    if not results:
        return _build_hackathon_data(hackathon, year, projects=[])

    project_names = [r.project for r in results if r.project]
    team_names = [r.team for r in results if r.team]

    projects_by_name = {
        p.name: p
        for p in frappe.get_all(
            HACKATHON_PROJECT,
            filters={"name": ["in", project_names]},
            fields=[
                "name",
                "title",
                "route",
                "short_description",
                "repo_link",
                "team_name",
                "is_contribution_project",
                "partner_project.project_name as partner_project_name",
                "partner_project.route as partner_project_route",
            ],
        )
    }

    raw_members = (
        frappe.get_all(
            HACKATHON_TEAM_MEMBER,
            filters={"parent": ["in", team_names]},
            fields=["parent as team", "member"],
        )
        if team_names
        else []
    )

    participant_names = [m.member for m in raw_members]
    profiles_by_participant = (
        {
            p.name: p
            for p in frappe.get_all(
                HACKATHON_PARTICIPANT,
                filters={"name": ["in", participant_names]},
                fields=[
                    "name",
                    "user_profile.full_name as full_name",
                    "user_profile.username as username",
                    "user_profile.route as route",
                    "user_profile.profile_photo as profile_photo",
                ],
            )
        }
        if participant_names
        else {}
    )

    members_by_team = {}
    for m in raw_members:
        profile = profiles_by_participant.get(m.member) or frappe._dict()
        members_by_team.setdefault(m.team, []).append(profile)

    projects = []
    for result in results:
        project = projects_by_name.get(result.project)
        if not project:
            continue
        projects.append(
            {
                "name": project.title or project.name,
                "url": f"/{project.route}",
                "description": project.short_description or "",
                "cash_prize": frappe.format_value(
                    result.cash_prize, {"fieldtype": "Currency", "precision": "0"}
                )
                if result.cash_prize
                else None,
                "status": result.status,
                "team_name": project.team_name or "",
                "team_members": members_by_team.get(result.team, []),
                "repo_link": project.repo_link,
                "is_contribution_project": project.is_contribution_project,
                "partner_project_name": project.partner_project_name or "",
                "partner_project_route": project.partner_project_route or "",
            }
        )

    return _build_hackathon_data(hackathon, year, projects)


def _build_hackathon_data(hackathon, year, projects):
    hackathon_id = hackathon.name
    return {
        "id": year,
        "year": year,
        "name": hackathon.hackathon_name or f"FOSS Hack {year}",
        "date": f"{formatdate(hackathon.start_date, 'd')} - {formatdate(hackathon.end_date, 'd MMM yyyy')}",
        "mode": hackathon.hackathon_type or "Hybrid",
        "total_teams": frappe.db.count(HACKATHON_TEAM, {"hackathon": hackathon_id}),
        "total_participants": frappe.db.count(HACKATHON_PARTICIPANT, {"hackathon": hackathon_id}),
        "project_submissions": frappe.db.count(HACKATHON_PROJECT, {"hackathon": hackathon_id}),
        "partner_projects": frappe.db.count(
            HACKATHON_PARTNER_PROJECT, {"hackathon": hackathon_id}
        ),
        "community_partners": len(hackathon.community_partners),
        "route": hackathon.external_website_url or f"/fosshack/{year}",
        "projects": projects,
        "forum_post": HACKATHON_URLS.get(year, {}).get("forum_post"),
        "partner_project_url": (
            HACKATHON_URLS.get(year, {}).get("partner_project_url")
            or f"https://fossunited.org/fosshack/{year}/partner-projects"
        ),
        "projects_url": (
            HACKATHON_URLS.get(year, {}).get("projects_url")
            or f"https://fossunited.org/{hackathon.route}/projects/all"
        ),
    }


def get_all_hackathon_results():
    """
    Get all hackathon results - manual data for 2020, 2021, 2023
    and fetched data for 2024, 2025, 2026
    """
    hackathons = []

    # Add manual data
    for year in ["2020", "2021", "2023"]:
        hackathons.append(ARCHIVE_HACKATHONS[year])

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
    context.no_cache = False

    return context
