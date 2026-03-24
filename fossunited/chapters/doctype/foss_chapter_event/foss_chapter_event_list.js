frappe.listview_settings['FOSS Chapter Event'] = {
  refresh(listview) {
    const events = (listview.data || []).map((d) => d.name)
    if (!events.length) return

    // inject header cols
    const $headerSubject = listview.$result.find('.list-row-head .list-header-subject')
    $headerSubject.find('.counts-col-head').remove()
    $headerSubject.append(`
      <div class="list-row-col counts-col-head hidden-xs text-muted small" style="flex: 0 0 60px;">CFP</div>
      <div class="list-row-col counts-col-head hidden-xs text-muted small" style="flex: 0 0 60px;">RSVP</div>
    `)

    frappe.call({
      method:
        'fossunited.chapters.doctype.foss_chapter_event.foss_chapter_event.get_event_connection_counts',
      args: { events: JSON.stringify(events) },
      callback({ message: counts }) {
        if (!counts) return
        listview.$result.find('.list-row').each(function () {
          const name = $(this).find('[data-name]').first().attr('data-name')
          const { cfp_count = 0, rsvp_count = 0 } = counts[name] || {}
          $(this).find('.level-left').find('.counts-col').remove()
          $(this).find('.level-left').append(`
            <div class="list-row-col counts-col hidden-xs text-muted small" style="flex: 0 0 60px;">${cfp_count}</div>
            <div class="list-row-col counts-col hidden-xs text-muted small" style="flex: 0 0 60px;">${rsvp_count}</div>
          `)
        })
      },
    })
  },
}
