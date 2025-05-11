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

export const isEventOrganizer = async (event_id) => {
  const isOrganizer = ref(false)
  const eventId = createResource({
    url: 'frappe.client.get_value',
    params: {
      doctype: 'FOSS Chapter Event',
      fieldname: 'chapter',
      filters: {
        name: event_id,
      },
    },
    auto: true,
  })
  await eventId.fetch()
  if (eventId.data) {
    isOrganizer.value = await isChapterMember(eventId.data.chapter)
  }

  return isOrganizer.value
}
