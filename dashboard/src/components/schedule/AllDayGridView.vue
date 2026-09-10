<template>
  <div class="w-full mt-4" role="region" aria-label="Timeline schedule for selected day">
    <div
      v-if="!orderedHalls.length"
      class="py-16 text-center text-ink-gray-7 dark:text-ink-gray-8"
      role="status"
    >
      No sessions for this day.
    </div>

    <div v-else :class="shouldCenter ? 'w-full' : 'max-w-[840px] mx-auto'">
      <!-- The hall header row lives outside the horizontal scroller to stay sticky-->
      <div
        ref="headerEl"
        class="sticky top-0 z-20 bg-surface-gray-2 dark:bg-surface-gray-1"
        style="overflow-x: hidden"
      >
        <div class="flex w-max" :class="{ 'mx-auto': shouldCenter }">
          <!-- Spacer matching the time axis width -->
          <div class="shrink-0 w-[34px] md:w-14 border-r border-outline-gray-3" />
          <div class="flex">
            <div
              v-for="hall in orderedHalls"
              :key="hall"
              class="h-[74px] flex items-end pb-3 px-3 shrink-0"
              style="min-width: 200px; width: 200px"
            >
              <div
                class="bg-surface-gray-3 dark:bg-surface-gray-4 text-ink-gray-9 text-xs font-semibold uppercase leading-tight px-3 py-2 rounded-lg border border-outline-gray-3 w-full text-center"
              >
                {{ hall }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Scrollable content - drives the scroll sync. -->
      <div
        ref="contentEl"
        style="overflow-x: auto; overflow-y: clip; padding-bottom: 360px"
        @scroll.passive="syncHeader"
      >
        <div class="flex w-max" :class="{ 'mx-auto': shouldCenter }">
          <!-- Time axis, sticky left during horizontal scroll  -->
          <div
            class="sticky left-0 z-20 shrink-0 w-[34px] md:w-14 border-r border-outline-gray-3 bg-surface-gray-2 dark:bg-surface-gray-1"
            :style="{ height: totalHeight + 'px' }"
            aria-label="Time of day"
          >
            <div
              v-for="label in timeLabels"
              :key="label.minutes"
              class="absolute right-0 md:right-1.5 flex items-center gap-1"
              :style="{ top: offsetFor(label.minutes) + 'px', transform: 'translateY(-50%)' }"
            >
              <span
                class="text-[10px] font-semibold text-ink-gray-7 dark:text-ink-gray-8 whitespace-nowrap"
              >
                {{ label.label }}
              </span>
              <div class="hidden md:block w-2 h-px bg-surface-gray-5" />
            </div>
          </div>

          <!-- Hall columns -- sessions only, headers live in the pinned row above -->
          <div class="flex">
            <div v-for="hall in orderedHalls" :key="hall" style="min-width: 200px; width: 200px">
              <div class="relative" :style="{ height: totalHeight + 'px' }">
                <div class="absolute inset-y-0 left-4 border-l border-outline-gray-5" />
                <div
                  v-for="label in timeLabels"
                  :key="'grid-' + label.minutes"
                  class="absolute left-0 right-0 border-t border-outline-gray-3"
                  :style="{ top: offsetFor(label.minutes) + 'px' }"
                />
                <div
                  v-for="placed in hallSessions(hall)"
                  :key="placed.session.name || placed.session.title"
                  class="absolute left-0 right-0 px-2"
                  :style="{ top: placed.top + 'px' }"
                >
                  <TimeCapsule :session="placed.session" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import TimeCapsule from '@/components/schedule/TimeCapsule.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true, // { hall: [sessions] }
  },
  // Hall names in the organiser's order, from the event's `hall_options`.
  // Falls back to the schedule's own key order when not supplied.
  halls: {
    type: Array,
    default: null,
  },
})

const PIXELS_PER_MINUTE = 6 // 60px = 10 min
const HALL_WIDTH = 200 // px per hall column
const TIME_AXIS_WIDTH = 56 // px (w-14 on desktop)
const CAPSULE_HEIGHT = 60 // px, matches TimeCapsule's own fixed h-[60px]
// space for kickstart
const TOP_PADDING = 14 // px

const headerEl = ref(null)
const contentEl = ref(null)

function syncHeader() {
  if (headerEl.value && contentEl.value) {
    headerEl.value.scrollLeft = contentEl.value.scrollLeft
  }
}
const CENTER_THRESHOLD = 840 // px — center only when content exceeds this

const orderedHalls = computed(() => {
  const present = Object.keys(props.schedule || {})
  if (!props.halls?.length) return present
  // Trust the page's order, but never render a column with no data behind it.
  const presentSet = new Set(present)
  return props.halls.filter((hall) => presentSet.has(hall))
})

// Apply mx-auto centering only when total content width exceeds the threshold
const shouldCenter = computed(
  () => orderedHalls.value.length * HALL_WIDTH + TIME_AXIS_WIDTH > CENTER_THRESHOLD,
)

// show overlapping short session above & below and not behind
function hallSessions(hall) {
  const sorted = (props.schedule[hall] || [])
    .slice()
    .sort((a, b) => toMinutes(a.start_time) - toMinutes(b.start_time))

  let cursor = -Infinity
  return sorted.map((session) => {
    const top = Math.max(offsetFor(toMinutes(session.start_time)), cursor)
    cursor = top + CAPSULE_HEIGHT
    return { session, top }
  })
}

function toMinutes(timeStr) {
  if (!timeStr) return 0
  const str = typeof timeStr === 'string' ? timeStr : String(timeStr)
  const parts = str.split(':').map(Number)
  return (parts[0] || 0) * 60 + (parts[1] || 0)
}

function offsetFor(minutes) {
  return (minutes - timeRange.value.min) * PIXELS_PER_MINUTE + TOP_PADDING
}

const DEFAULT_RANGE = { min: 9 * 60, max: 18 * 60 }

const timeRange = computed(() => {
  const all = Object.values(props.schedule || {}).flat()
  const starts = all.filter((s) => s?.start_time).map((s) => toMinutes(s.start_time))
  const ends = all
    .filter((s) => s?.end_time || s?.start_time)
    .map((s) => toMinutes(s.end_time || s.start_time))

  if (!starts.length || !ends.length) return DEFAULT_RANGE

  return {
    min: Math.floor(Math.min(...starts) / 30) * 30,
    max: Math.ceil((Math.max(...ends) + 30) / 30) * 30,
  }
})

const totalHeight = computed(
  () => (timeRange.value.max - timeRange.value.min) * PIXELS_PER_MINUTE + TOP_PADDING,
)

// 30-minute steps: most sessions run 25 minutes or less
const timeLabels = computed(() => {
  const labels = []
  for (let m = timeRange.value.min; m <= timeRange.value.max; m += 30) {
    labels.push({ minutes: m, label: minutesToAmPm(m) })
  }
  return labels
})

function minutesToAmPm(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  const ampm = h < 12 ? 'AM' : 'PM'
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
  return m === 0 ? `${h12} ${ampm}` : `${h12}:${m.toString().padStart(2, '0')}`
}
</script>
