<template>
  <div class="w-full mt-4">
    <div v-if="!sortedHalls.length" class="py-16 text-center text-ink-gray-4">
      No sessions for this day.
    </div>

    <!--
      Narrow (≤ 840px): container matches the 840px page column so content starts
      from the same left edge as the nav. overflow-y:clip prevents the implicit
      overflow-y:auto browsers apply when overflow-x is set.

      Wide (> 840px): container is full-width and mx-auto on the w-max inner block
      centers the content (time axis + halls together) symmetrically on the viewport.
    -->
    <div
      v-else
      :class="shouldCenter ? 'w-full' : 'max-w-[840px] mx-auto'"
      style="overflow-x: auto; overflow-y: clip"
    >
      <div
        class="flex w-max"
        :class="{ 'mx-auto': shouldCenter }"
      >
        <!-- Time axis: sticky so it stays visible during horizontal scroll -->
        <div
          class="sticky left-0 z-10 shrink-0 w-14 relative border-r border-outline-gray-2 bg-surface-gray-2 dark:bg-surface-gray-1"
          :style="{ height: totalHeight + 74 + 'px' }"
        >
          <div
            v-for="label in timeLabels"
            :key="label.minutes"
            class="sticky absolute right-1.5 flex items-center gap-1"
            :style="{ top: offsetFor(label.minutes) + 74 + 'px', transform: 'translateY(-50%)' }"
          >
            <span class="text-[10px] font-semibold text-ink-gray-5 whitespace-nowrap">
              {{ label.label }}
            </span>
            <div class="w-2 h-px bg-outline-gray-3" />
          </div>
          <div
            v-for="label in halfLabels"
            :key="'h' + label.minutes"
            class="absolute right-1"
            :style="{ top: offsetFor(label.minutes) + 74 + 'px', transform: 'translateY(-50%)' }"
          >
            <div class="w-1.5 h-px bg-outline-gray-2" />
          </div>
        </div>

        <!-- Hall columns -->
        <div class="flex">
          <div
            v-for="hall in sortedHalls"
            :key="hall"
            class="flex flex-col"
            style="min-width: 200px; width: 200px"
          >
            <!-- Hall header -->
            <div class="h-[74px] flex items-end pb-3 px-3 shrink-0">
              <div
                class="bg-surface-gray-3 dark:bg-surface-gray-4 text-ink-gray-7 text-xs font-semibold uppercase px-3 py-2 rounded-lg border border-outline-gray-2 whitespace-nowrap w-full text-center"
              >
                {{ hall }}
              </div>
            </div>

            <!-- Sessions area -->
            <div class="relative" :style="{ height: totalHeight + 'px' }">
              <div class="absolute inset-y-0 left-4 border-l border-outline-gray-5" />
              <div
                v-for="label in timeLabels"
                :key="'grid-' + label.minutes"
                class="absolute left-0 right-0 border-t border-outline-gray-2"
                :style="{ top: offsetFor(label.minutes) + 'px' }"
              />
              <div
                v-for="session in hallSessions(hall)"
                :key="session.name || session.title"
                class="absolute left-0 right-0 px-2"
                :style="{ top: offsetFor(toMinutes(session.start_time)) + 'px' }"
              >
                <TimeCapsule :session="session" />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TimeCapsule from '@/components/schedule/TimeCapsule.vue'

const props = defineProps({
  schedule: {
    type: Object,
    required: true, // { hall: [sessions] }
  },
})

const PIXELS_PER_MINUTE = 6  // 60px = 10 min
const HALL_WIDTH = 200        // px per hall column
const TIME_AXIS_WIDTH = 56    // px (w-14)
const CENTER_THRESHOLD = 840  // px — center only when content exceeds this

const sortedHalls = computed(() => Object.keys(props.schedule || {}).sort())

// Apply mx-auto centering only when total content width exceeds the threshold
const shouldCenter = computed(
  () => sortedHalls.value.length * HALL_WIDTH + TIME_AXIS_WIDTH > CENTER_THRESHOLD,
)

function hallSessions(hall) {
  return (props.schedule[hall] || []).slice().sort(
    (a, b) => toMinutes(a.start_time) - toMinutes(b.start_time),
  )
}

function toMinutes(timeStr) {
  if (!timeStr) return 0
  const str = typeof timeStr === 'string' ? timeStr : String(timeStr)
  const parts = str.split(':').map(Number)
  return (parts[0] || 0) * 60 + (parts[1] || 0)
}

function offsetFor(minutes) {
  return (minutes - timeRange.value.min) * PIXELS_PER_MINUTE
}

const timeRange = computed(() => {
  const all = Object.values(props.schedule || {}).flat()
  if (!all.length) return { min: 9 * 60, max: 18 * 60 }
  const starts = all.map((s) => toMinutes(s.start_time)).filter(Boolean)
  const ends = all.map((s) => toMinutes(s.end_time || s.start_time)).filter(Boolean)
  return {
    min: Math.floor(Math.min(...starts) / 30) * 30,
    max: Math.ceil((Math.max(...ends) + 30) / 30) * 30,
  }
})

const totalHeight = computed(
  () => (timeRange.value.max - timeRange.value.min) * PIXELS_PER_MINUTE,
)

const timeLabels = computed(() => {
  const labels = []
  for (let m = timeRange.value.min; m <= timeRange.value.max; m += 60) {
    labels.push({ minutes: m, label: minutesToAmPm(m) })
  }
  return labels
})

const halfLabels = computed(() => {
  const labels = []
  for (let m = timeRange.value.min + 30; m < timeRange.value.max; m += 60) {
    labels.push({ minutes: m })
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
