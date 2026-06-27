import os as _os

app_name = "fossunited"
app_title = "FOSSUnited Platform"
app_publisher = "Frappe x FOSSUnited"
app_description = "FOSS to organize events and to facilitate the community engagement"
app_email = "developers@fossunited.org"
app_license = "AGPL-3.0"

export_python_type_annotations = True

fixtures = ["State", "City", "FOSS Event Type"]

# Includes in <head>
# ------------------

# include js, css files in header of web template
_css_file = _os.path.join(_os.path.dirname(__file__), "public/css/custom.css")
_css_v = str(int(_os.path.getmtime(_css_file))) if _os.path.exists(_css_file) else "1"
web_include_css = [f"/assets/fossunited/css/custom.css?v={_css_v}"]
web_include_js = ["website.bundle.js"]

# Jinja
# -----

# Add all simple route bench rules here
website_route_rules = [
    {
        "from_route": "/dashboard/<path:app_path>",
        "to_route": "dashboard",
    },
    {
        "from_route": "/<path:event_route>/rsvp/<submission>/edit",
        "to_route": "/rsvp/submission/edit",
    },
    {
        "from_route": "/hack/<permalink>/projects/all",
        "to_route": "/hackathon/projects",
    },
    {
        "from_route": "/c/<chapter>/rss.xml",
        "to_route": "/c/rss.xml",
    },
]

# add methods and filters to jinja environment
jinja = {
    "methods": [
        "fossunited.fossunited.utils.make_badge",
        "fossunited.fossunited.utils.get_doc_likes",
        "fossunited.fossunited.utils.get_user_socials",
        "fossunited.fossunited.utils.get_user_editable_doctype_fields",
        "fossunited.fossunited.utils.get_signup_optin_checks",
        "fossunited.fossunited.utils.get_volunteers_data",
        "fossunited.fossunited.utils.get_volunteers_stats",
        "fossunited.fossunited.utils.get_chapter_details",
        "fossunited.stack.utils.get_stack_dict",
        "fossunited.www.events.timeline.index.get_must_attend_events",
        "fossunited.fossunited.utils.get_all_city_names",
    ],
    "filters": [
        "fossunited.fossunited.utils.make_badge",
        "fossunited.fossunited.utils.get_profile_image",
    ],
}


signup_form_template = "fossunited.plugins.show_custom_signup"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "after_insert": [
            "fossunited.fossunited.user_utils.set_unique_username",
            "fossunited.fossunited.user_utils.create_profile_on_user_create",
        ],
    },
    "Razorpay Payment": {
        "on_update": [
            "fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket.handle_payment_on_update"
        ],
        "before_insert": [
            "fossunited.ticketing.doctype.foss_event_ticket.foss_event_ticket.validate_payment_before_insert"
        ],
    },
    # ToDO email is sent by frappe only when assigned from desk, we will have custom mail
    # when a reviewer is assigned to a proposal so we give dashboard link itself to open
    "ToDo": {
        "after_insert": "fossunited.utils.notifications.notify_cfp_reviewer_assignment",
    },
}

website_redirects = [
    {"source": "/events/timeline/upcoming", "target": "/events/timeline"},
    {"source": r"c/(.+)/cfp", "target": r"/dashboard/cfp/apply/\1"},
    {"source": r"c/(.+)/cfp/all", "target": r"/dashboard/cfp/all/\1"},
    {"source": r"c/(.+)/schedule", "target": r"/dashboard/schedule/\1"},
    {
        "source": r"c/(.+)/tickets",
        "target": r"/api/method/fossunited.api.pages.buy_tickets_page?route=c/\1",
    },
    # grants pages
    {"source": r"^grants/project(/.*)?$", "target": r"/grants/projects\1"},
    {"source": r"^grants/event(/.*)?$", "target": r"/grants/events\1"},
    {"source": r"^grants/fellowship(/.*)?$", "target": r"/grants/fellowships\1"},
    {"source": r"^grants/grantee(/.*)?$", "target": r"/grants/grantees\1"},
    # rss feeds
    {"source": r"^blog/rss\.xml$", "target": r"/rss.xml"},
    {"source": r"^blog/rss$", "target": r"/rss.xml"},
    {"source": r"^rss$", "target": r"/rss.xml"},
    {"source": r"^(?!.*\.xml$)(.*)/rss$", "target": r"/\1/rss.xml"},
    {
        "source": r"hack/(.+)/partner-projects(.*)",
        "target": r"/api/method/fossunited.api.pages.partner_projects_redirect?hack=\1&project=\2",
    },
    # fosshack
    {"source": r"^fosshack/(\d{4})/results/?$", "target": "/fosshack/results?year=\\1"},
]

# Installation
# ----------------
before_install = "fossunited.install.before_install"
after_install = "fossunited.install.after_install"

# Uninstallation
# ----------------
before_uninstall = "fossunited.uninstall.before_uninstall"

permission_query_conditions = {
    "FOSS Event CFP Submission": "fossunited.fossunited.permissions.cfp_submission_query",
    "FOSS Event RSVP Submission": "fossunited.fossunited.permissions.rsvp_submission_query",
}

override_doctype_class = {
    "Newsletter": "fossunited.overrides.newsletter_extend.NewsletterExtend",
}

before_tests = "fossunited.setup.before_tests"

# Migration
# ----------------
before_migrate = "fossunited.migrate.before_migrate"

# Scheduler Events
# ----------------
scheduler_events = {
    "daily_long": [
        "fossunited.scheduled_tasks.conclude_events",
        "fossunited.scheduled_tasks.send_rsvp_event_reminders",
    ],
    "monthly": [
        "fossunited.scheduled_tasks.update_past_job_status",
    ],
}
