<template>
  <div>
    <button
      class="h-8 sm:h-10 flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-7 text-xs sm:text-sm font-semibold uppercase hover:bg-surface-gray-3 dark:hover:bg-surface-gray-4 transition-colors shrink-0"
      aria-label="Download schedule"
      @click="showModal = true"
    >
      <IconDownload class="w-4 h-4" />
      <span class="hidden sm:inline">Download</span>
    </button>

    <!-- Modal backdrop -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="showModal"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
          @click.self="showModal = false"
        >
          <div class="absolute inset-0 bg-black/50" @click="showModal = false" />
          <div
            class="relative bg-surface-white dark:bg-surface-gray-1 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
            @click.stop
          >
            <div class="p-6">
              <div class="flex items-center justify-between mb-5">
                <h2 class="text-lg font-semibold text-ink-gray-9">Download Schedule</h2>
                <button
                  class="text-ink-gray-5 hover:text-ink-gray-9 transition-colors"
                  @click="showModal = false"
                >
                  <IconX class="w-5 h-5" />
                </button>
              </div>

              <!-- Format selector -->
              <div class="mb-5">
                <label class="block text-sm font-medium text-ink-gray-7 mb-2">Format</label>
                <div class="flex gap-2 flex-wrap">
                  <label
                    v-for="fmt in formats"
                    :key="fmt"
                    class="cursor-pointer px-3 py-1.5 rounded-lg border text-sm font-semibold uppercase select-none transition-colors"
                    :class="
                      selectedFormat === fmt
                        ? 'bg-surface-gray-7 text-ink-white border-surface-gray-7'
                        : 'bg-surface-white dark:bg-surface-gray-2 text-ink-gray-6 border-outline-gray-2 hover:bg-surface-gray-2'
                    "
                    @click="selectedFormat = fmt"
                  >
                    {{ fmt }}
                  </label>
                </div>
              </div>

              <!-- Days selector -->
              <div class="mb-5">
                <label class="block text-sm font-medium text-ink-gray-7 mb-2">Days</label>
                <div class="flex gap-2 flex-wrap">
                  <label
                    v-for="day in allDates"
                    :key="day.value"
                    class="cursor-pointer px-3 py-1.5 rounded-lg border text-sm select-none transition-colors"
                    :class="
                      selectedDays.includes(day.value)
                        ? 'bg-surface-gray-7 text-ink-white border-surface-gray-7'
                        : 'bg-surface-white dark:bg-surface-gray-2 text-ink-gray-6 border-outline-gray-2 hover:bg-surface-gray-2'
                    "
                  >
                    <input
                      v-model="selectedDays"
                      type="checkbox"
                      :value="day.value"
                      class="sr-only"
                    />
                    {{ day.display }}
                  </label>
                </div>
              </div>

              <!-- Halls selector -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-ink-gray-7 mb-2">Halls</label>
                <div class="flex gap-2 flex-wrap">
                  <label
                    v-for="hall in allHalls"
                    :key="hall"
                    class="cursor-pointer px-3 py-1.5 rounded-lg border text-sm select-none transition-colors"
                    :class="
                      selectedHalls.includes(hall)
                        ? 'bg-surface-gray-7 text-ink-white border-surface-gray-7'
                        : 'bg-surface-white dark:bg-surface-gray-2 text-ink-gray-6 border-outline-gray-2 hover:bg-surface-gray-2'
                    "
                  >
                    <input v-model="selectedHalls" type="checkbox" :value="hall" class="sr-only" />
                    {{ hall }}
                  </label>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex justify-end gap-3">
                <button
                  class="text-sm text-ink-gray-5 hover:text-ink-gray-9 transition-colors px-4 py-2"
                  @click="showModal = false"
                >
                  Cancel
                </button>
                <button
                  class="px-5 py-2 rounded-lg bg-surface-gray-7 text-ink-white text-sm font-semibold hover:bg-surface-gray-6 transition-colors"
                  @click="downloadSchedule"
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconDownload, IconX } from '@tabler/icons-vue'
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
})

const formats = ['ics', 'csv', 'txt', 'md', 'org', 'json']
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

const allHalls = computed(() => {
  const halls = new Set()
  for (const day of Object.values(props.schedule || {})) {
    for (const hall of Object.keys(day)) halls.add(hall)
  }
  return Array.from(halls).sort()
})

function downloadSchedule() {
  showModal.value = false
  const query = new URLSearchParams()
  query.set('event', props.event.name)
  query.set('format', selectedFormat.value)
  selectedDays.value.forEach((d) => query.append('days', d))
  selectedHalls.value.forEach((h) => query.append('halls', h))
  window.open(
    `/api/method/fossunited.api.schedule.download_schedule?${query.toString()}`,
    '_blank',
  )
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
