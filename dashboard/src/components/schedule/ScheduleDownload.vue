<template>
  <div>
    <button
      type="button"
      class="h-8 sm:h-10 flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 rounded-6 bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-7 dark:text-ink-gray-8 text-xs-semibold sm:text-sm uppercase hover:bg-surface-base dark:hover:bg-surface-gray-1 transition-colors shrink-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-7"
      aria-label="Download schedule"
      aria-haspopup="dialog"
      :aria-expanded="showModal"
      @click="showModal = true"
    >
      <IconDownload class="w-4 h-4" aria-hidden="true" />
      <span class="hidden sm:inline">Download</span>
    </button>

    <Dialog v-model:open="showModal" title="Download schedule" size="md">
      <div class="flex flex-col gap-5">
        <!-- Format names say what the file is for, not just its extension. -->
        <FormControl
          v-model="selectedFormat"
          type="select"
          label="Format"
          size="sm"
          variant="subtle"
          :options="formatOptions"
        />

        <!-- A single day or a single hall is not a choice, so it is not offered. -->
        <fieldset v-if="allDates.length > 1">
          <legend class="text-sm-medium text-ink-gray-7 dark:text-ink-gray-8 mb-2">
            Days
          </legend>
          <div class="flex gap-2 flex-wrap">
            <label
              v-for="day in allDates"
              :key="day.value"
              :class="[pillBase, selectedDays.includes(day.value) ? pillOn : pillOff]"
            >
              <input v-model="selectedDays" type="checkbox" :value="day.value" class="sr-only" />
              {{ day.display }}
            </label>
          </div>
        </fieldset>

        <fieldset v-if="allHalls.length > 1">
          <legend class="text-sm-medium text-ink-gray-7 dark:text-ink-gray-8 mb-2">
            Halls
          </legend>
          <div class="flex gap-2 flex-wrap">
            <label
              v-for="hall in allHalls"
              :key="hall"
              :class="[pillBase, selectedHalls.includes(hall) ? pillOn : pillOff]"
            >
              <input v-model="selectedHalls" type="checkbox" :value="hall" class="sr-only" />
              {{ hall }}
            </label>
          </div>
        </fieldset>

        <p
          v-if="validationMessage"
          id="schedule-download-error"
          class="text-sm text-ink-red-8"
          role="alert"
        >
          {{ validationMessage }}
        </p>
      </div>

      <template #actions="{ close }">
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="text-sm text-ink-gray-7 dark:text-ink-gray-8 hover:text-ink-gray-9 transition-colors px-4 py-2 rounded-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-7"
            @click="close"
          >
            Cancel
          </button>
          <button
            type="button"
            class="px-5 py-2 rounded-6 bg-surface-gray-10 text-ink-base text-sm-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-7"
            :class="
              validationMessage ? 'opacity-50 cursor-not-allowed' : 'hover:bg-surface-gray-9'
            "
            :aria-disabled="Boolean(validationMessage)"
            :aria-describedby="validationMessage ? 'schedule-download-error' : undefined"
            @click="downloadSchedule(close)"
          >
            Download
          </button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, FormControl } from 'frappe-ui'
import { IconDownload } from '@tabler/icons-vue'
import dayjs from 'dayjs'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  schedule: {
    type: Object,
    required: true, // { "YYYY-MM-DD": { hall: [sessions] } }
  },
  // Hall names in the organiser's order, parsed from `hall_options` by the page.
  hallOrder: {
    type: Array,
    default: () => [],
  },
})

const formatOptions = [
  { label: 'Calendar (.ics)', value: 'ics' },
  { label: 'Spreadsheet (.csv)', value: 'csv' },
  { label: 'Plain text (.txt)', value: 'txt' },
  { label: 'Markdown (.md)', value: 'md' },
  { label: 'Org mode (.org)', value: 'org' },
  { label: 'JSON (.json)', value: 'json' },
]

const pillBase =
  'cursor-pointer px-3 py-1.5 rounded-6 border text-sm select-none transition-colors focus-within:ring-2 focus-within:ring-outline-gray-7'
const pillOn = 'bg-surface-gray-10 text-ink-base border-transparent'
const pillOff =
  'bg-surface-base dark:bg-surface-gray-2 text-ink-gray-7 dark:text-ink-gray-8 border-outline-gray-3 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'

const showModal = ref(false)
const selectedFormat = ref('ics')
const selectedDays = ref([])
const selectedHalls = ref([])

const allDates = computed(() =>
  Object.keys(props.schedule || {}).map((iso) => ({
    value: iso,
    display: dayjs(iso).format('D MMM'),
  })),
)

// Union across every day, in the organiser's order. Unlisted halls come last in
// schedule order. Never sorted -- this has to match the hall row on the page.
const allHalls = computed(() => {
  const present = new Set()
  for (const day of Object.values(props.schedule || {})) {
    for (const hall of Object.keys(day)) present.add(hall)
  }
  if (!props.hallOrder.length) return [...present]

  const configuredSet = new Set(props.hallOrder)
  return [
    ...props.hallOrder.filter((hall) => present.has(hall)),
    ...[...present].filter((hall) => !configuredSet.has(hall)),
  ]
})

// Everything starts selected. An empty set used to mean "all" to the endpoint,
// which read on screen as "nothing will be downloaded".
watch(allDates, (dates) => (selectedDays.value = dates.map((d) => d.value)), { immediate: true })
watch(allHalls, (halls) => (selectedHalls.value = [...halls]), { immediate: true })

const validationMessage = computed(() => {
  if (!selectedDays.value.length) return 'Select at least one day.'
  if (!selectedHalls.value.length) return 'Select at least one hall.'
  return ''
})

function downloadSchedule(close) {
  if (validationMessage.value) return

  const query = new URLSearchParams()
  query.set('event', props.event.name)
  query.set('format', selectedFormat.value)

  // Send a filter only when it actually narrows the result
  if (selectedDays.value.length < allDates.value.length) {
    selectedDays.value.forEach((d) => query.append('days', d))
  }
  if (selectedHalls.value.length < allHalls.value.length) {
    selectedHalls.value.forEach((h) => query.append('halls', h))
  }

  window.open(
    `/api/method/fossunited.api.schedule.download_schedule?${query.toString()}`,
    '_blank',
  )
  close()
}
</script>
