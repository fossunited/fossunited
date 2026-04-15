const render_talk_categories = (frm) => {
  let categories = frm.doc.session_categories
    .split('\n')
    .filter((category) => category.trim() !== '')

  let html = `<div>
                               <label class="control-label">Talk Categories</label>
                                <div style="display: flex; flex-wrap: wrap; gap: 8px;">`
  categories.forEach((category) => {
    html += `<div style="background: white; border: 1px solid #ddd; padding: 4px 8px; font-size: 12px; border-radius: 4px;">
                                                         ${frappe.utils.escape_html(category)}
                                                 </div>`
  })
  html += `   </div>
                        </div>`

  frm.set_df_property('categories_preview', 'options', html)
}

function is_reviewer_only() {
  return (
    frappe.user.has_role('CFP Reviewer') &&
    !frappe.user.has_role('System Manager') &&
    !frappe.user.has_role('Chapter Team Member')
  )
}

// Make all fields except the reviews table read-only for CFP Reviewers.
// Permlevels alone can't restrict level-0 fields for a role that needs
// write at level 0 to save (required to add review rows).
function restrict_reviewer_fields(frm) {
  if (!is_reviewer_only()) return
  frm.fields.forEach((f) => {
    if (f.df.fieldname !== 'reviews') {
      frm.set_df_property(f.df.fieldname, 'read_only', 1)
    }
  })
  frm.refresh_fields()

  const user = frappe.session.user
  const already_reviewed = (frm.doc.reviews || []).some((r) => r.email === user)
  const grid = frm.fields_dict.reviews.grid
  grid.cannot_add_rows = already_reviewed
  grid.refresh()
}

// Within a review row dialog: make all fields read-only if it belongs
// to a different reviewer.
frappe.ui.form.on('FOSS Event CFP Review', {
  refresh(frm) {
    if (!is_reviewer_only()) return
    if (frm.doc.email && frm.doc.email !== frappe.session.user) {
      frm.fields.forEach((f) => frm.set_df_property(f.df.fieldname, 'read_only', 1))
      frm.refresh_fields()
    }
  },
})

frappe.ui.form.on('FOSS Event CFP Submission', {
  refresh(frm) {
    render_talk_categories(frm)
    restrict_reviewer_fields(frm)
  },
})
