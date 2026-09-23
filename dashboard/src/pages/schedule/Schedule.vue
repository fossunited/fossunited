<template>
  <Header :sticky="false" />

  <div
    v-if="event.data && schedule.data"
    class="w-full min-h-screen bg-surface-gray-2 dark:bg-surface-gray-1"
  >
    <!-- ── Non-sticky: Event header ──────────────────────────────────────── -->
    <div class="max-w-[840px] mx-auto px-3 sm:px-4 pt-4 pb-2">
      <Breadcrumb :items="breadcrumb_items" />
      <EventHeader :event="event.data" class="mt-3 pb-4 border-b border-outline-gray-3" />
      <!-- Organiser note, rendered from the event's Markdown Editor field. -->
      <div
        v-if="sanitizedDesc"
        class="schedule-note mt-3 rounded-lg border border-outline-gray-3 bg-surface-gray-1 dark:bg-surface-gray-2 px-4 py-3 text-sm text-ink-gray-7 dark:text-ink-gray-8 leading-relaxed"
        v-html="sanitizedDesc"
      />
    </div>

    <!-- Sticky navigation. It slides out of sight on scroll down and back on scroll up -->
    <div
      ref="navEl"
      class="sticky top-0 z-40 bg-surface-gray-2 dark:bg-surface-gray-1 transition-transform duration-300 ease-in-out motion-reduce:transition-none"
      :class="{ '-translate-y-full': !navVisible }"
      @focusin="navVisible = true"
    >
      <div class="max-w-[840px] mx-auto px-3 sm:px-4 pt-2 sm:pt-3">
        <div
          class="bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-3 rounded-xl p-2 flex flex-col gap-2 shadow-sm"
        >
          <!-- Row 1: Day selector + View switch -->
          <div class="flex items-center gap-2">
            <div
              class="flex border border-outline-gray-3 rounded-lg overflow-hidden overflow-x-auto scrollbar-none flex-1 min-w-0"
              role="group"
              aria-label="Select event day"
            >
              <button
                v-for="(date, index) in eventDays"
                :key="date"
                type="button"
                :aria-pressed="selectedDay === date"
                :aria-label="`Day ${index + 1}, ${formatFullDate(date)}`"
                class="flex-1 flex flex-col items-center justify-center min-w-[64px] sm:min-w-[72px] h-[44px] sm:h-[48px] border-r border-outline-gray-3 last:border-r-0 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-outline-gray-5"
                :class="selectedDay === date ? SEG_ON : SEG_OFF"
                @click="selectedDay = date"
              >
                <span
                  class="text-[10px] sm:text-xs font-semibold uppercase tracking-wide leading-none"
                >
                  Day {{ index + 1 }}
                </span>
                <span class="text-[9px] sm:text-[10px] mt-0.5 leading-none">
                  {{ formatDateLabel(date) }}
                </span>
              </button>
            </div>
            <!-- Toggle buttons -->
            <div
              class="shrink-0 flex border border-outline-gray-3 rounded-lg overflow-hidden"
              role="group"
              aria-label="Schedule view"
            >
              <button
                v-for="option in viewOptions"
                :key="option.value"
                type="button"
                :aria-pressed="view === option.value"
                :aria-label="option.label + ' view'"
                class="h-8 flex items-center gap-1.5 px-2.5 text-xs font-semibold uppercase tracking-wide transition-colors border-r border-outline-gray-3 last:border-r-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-outline-gray-5"
                :class="view === option.value ? SEG_ON : SEG_OFF"
                @click="view = option.value"
              >
                <component :is="option.icon" class="w-4 h-4 shrink-0" aria-hidden="true" />
                <span class="hidden sm:inline">{{ option.label }}</span>
              </button>
            </div>
          </div>
          <!-- Row 2: Search + Download -->
          <div class="flex items-center gap-2">
            <div class="relative flex-1 min-w-0">
              <IconSearch
                class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-gray-7 dark:text-ink-gray-8 pointer-events-none"
                aria-hidden="true"
              />
              <input
                v-model="searchQuery"
                type="search"
                aria-label="Search sessions"
                placeholder="Search sessions..."
                autocomplete="off"
                autocapitalize="off"
                spellcheck="false"
                class="w-full h-8 pl-8 pr-3 border border-outline-gray-3 rounded-lg text-xs bg-surface-gray-1 dark:bg-surface-gray-3 text-ink-gray-9 placeholder:text-ink-gray-7 dark:placeholder:text-ink-gray-8 focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-5 focus:border-outline-gray-4 transition-colors"
              />
            </div>
            <ScheduleDownload
              :schedule="schedule.data"
              :event="event.data"
              :hall-order="hallOrder"
            />
          </div>
          <!-- All | Live | Mine. Only rendered once there is something to switch to -->
          <div
            v-if="modes.length > 1 && !isSearching"
            class="flex border border-outline-gray-3 rounded-lg overflow-hidden"
            role="group"
            aria-label="Filter sessions"
          >
            <button
              v-for="m in modes"
              :key="m.id"
              type="button"
              :aria-pressed="mode === m.id"
              class="flex-1 h-8 flex items-center justify-center gap-1.5 border-r border-outline-gray-3 last:border-r-0 text-[10px] font-semibold uppercase tracking-wide transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-outline-gray-5"
              :class="mode === m.id ? SEG_ON : SEG_OFF"
              @click="mode = m.id"
            >
              <span
                v-if="m.id === 'live'"
                class="w-1.5 h-1.5 rounded-full bg-current animate-pulse motion-reduce:animate-none"
                aria-hidden="true"
              />
              {{ m.label }}
              <span v-if="m.count" class="font-normal">{{ m.count }}</span>
            </button>
          </div>

          <!--
            Row 4: Halls (list view only). One boxy group like the day selector,
            but wrapping so every hall is visible. The 1px gaps over a tinted
            container draw the dividers, which is what makes a joined group
            survive a wrap -- border-r alone cannot rule between two rows.

            min-h rather than a fixed height, and no truncate: a name too long
            for the row wraps inside its own button instead of being cut off.
          -->
          <div
            v-if="view === 'list' && !isSearching && !narrowed && halls.length > 0"
            class="flex flex-wrap gap-px bg-surface-gray-4 border border-outline-gray-3 rounded-lg overflow-hidden"
            role="group"
            aria-label="Select hall"
          >
            <button
              v-for="hall in halls"
              :key="hall"
              type="button"
              :aria-pressed="selectedHall === hall"
              class="flex-1 min-h-[44px] flex items-center justify-center px-4 py-1.5 text-xs font-semibold uppercase tracking-wide leading-tight text-center transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-outline-gray-5"
              :class="
                selectedHall === hall
                  ? SEG_ON
                  : `bg-surface-white dark:bg-surface-gray-2 ${SEG_OFF}`
              "
              @click="selectedHall = hall"
            >
              {{ hall }}
            </button>
          </div>
        </div>
      </div>
      <!-- Fade shadow -->
      <div
        class="h-2 bg-gradient-to-b from-surface-gray-2 to-transparent pointer-events-none dark:from-surface-gray-1"
      />
    </div>

    <!-- ── Main content ──────────────────────────────────────────────────── -->
    <!--
      Live and Mine: one flat cross-hall list each, the same SessionCard the
      search results use, with the hall shown on the card instead of picked
      from a selector.
    -->
    <div v-if="narrowed && !isSearching" class="max-w-[840px] mx-auto px-3 sm:px-4 pb-12 w-full">
      <SearchSession
        :schedule="schedule.data"
        :filter="narrowed.filter"
        :label="narrowed.title"
        :empty-text="narrowed.empty"
      />
    </div>

    <template v-else-if="!isSearching">
      <!-- List view -->
      <div v-if="view === 'list'" class="max-w-[840px] mx-auto px-3 sm:px-4 pb-12 w-full">
        <HallDayView :sessions="selectedHallSessions" />
      </div>
      <!-- Timeline view: expands to full viewport width if halls exceed 840px -->
      <div v-else class="w-full pb-12 px-3 sm:px-4">
        <AllDayGridView :schedule="selectedDaySchedule" :halls="halls" />
      </div>
    </template>
    <div v-if="isSearching" class="max-w-[840px] mx-auto px-3 sm:px-4 pb-12 w-full">
      <SearchSession :schedule="schedule.data" :query="searchQuery" />
    </div>
  </div>

  <!-- Loading state -->
  <div v-else class="flex items-center justify-center min-h-[400px]">
    <LoadingText text="Loading schedule..." class="text-ink-gray-7 dark:text-ink-gray-8" />
  </div>
</template>

<script setup>
import { ref, computed, watch, provide, onMounted, onUnmounted } from 'vue'
import { createResource, LoadingText, usePageMeta } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { IconTimelineEventText, IconAlignLeft, IconSearch } from '@tabler/icons-vue'
import DOMPurify from 'dompurify'
import { markdownToHTML } from 'frappe-ui/src/utils/markdown'
import dayjs from 'dayjs'

import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/common/EventHeader.vue'
import ScheduleDownload from '@/components/schedule/ScheduleDownload.vue'
import SearchSession from '@/components/schedule/SearchSession.vue'
import HallDayView from '@/components/schedule/HallDayView.vue'
import { isSessionLive } from '@/helpers/date'
import AllDayGridView from '@/components/schedule/AllDayGridView.vue'

const route = useRoute()

const eventDays = ref([])
const selectedDay = ref(null)
const selectedHall = ref(null)
const view = ref('list') // 'list' | 'allday'
const searchQuery = ref('')
const isSearching = computed(() => searchQuery.value.trim().length > 0)

// ── All | Live now
const countMatching = (predicate) =>
  Object.values(schedule.data ?? {})
    .flatMap((day) => Object.values(day).flat())
    .filter(predicate).length

const NARROWED = {
  live: {
    label: 'Live Now',
    title: 'Live Now',
    empty: 'Nothing running right now.',
    filter: isSessionLive,
    count: () => countMatching(isSessionLive),
  },
}

const mode = ref('all')

const modes = computed(() => [
  { id: 'all', label: 'All' },
  ...Object.entries(NARROWED)
    .map(([id, m]) => ({ ...m, id, count: m.count() }))
    .filter((m) => m.count),
])

// Null on All, and falls back to it the moment the active option stops existing
// -- the last live session ending mid-view.
const narrowed = computed(() => modes.value.find((m) => m.id === mode.value && m.filter))

// Days, view switch and All/Live/Mine are the same segmented control, so they
// share one pair of state classes rather than three copies of each.
const SEG_ON = 'bg-surface-gray-7 text-ink-white'
const SEG_OFF =
  'text-ink-gray-7 dark:text-ink-gray-8 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'

const viewOptions = [
  { value: 'list', label: 'List', icon: IconAlignLeft },
  { value: 'allday', label: 'Timeline', icon: IconTimelineEventText },
]

// ── Scroll-reveal nav ─────────────────────────────────────────────────────
const SCROLL_DELTA_MIN = 6 // px — swallows iOS rubber-band and trackpad jitter

const navEl = ref(null)
const navVisible = ref(true)
let lastScrollY = 0
let scrollQueued = false

function readScroll() {
  scrollQueued = false
  const y = Math.max(0, window.scrollY)
  const delta = y - lastScrollY

  // Leave lastScrollY untouched below the threshold so slow scrolls still accumulate.
  if (Math.abs(delta) < SCROLL_DELTA_MIN) return

  /*
   * Hide only once the nav has actually reached the top and stuck. Until then it
   * still occupies its slot in normal flow, so translating it away leaves a hole
   * exactly its own height -- which is the blank space that showed up on a short
   * scroll. offsetTop is a layout value, so neither the sticky offset nor the
   * transform skews it, and reading it live keeps up with the event header being
   * collapsed or the viewport being resized.
   */
  const stickPoint = navEl.value?.offsetTop ?? 0

  if (delta > 0 && y > stickPoint) navVisible.value = false
  else if (delta < 0) navVisible.value = true
  lastScrollY = y
}

function onScroll() {
  if (scrollQueued) return
  scrollQueued = true
  requestAnimationFrame(readScroll)
}

onMounted(() => {
  lastScrollY = Math.max(0, window.scrollY)
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => window.removeEventListener('scroll', onScroll))

function formatDateLabel(isoDate) {
  return dayjs(isoDate).format('D MMM')
}

function formatFullDate(isoDate) {
  return dayjs(isoDate).format('dddd, D MMMM YYYY')
}

// Data fetching
const event = createResource({
  url: 'fossunited.api.dashboard.get_event',
  makeParams() {
    return { name: route.params.route, by_route: true }
  },
  auto: true,
  onSuccess() {
    schedule.fetch()
  },
})

provide('event', event)

const schedule = createResource({
  url: 'fossunited.api.schedule.get_event_schedule',
  makeParams() {
    return { event_id: event.data.name }
  },
  loading: true,
  onSuccess(data) {
    eventDays.value = Object.keys(data)
    const today = dayjs().format('YYYY-MM-DD')
    selectedDay.value = eventDays.value.includes(today) ? today : eventDays.value[0]
  },
})

// Derived data

const selectedDaySchedule = computed(() => {
  if (!selectedDay.value || !schedule.data) return {}
  return schedule.data[selectedDay.value] || {}
})

/**
 * Hall order is the organiser's: the line order of the event's `hall_options`
 * field. Never sorted. Parsed once here and handed to everything that renders a
 * hall list, so the page and the download dialog cannot disagree.
 */
const hallOrder = computed(() =>
  (event.data?.hall_options || '')
    .split('\n')
    .map((hall) => hall.trim())
    .filter(Boolean),
)

/**
 * Halls in the selected day, in the organiser's order. Halls `hall_options` does
 * not mention keep the schedule's own order and come last, so a session in an
 * unlisted hall is never dropped. With no `hall_options` set, schedule order stands.
 */
const halls = computed(() => {
  const present = Object.keys(selectedDaySchedule.value)
  // No hall_options: busiest hall first, so the main track leads instead of
  // whichever hall happened to open earliest.
  if (!hallOrder.value.length) {
    const day = selectedDaySchedule.value
    return present.slice().sort((a, b) => day[b].length - day[a].length)
  }

  const configuredSet = new Set(hallOrder.value)
  return [
    ...hallOrder.value.filter((hall) => present.includes(hall)),
    ...present.filter((hall) => !configuredSet.has(hall)),
  ]
})

watch(
  halls,
  (newHalls) => {
    if (newHalls.length > 0 && (!selectedHall.value || !newHalls.includes(selectedHall.value))) {
      selectedHall.value = newHalls[0]
    }
  },
  { immediate: true },
)

const selectedHallSessions = computed(() => {
  if (!selectedHall.value || !selectedDaySchedule.value) return []
  return selectedDaySchedule.value[selectedHall.value] || []
})

// schedule_page_description is a Markdown Editor field. marked does not
// sanitise -- it passes inline HTML straight through -- so DOMPurify is doing
// real work here, not belt-and-braces.
const sanitizedDesc = computed(() => {
  const markdown = event.data?.schedule_page_description
  return markdown ? DOMPurify.sanitize(markdownToHTML(markdown)) : ''
})

const breadcrumb_items = computed(() => {
  if (!event.data) return []
  return [
    {
      label: event.data.event_name,
      link: event.data.has_external_webpage
        ? event.data.external_event_url
        : window.location.origin + '/' + event.data.route,
    },
    { label: 'Schedule' },
  ]
})

usePageMeta(() => ({
  title: event.data ? `${event.data.event_name} – Schedule` : 'Schedule',
}))
</script>

<style scoped>
.schedule-note :deep(> *:first-child) {
  margin-top: 0;
}
.schedule-note :deep(> *:last-child) {
  margin-bottom: 0;
}
.schedule-note :deep(p),
.schedule-note :deep(ul),
.schedule-note :deep(ol) {
  margin: 0 0 0.5rem;
}
.schedule-note :deep(ul),
.schedule-note :deep(ol) {
  padding-left: 1.25rem;
}
.schedule-note :deep(ul) {
  list-style: disc;
}
.schedule-note :deep(ol) {
  list-style: decimal;
}
.schedule-note :deep(li) {
  margin-bottom: 0.125rem;
}
.schedule-note :deep(h1),
.schedule-note :deep(h2),
.schedule-note :deep(h3),
.schedule-note :deep(h4) {
  margin: 0.75rem 0 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgb(var(--ink-gray-9));
}
.schedule-note :deep(strong) {
  font-weight: 600;
  color: rgb(var(--ink-gray-9));
}
/* Underlined, not colour-only: colour alone as the link cue fails WCAG 1.4.1. */
.schedule-note :deep(a) {
  color: rgb(var(--ink-gray-9));
  text-decoration: underline;
}
.schedule-note :deep(a:hover) {
  text-decoration-thickness: 2px;
}
.schedule-note :deep(code) {
  padding: 0.0625rem 0.25rem;
  border-radius: 0.25rem;
  background-color: rgb(var(--surface-gray-3));
  color: rgb(var(--ink-gray-9));
  font-size: 0.8125rem;
}
.schedule-note :deep(pre) {
  margin: 0 0 0.5rem;
  padding: 0.5rem 0.75rem;
  overflow-x: auto;
  border-radius: 0.375rem;
  background-color: rgb(var(--surface-gray-3));
}
.schedule-note :deep(pre code) {
  padding: 0;
  background: none;
}
.schedule-note :deep(hr) {
  margin: 0.75rem 0;
  border-color: rgb(var(--outline-gray-3));
}
.schedule-note :deep(blockquote) {
  margin: 0 0 0.5rem;
  padding-left: 0.75rem;
  border-left: 2px solid rgb(var(--outline-gray-3));
}

.scrollbar-none {
  scrollbar-width: none;
}
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
