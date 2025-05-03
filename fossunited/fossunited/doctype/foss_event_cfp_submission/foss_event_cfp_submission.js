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

frappe.ui.form.on('FOSS Event CFP Submission', {
  refresh(frm) {
    render_talk_categories(frm)
  },
})
