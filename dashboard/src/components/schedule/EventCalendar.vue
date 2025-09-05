<template>
  <div>
    <!-- Main Download Button -->
    <button
      class="px-2 py-2 bg-gray-900 text-white text-xs font-medium rounded flex items-center gap-1"
      @click="showDownloadModal = true"
    >
      <IconCalendarPlus class="w-4 h-4" />
      <span class="hidden md:inline uppercase">Download .ics</span>
    </button>

    <!-- Modal -->
    <div
      v-if="showDownloadModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70"
    >
      <div class="bg-white rounded-md shadow-md p-4 w-[90%] max-w-sm">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-medium">
            Download Calendar (.ics) for {{ props.event.event_name }}
          </h3>
          <button
            class="text-gray-500 hover:text-black text-lg"
            @click="showDownloadModal = false"
          >
            ×
          </button>
        </div>

        <div class="flex flex-col gap-3">
          <!-- Day Dropdown -->
          <label class="text-xs">
            Day
            <select
              v-model="selectedDay"
              class="w-full mt-1 px-2 py-1 border border-gray-300 text-lg rounded bg-gray-900 text-white"
            >
              <option value="">All Days</option>
              <option v-for="day in allDates" :key="day" :value="day">{{ day }}</option>
            </select>
          </label>

          <!-- Hall Dropdown -->
          <label class="text-xs">
            Hall
            <select
              v-model="selectedHall"
              class="w-full mt-1 px-2 py-1 border border-gray-300 text-lg rounded bg-gray-900 text-white"
            >
              <option value="">All Halls</option>
              <option v-for="hall in allHalls" :key="hall" :value="hall">{{ hall }}</option>
            </select>
          </label>

          <!-- Buttons -->
          <div class="flex justify-end gap-2 mt-4">
            <button
              class="text-xs text-gray-600 hover:underline"
              @click="showDownloadModal = false"
            >
              Cancel
            </button>
            <button
              class="px-3 py-2 bg-gray-900 text-white text-base font-medium rounded"
              @click="confirmDownload"
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createEvents } from 'ics'
import { IconCalendarPlus } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import { computed, defineProps, inject, ref } from 'vue'

const showDownloadModal = ref(false)

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

function confirmDownload() {
  showDownloadModal.value = false
  handleDownload()
}
</script>
