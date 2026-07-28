# Macros

Reusable Jinja2 macros used in the server-rendered website templates
(Frappe web pages, not the Desk/admin UI).

A file can define more than one related macro. For example,
`breadcrumb.html` also contains `theme_toggle` and `v3_navbar`.

Macros are imported using their full app path:

```jinja
{% from "fossunited/templates/macros/chapter_branding_block.html" import chapter_branding_block %}
```

Not everything here is visual - `meta_block.html` just renders page
`<meta>` tags for SEO/social sharing, rather than page content.
