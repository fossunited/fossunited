frappe.ui.form.on('User', {
  setup(frm) {
    // Frappe bug: frm.module_editor is never initialized for Website Users,
    // causing refresh to crash at `frm.module_editor.disable = ...` (user.js:253).
    // Provide a safe no-op so Frappe's refresh doesn't abort before our handler runs.
    if (!frm.module_editor) {
      frm.module_editor = { disable: 0, show() {} }
    }
  },

  refresh(frm) {
    if (
      frm.doc.user_type === 'Website User' &&
      !frm.is_new() &&
      frappe.user.has_role('System Manager')
    ) {
      frm.add_custom_button(
        __('Delete User & Profile'),
        () => {
          frappe.confirm(
            `Permanently delete <strong>${frappe.utils.escape_html(frm.doc.full_name)}</strong> and their FOSS profile?`,
            () => {
              frappe.call({
                method: 'fossunited.fossunited.user_utils.delete_user_and_profile',
                args: { user: frm.doc.name },
                callback(r) {
                  if (r.message === 'deleted') {
                    frappe.show_alert({ message: __('User and profile deleted'), indicator: 'red' })
                    frappe.set_route('List', 'User')
                  }
                },
              })
            },
          )
        },
        __('Spam'),
      )
    }

    if (
      frm.doc.user_type === 'Website User' &&
      !frm.doc.enabled &&
      !frm.is_new() &&
      frappe.user.has_role('System Manager')
    ) {
      frm.add_custom_button(
        __('Approve'),
        () => {
          frappe.confirm(
            `Approve account for <strong>${frappe.utils.escape_html(frm.doc.full_name)}</strong>?`,
            () => {
              frappe.call({
                method: 'fossunited.fossunited.user_utils.approve_user',
                args: { user: frm.doc.name },
                callback(r) {
                  if (r.message === 'approved') {
                    frappe.show_alert({
                      message: __('User approved and notified by email'),
                      indicator: 'green',
                    })
                    frm.reload_doc()
                  }
                },
              })
            },
          )
        },
        __('Approval'),
      )

      frm.add_custom_button(
        __('Deny'),
        () => {
          let d = new frappe.ui.Dialog({
            title: __('Deny Signup'),
            fields: [
              {
                label: __('Notify user by email'),
                fieldname: 'notify',
                fieldtype: 'Check',
                default: 0,
              },
              {
                label: __('Reason (optional — sent to user)'),
                fieldname: 'reason',
                fieldtype: 'Small Text',
                depends_on: 'notify',
              },
            ],
            primary_action_label: __('Deny & Delete User'),
            primary_action({ notify, reason }) {
              frappe.call({
                method: 'fossunited.fossunited.user_utils.deny_user',
                args: { user: frm.doc.name, reason: reason || '', notify: notify ? 1 : 0 },
                callback(r) {
                  if (r.message === 'denied') {
                    d.hide()
                    frappe.show_alert({
                      message: __('User denied and deleted'),
                      indicator: 'red',
                    })
                    frappe.set_route('List', 'User')
                  }
                },
              })
            },
          })
          d.show()
        },
        __('Approval'),
      )
    }
  },
})
