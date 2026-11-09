# Frappe's own web_form.html/web_list.html extend templates/web.html, which hardcodes
# templates/includes/navbar/navbar.html and footer/footer.html directly
#
# Mixin via `extend_doctype_class`: frappe puts it before WebForm in the MRO, so
# super().get_context() runs the original (banner image, metatags, boot data, field
# permissions, etc. all untouched), and we only swap in our own template afterwards.
WEB_FORM_TEMPLATE = "website/doctype/web_form/templates/web_form.html"
WEB_LIST_TEMPLATE = "website/doctype/web_form/templates/web_list.html"


class WebFormExtend:
    def get_context(self, context):
        super().get_context(context)

        if context.template == WEB_LIST_TEMPLATE:
            context.template = "fossunited/templates/overrides/web_form_list.html"
        else:
            context.template = "fossunited/templates/overrides/web_form.html"

        # foss_base.html reads these two context keys for its own navbar/footer blocks;
        # map the Web Form's own per-form toggles onto them.
        context.hide_nav = bool(self.hide_navbar)
        context.hide_footer = bool(self.hide_footer)
