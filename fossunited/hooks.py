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
web_include_css = ["/assets/fossunited/css/custom.css"]
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
        "from_route": "/blog/rss.xml",
        "to_route": "/rss.xml",
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
        "fossunited.fossunited.utils.get_grouped_events_by_chapter_type",
        "fossunited.fossunited.utils.get_volunteers_data",
        "fossunited.fossunited.utils.get_volunteers_stats",
        "fossunited.fossunited.utils.get_chapter_details",
        "fossunited.stack.utils.get_stack_dict",
        "fossunited.fossunited.utils.get_main_foss_events",
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
}

website_redirects = [
    {"source": r"c/(.+)/cfp", "target": r"/dashboard/cfp/apply/\1"},
    {"source": r"c/(.+)/cfp/all", "target": r"/dashboard/cfp/all/\1"},
    {"source": r"c/(.+)/schedule", "target": r"/dashboard/schedule/\1"},
    {
        "source": r"c/(.+)/tickets",
        "target": r"/api/method/fossunited.api.pages.buy_tickets_page?route=c/\1",
    },
    {"source": r"^grants/project(/.*)?$", "target": r"/grants/projects\1"},
    {"source": r"^grants/event(/.*)?$", "target": r"/grants/events\1"},
    {"source": r"^grants/fellowship(/.*)?$", "target": r"/grants/fellowships\1"},
    {"source": r"^grants/grantee(/.*)?$", "target": r"/grants/grantees\1"},
]

# Installation
# ----------------
before_install = "fossunited.install.before_install"
after_install = "fossunited.install.after_install"

# Uninstallation
# ----------------
before_uninstall = "fossunited.uninstall.before_uninstall"

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
    ],
    "monthly": [
        "fossunited.scheduled_tasks.update_past_job_status",
    ],
}
