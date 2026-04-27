const CATEGORY_COLORS = [
  { bg: '#e8f4fd', text: '#1a73c7' },
  { bg: '#e8f8f0', text: '#1a7a45' },
  { bg: '#fdf3e8', text: '#b45309' },
  { bg: '#f3e8fd', text: '#7c3aed' },
  { bg: '#fde8e8', text: '#b91c1c' },
  { bg: '#e8fdf8', text: '#0f766e' },
]

const render_talk_categories = (frm) => {
  if (!frm.doc.session_categories) return
  const categories = frm.doc.session_categories
    .split('\n')
    .filter((c) => c.trim() !== '')

  const pills = categories
    .map((category, i) => {
      const color = CATEGORY_COLORS[i % CATEGORY_COLORS.length]
      return `<span style="background:${color.bg}; color:${color.text}; border-radius:4px; padding:3px 10px; font-size:12px; font-weight:500; display:inline-block;">
        ${frappe.utils.escape_html(category.trim())}
      </span>`
    })
    .join('')

  frm.set_df_property(
    'categories_preview',
    'options',
    `<div>
      <label class="control-label">Talk Categories</label>
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:4px;">${pills}</div>
    </div>`,
  )
}

// --- Role helpers ---

const is_system_manager = () => frappe.user.has_role('System Manager')
const is_chapter_team_member = () => frappe.user.has_role('Chapter Team Member')
const is_cfp_reviewer = () => frappe.user.has_role('CFP Reviewer')

// --- Field restriction logic ---

// Design intent:
//   Owner           — full edit on their own submission (permlevel 0+1+4)
//   Chapter Member  — can change status (L3) and add reviews (L2); NOT owner content (L1)
//   CFP Reviewer    — can only add reviews (L2); everything else read-only
//   Both roles      — Chapter Member behaviour (more permissive: status + reviews)
//   System Manager  — no restrictions
//
// perm.js ignores if_owner at permlevel 1+ client-side, so JS must enforce the
// owner-content read-only. Server still enforces via validate_higher_perm_levels.
function apply_role_restrictions(frm) {
  if (is_system_manager()) return

  const is_ctm = is_chapter_team_member()
  const is_reviewer = is_cfp_reviewer()

  if (!is_ctm && !is_reviewer) return

  // Own submission: owner can always edit their own content regardless of roles.
  if (frm.doc.owner === frappe.session.user) return

  // Lock permlevel 1 fields (owner-only content: talk_title, bio, speakers, etc.)
  // for both CTM and Reviewer — neither should edit the proposal content.
  frm.fields.forEach((field) => {
    if (field.df.permlevel === 1) {
      frm.set_df_property(field.df.fieldname, 'read_only', 1)
    }
  })
  frm.refresh_fields()

  // CFP Reviewer (without CTM): also lock status and other non-review fields.
  // CTM keeps status (L3) editable since they manage proposal workflow.
  if (is_reviewer && !is_ctm) {
    frm.fields.forEach((field) => {
      if (field.df.fieldname !== 'reviews' && field.df.permlevel !== 1) {
        frm.set_df_property(field.df.fieldname, 'read_only', 1)
      }
    })
    frm.refresh_fields()
  }

  // One review per person: hide Add Row once current user has submitted one.
  const user = frappe.session.user
  const already_reviewed = (frm.doc.reviews || []).some((r) => r.email === user)
  const grid = frm.fields_dict.reviews.grid
  grid.cannot_add_rows = already_reviewed
  grid.refresh()
}

// Within a review row dialog: lock fields belonging to a different reviewer.
frappe.ui.form.on('FOSS Event CFP Review', {
  refresh(frm) {
    if (is_system_manager()) return
    if (frm.doc.email && frm.doc.email !== frappe.session.user) {
      frm.fields.forEach((f) => frm.set_df_property(f.df.fieldname, 'read_only', 1))
      frm.refresh_fields()
    }
  },
})

frappe.ui.form.on('FOSS Event CFP Submission', {
  refresh(frm) {
    render_talk_categories(frm)
    apply_role_restrictions(frm)
  },
})
