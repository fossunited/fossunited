<template>
  <div class="flex flex-wrap items-center gap-2">
    <!-- Day Dropdown -->
    <select
      v-model="selectedDay"
      class="px-2 py-1 bg-gray-100 border border-gray-300 text-xs rounded-[2px] focus:outline-none min-w-[100px]"
    >
      <option value="">All Days</option>
      <option v-for="day in allDates" :key="day" :value="day">{{ day }}</option>
    </select>

    <!-- Hall Dropdown -->
    <select
      v-model="selectedHall"
      class="px-2 py-1 bg-gray-100 border border-gray-300 text-xs rounded-[2px] focus:outline-none min-w-[100px]"
    >
      <option value="">All Halls</option>
      <option v-for="hall in allHalls" :key="hall" :value="hall">{{ hall }}</option>
    </select>

    <!-- Download Button -->
    <button
      class="px-2 py-1 bg-gray-900 text-white text-xs font-medium rounded-[2px] flex items-center gap-1"
      @click="handleDownload"
    >
      <IconCalendarPlus class="w-4 h-4" />
      <span class="hidden md:inline uppercase">Download .ics</span>
    </button>
  </div>
</template>

<script setup>
import { createEvents } from 'ics'
import { IconCalendarPlus } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import { computed, defineProps, inject, ref } from 'vue'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  schedule: {
    type: Object,
    required: true,
  },
})

// Extract unique days and halls
const allDates = computed(() => Object.keys(props.schedule))
const allHalls = computed(() => {
  const halls = new Set()
  for (const day in props.schedule) {
    for (const hall in props.schedule[day]) {
      halls.add(hall)
    }
  }
  return Array.from(halls)
})

const selectedDay = ref('')
const selectedHall = ref('')

// function formatTimeForIcs(time) {
//   let date_arr = props.session.scheduled_date.split('-').map(Number)
//   let time_arr = time.split(':').map(Number)
//   time_arr.pop()

//   const formattedTime = date_arr.concat(time_arr)
//   return formattedTime
// }

function formatTimeForIcs(dateStr, timeStr) {
  const dateParts = dateStr.split('-').map(Number) // e.g. ['2025', '08', '26']
  const timeParts = timeStr.split(':').map(Number) // e.g. ['10', '30', '00']

  if (dateParts.length !== 3 || timeParts.length < 2) {
    console.warn('Invalid date/time:', dateStr, timeStr)
    return null
  }

  return [dateParts[0], dateParts[1], dateParts[2], timeParts[0], timeParts[1]]
}

// Flatten schedule object: { date: { hall: [sessions] } } → [sessions]
function flattenSchedule(schedule, { hall = null, date = null } = {}) {
  const sessions = []

  for (const d in schedule) {
    if (date && d !== date) continue // filter by date (e.g. "26/08/2025")

    const halls = schedule[d]
    for (const h in halls) {
      if (hall && h !== hall) continue // filter by hall (e.g. "Room 1")

      sessions.push(...halls[h])
    }
  }

  return sessions
}

// Main download function
function generateAndDownloadIcs(sessions, filename, eventMeta) {
  if (!sessions.length) {
    toast.error('No sessions found.')
    return
  }

  const events = sessions.flatMap((session) => {
    const start = formatTimeForIcs(session.scheduled_date, session.start_time)
    const end = formatTimeForIcs(session.scheduled_date, session.end_time)
    if (!start || !end) return []
    const category = session.category !== 'Other' ? session.category : session.other_category
    return [
      {
        title: `${session.title} - ${eventMeta.event_name}`,
        start,
        end,
        location: `${session.hall || 'TBD'}, ${eventMeta.event_location}`,
        ...(category ? { categories: [category] } : {}),
        alarms: [
          {
            action: 'display',
            description: `Reminder: ${session.title} at ${eventMeta.event_name}`,
            trigger: { minutes: 10, before: true },
          },
        ],
      },
    ]
  })

  if (!events.length) {
    toast.error('No valid sessions to export.')
    return
  }

  createEvents(events, (error, value) => {
    if (error) {
      console.error(error)
      toast.error('ICS generation failed: ' + error.message)
      return
    }

    const blob = new Blob([value], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)

    toast.success(`.ics file "${filename}" downloaded.`)
  })
}

function handleDownload() {
  const hasDay = selectedDay.value
  const hasHall = selectedHall.value

  let sessions = []
  let filename = props.event.event_name

  if (!hasDay && !hasHall) {
    sessions = flattenSchedule(props.schedule)
    filename += '.ics'
  } else if (hasDay && !hasHall) {
    sessions = flattenSchedule(props.schedule, { date: selectedDay.value })
    filename += `-Day-${selectedDay.value}.ics`
  } else if (!hasDay && hasHall) {
    sessions = flattenSchedule(props.schedule, { hall: selectedHall.value })
    filename += `-Hall-${selectedHall.value}.ics`
  } else {
    sessions = flattenSchedule(props.schedule, {
      date: selectedDay.value,
      hall: selectedHall.value,
    })
    filename += `-${selectedHall.value}-${selectedDay.value}.ics`
  }

  generateAndDownloadIcs(sessions, filename, props.event)
}
</script>
