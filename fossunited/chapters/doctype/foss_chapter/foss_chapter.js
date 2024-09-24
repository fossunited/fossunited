// Copyright (c) 2024, Frappe x FOSSUnited and contributors
// For license information, please see license.txt

frappe.ui.form.on('FOSS Chapter', {
  chapter_name(frm) {
    if (frm.doc.chapter_name) {
      frm.doc.slug = frm.doc.chapter_name
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
      frm.refresh_field('slug')
    }
  },
})
