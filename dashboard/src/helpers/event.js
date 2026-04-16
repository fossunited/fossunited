import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { ref } from 'vue'

export const isChapterMember = async (chapter_id) => {
  const isMember = createResource({
    url: 'fossunited.api.chapter.check_if_chapter_member',
    params: {
      chapter: chapter_id,
      user: session.user,
    },
  })

  await isMember.fetch()

  return isMember.data
}

export const isEventMember = async (event_id) => {
  const isMember = createResource({
    url: 'fossunited.api.chapter.check_if_event_member',
    params: { event: event_id },
  })
  await isMember.fetch()
  return isMember.data
}

export const isEventOrganizer = async (event_id) => {
  const eventId = createResource({
    url: 'frappe.client.get_value',
    params: {
      doctype: 'FOSS Chapter Event',
      fieldname: 'chapter',
      filters: { name: event_id },
    },
  })
  await eventId.fetch()

  if (eventId.data) {
    const chapterMember = await isChapterMember(eventId.data.chapter)
    if (chapterMember) return true
  }

  return await isEventMember(event_id)
}
