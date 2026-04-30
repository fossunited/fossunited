// Copyright (c) 2025, Frappe x FOSSUnited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Grants Funding Directory', {
  refresh(frm) {
    // show button only for saved docs
    if (frm.is_new()) return

    frm.add_custom_button(__('Re-fetch Manifest Data'), () => {
      frappe.call({
        method:
          'fossunited.fossunited.doctype.grants_funding_directory.grants_funding_directory.refresh_funding_data',
        args: { docname: frm.doc.name },
        freeze: true,
        freeze_message: __('Refreshing funding data…'),
        callback(r) {
          if (r && r.message && r.message.success) {
            frappe.msgprint(r.message.message || __('Funding data refreshed'))
            frm.reload_doc()
          } else {
            frappe.msgprint({
              title: __('Refresh failed'),
              message: (r && r.message && r.message.message) || __('Unknown error'),
              indicator: 'red',
            })
          }
        },
      })
    })
  },
})
