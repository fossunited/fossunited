<template>
  <div>
    <!-- Open Modal Button -->
    <button
      class="flex bg-surface-gray-7 text-ink-white px-4 py-2 rounded text-sm"
      @click="showModal = true"
      aria-label="Download schedule"
    >
      <IconDownload class="w-4 h-4 mr-1" />
      <span class="hidden md:block uppercase">Download Schedule</span>
    </button>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-surface-gray-7 bg-opacity-50 flex justify-center items-center z-50"
    >
      <div class="bg-surface-white p-6 rounded w-full max-w-lg">
        <h2 class="text-lg font-semibold mb-4">Download Options</h2>

        <!-- Format Selector -->
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">Select Format</label>
          <div class="flex gap-2 flex-wrap">
            <label
              v-for="format in ['ics', 'orgmode', 'markdown', 'csv', 'txt', 'pdf', 'json']"
              :key="format"
              class="cursor-pointer px-4 py-2 rounded border border-outline-gray-2 text-sm select-none hover:bg-surface-gray-7 hover:text-ink-white transition-colors duration-200"
              :class="{
                'bg-surface-gray-7 text-ink-white border-black': selectedFormat === format,
                'bg-surface-white text-ink-gray-6': selectedFormat !== format,
              }"
              @click="selectedFormat = format"
            >
              {{ format.toUpperCase() }}
            </label>
          </div>
        </div>

        <!-- Days -->
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">Days</label>
          <div class="flex gap-2 flex-wrap max-h-32 overflow-y-auto border p-2 rounded text-sm">
            <label
              v-for="day in allDates"
              :key="day.value"
              class="cursor-pointer px-3 py-1 rounded border border-outline-gray-2 select-none transition-colors duration-200"
              :class="{
                'bg-surface-gray-7 text-ink-white border-black': selectedDays.includes(day.value),
                'bg-surface-white text-ink-gray-6': !selectedDays.includes(day.value),
              }"
            >
              <input v-model="selectedDays" type="checkbox" :value="day.value" class="hidden" />
              {{ day.display }}
            </label>
          </div>
        </div>

        <!-- Halls -->
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">Halls</label>
          <div class="flex gap-2 flex-wrap max-h-32 overflow-y-auto border p-2 rounded text-sm">
            <label
              v-for="hall in allHalls"
              :key="hall"
              class="cursor-pointer px-3 py-1 rounded border border-outline-gray-2 select-none transition-colors duration-200"
              :class="{
                'bg-surface-gray-7 text-ink-white border-black': selectedHalls.includes(hall),
                'bg-surface-white text-ink-gray-6': !selectedHalls.includes(hall),
              }"
            >
              <input v-model="selectedHalls" type="checkbox" :value="hall" class="hidden" />
              {{ hall }}
            </label>
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex justify-end gap-3 mt-4">
          <button class="text-sm text-ink-gray-5 hover:underline" @click="showModal = false">
            Cancel
          </button>
          <button
            class="bg-surface-gray-7 text-ink-white px-4 py-2 rounded text-sm hover:bg-surface-gray-6 transition-colors duration-200"
            @click="downloadSchedule"
          >
            Download
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconDownload } from '@tabler/icons-vue'

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

const showModal = ref(false)
const selectedFormat = ref('ics')
const selectedDays = ref([])
const selectedHalls = ref([])

const allDatesRaw = props.schedule ? Object.keys(props.schedule) : [] // dd/mm/YYYY

const allDates = computed(() =>
  allDatesRaw.map((d) => {
    const [day, month, year] = d.split('/')
    return {
      display: d,
      value: `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`,
    }
  }),
)

const allHalls = computed(() => {
  const halls = new Set()
  for (const day in props.schedule) {
    for (const hall in props.schedule[day]) {
      halls.add(hall)
    }
  }
  return Array.from(halls)
})

function downloadSchedule() {
  showModal.value = false

  const query = new URLSearchParams()
  query.append('event', props.event.name)
  query.append('format', selectedFormat.value)

  selectedDays.value.forEach((day) => query.append('days', day))
  selectedHalls.value.forEach((hall) => query.append('halls', hall))

  const url = `/api/method/fossunited.api.schedule.download_schedule?${query.toString()}`
  window.open(url, '_blank')
}
</script>
