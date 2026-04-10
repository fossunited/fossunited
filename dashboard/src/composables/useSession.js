import { computed, inject } from 'vue'
import { createEvent } from 'ics'
import { toast } from 'vue-sonner'
import dayjs from 'dayjs'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'

/**
 * Shared session logic for SessionCard and TimeCapsule.
 * @param {import('vue').Ref} session - a ref to the session object (toRef(props, 'session'))
 */
export function useSession(session) {
  const event = inject('event', null)

  function formatTime(timeStr) {
    if (!timeStr) return ''
    return dayjs(`1970-01-01 ${timeStr}`).format('h:mm A')
  }

  const speakers = computed(() => {
    const s = session.value
    if (s.cfp_speakers?.length) return s.cfp_speakers
    if (s.speakers) {
      try { return JSON.parse(s.speakers) } catch { return [] }
    }
    return []
  })

  const visibleSpeakers = computed(() => speakers.value.slice(0, 4))

  const speakerGridClass = computed(() => {
    const n = visibleSpeakers.value.length
    if (n <= 1) return 'grid-cols-1'
    if (n === 2) return 'grid-cols-2'
    if (n === 3) return 'grid-cols-3'
    return 'grid-cols-2 grid-rows-2'
  })

  const sessionDuration = computed(() => {
    const s = session.value
    if (!s.start_time || !s.end_time) return ''
    const mins = dayjs(`1970-01-01 ${s.end_time}`).diff(
      dayjs(`1970-01-01 ${s.start_time}`),
      'minute',
    )
    return `${mins} min`
  })

  const sessionCategory = computed(() => {
    const cat = session.value.category
    if (!cat || cat === 'Other') return session.value.other_category || ''
    return cat
  })

  const showCategory = computed(
    () => Boolean(sessionCategory.value) && sessionCategory.value !== 'Break',
  )

  const categoryStyle = computed(() => {
    const cat = (sessionCategory.value || '').toLowerCase()
    if (cat.includes('workshop')) return 'bg-surface-green-2 text-ink-green-3'
    if (cat.includes('keynote')) return 'bg-surface-violet-1 text-ink-violet-1'
    if (cat.includes('panel')) return 'bg-surface-blue-2 text-ink-blue-3'
    if (cat.includes('lightning')) return 'bg-surface-amber-2 text-ink-amber-3'
    return 'bg-surface-green-2 text-ink-green-3'
  })

  const cfpHref = computed(() => {
    const r = session.value.cfp_route
    return r ? createAbsoluteUrlFromRoute(r) : null
  })

  function downloadIcs() {
    const s = session.value
    if (!s.scheduled_date || !s.start_time || !s.end_time) {
      toast.error('Missing time info for this session')
      return
    }
    const dateParts = s.scheduled_date.toString().split('-').map(Number)
    createEvent(
      {
        title: `${s.title} – ${event?.data?.event_name ?? ''}`,
        start: dateParts.concat(s.start_time.split(':').map(Number).slice(0, 2)),
        end: dateParts.concat(s.end_time.split(':').map(Number).slice(0, 2)),
        location: `${s.hall ?? ''}, ${event?.data?.event_location ?? ''}`,
        categories: [sessionCategory.value].filter(Boolean),
        alarms: [
          {
            action: 'display',
            description: `Reminder: ${s.title}`,
            trigger: { minutes: 10, before: true },
          },
        ],
      },
      (error, value) => {
        if (error) { toast.error('Error creating calendar event'); return }
        const url = URL.createObjectURL(new Blob([value], { type: 'text/calendar' }))
        const a = document.createElement('a')
        a.href = url
        a.download = `${s.title}.ics`
        a.click()
        URL.revokeObjectURL(url)
        toast.info('.ics downloaded')
      },
    )
  }

  return {
    formatTime,
    speakers,
    visibleSpeakers,
    speakerGridClass,
    sessionDuration,
    sessionCategory,
    showCategory,
    categoryStyle,
    cfpHref,
    downloadIcs,
  }
}
