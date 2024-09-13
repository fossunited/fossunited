app_name = "fossunited"
app_title = "FOSSUnited Platform"
app_publisher = "Frappe x FOSSUnited"
app_description = "Built on Frappe"
app_email = "developers@fossunited.org"
app_license = "AGPL-3.0"
# required_apps = []

export_python_type_annotations = True

fixtures = ["State", "City", "FOSS Event Type"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/fossunited/css/fossunited.css"
# app_include_js = ["website.bundle.js", "dialog.bundle.js", "form.bundle.js"]

# include js, css files in header of web template
web_include_css = ["/assets/fossunited/css/custom.css"]
web_include_js = ["website.bundle.js"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "fossunited/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}tele

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# Add all simple route bench rules here
website_route_rules = [
    {
        "from_route": "/dashboard/<path:app_path>",
        "to_route": "dashboard",
    },
    {
        "from_route": "/events/<event>/cfp/new",
        "to_route": "/cfp/create/new",
    },
    {
        "from_route": "/events/<event>/rsvp/new",
        "to_route": "/rsvp/create/new",
    },
    {
        "from_route": "/events/<event_permalink>/schedule",
        "to_route": "/schedule",
    },
    {
        "from_route": "/events/<event_permalink>/cfp/<submission>/edit",
        "to_route": "/cfp/submission/edit",
    },
    {
        "from_route": "/events/<event_permalink>/rsvp/<submission>/edit",
        "to_route": "/rsvp/submission/edit",
    },
    {
        "from_route": "/<foss_user>/edit-profile",
        "to_route": "/foss_profile/edit",
    },
    {
        "from_route": "/create-foss-profile",
        "to_route": "/foss_profile/create",
    },
    {
        "from_route": "/events/<event_permalink>/book-conference-ticket",
        "to_route": "/book-conference-ticket",
    },
    {
        "from_route": "/events/<event_permalink>/cfp/all",
        "to_route": "/cfp/all",
    },
    {
        "from_route": "/hack/<permalink>/projects/all",
        "to_route": "/hackathon/projects",
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
        "fossunited.fossunited.utils.get_grouped_events",
    ],
    "filters": [
        "fossunited.fossunited.utils.make_badge",
        "fossunited.fossunited.utils.get_profile_image",
    ],
}


signup_form_template = "fossunited.plugins.show_custom_signup"

# Installation
# ------------

# before_install = "fossunited.install.before_install"
# after_install = "fossunited.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "fossunited.uninstall.before_uninstall"
# after_uninstall = "fossunited.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "fossunited.utils.before_app_install"
# after_app_install = "fossunited.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "fossunited.utils.before_app_uninstall"
# after_app_uninstall = "fossunited.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fossunited.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"fossunited.tasks.all"
# 	],
# 	"daily": [
# 		"fossunited.tasks.daily"
# 	],
# 	"hourly": [
# 		"fossunited.tasks.hourly"
# 	],
# 	"weekly": [
# 		"fossunited.tasks.weekly"
# 	],
# 	"monthly": [
# 		"fossunited.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "fossunited.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "fossunited.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "fossunited.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["fossunited.utils.before_request"]
# after_request = ["fossunited.utils.after_request"]

# Job Events
# ----------
# before_job = ["fossunited.utils.before_job"]
# after_job = ["fossunited.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"fossunited.auth.validate"
# ]
