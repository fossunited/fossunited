<template>
  <Header />

  <div v-if="event.data && schedule.data" class="w-full min-h-screen bg-surface-gray-2 dark:bg-surface-gray-1">
    <!-- ── Non-sticky: Event header ──────────────────────────────────────── -->
    <div class="max-w-[840px] mx-auto px-3 sm:px-4 pt-4 pb-2">
      <Breadcrumb :items="breadcrumb_items" />
      <EventHeader :event="event.data" class="mt-3 pb-4 border-b border-outline-gray-2" />
      <p
        v-if="event.data.schedule_page_description"
        class="mt-3 text-sm text-ink-gray-5 leading-relaxed max-w-2xl"
        v-html="sanitizedDesc"
      />
    </div>

    <!-- ── Sticky navigation ─────────────────────────────────────────────── -->
    <div class="sticky top-0 z-30 bg-surface-gray-2 dark:bg-surface-gray-1">
      <div class="max-w-[840px] mx-auto px-3 sm:px-4 pt-2 sm:pt-3">
        <div
          class="bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-xl p-2 flex flex-col gap-2 shadow-sm"
        >
          <!-- Row 1: Day selector + View toggle -->
          <div class="flex items-center gap-2">
            <div class="flex border border-outline-gray-2 rounded-lg overflow-hidden overflow-x-auto scrollbar-none flex-1 min-w-0">
              <button
                v-for="(date, index) in eventDays"
                :key="date"
                class="flex flex-col items-center justify-center w-[64px] sm:w-[72px] h-[44px] sm:h-[48px] shrink-0 border-r border-outline-gray-2 last:border-r-0 transition-colors"
                :class="selectedDay === date ? 'bg-surface-gray-3 dark:bg-surface-gray-4' : 'hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'"
                @click="selectedDay = date"
              >
                <span
                  class="text-[10px] sm:text-xs font-semibold uppercase tracking-wide leading-none"
                  :class="selectedDay === date ? 'text-ink-gray-9' : 'text-ink-gray-5'"
                >
                  Day {{ index + 1 }}
                </span>
                <span
                  class="text-[9px] sm:text-[10px] mt-0.5 leading-none"
                  :class="selectedDay === date ? 'text-ink-gray-7' : 'text-ink-gray-4'"
                >
                  {{ formatDateLabel(date) }}
                </span>
              </button>
            </div>
            <!-- View toggle -->
            <button
              class="shrink-0 h-8 flex items-center gap-1.5 px-2.5 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-7 text-xs font-semibold uppercase tracking-wide transition-colors hover:bg-surface-gray-3 dark:hover:bg-surface-gray-4"
              @click="toggleView"
            >
              <IconTimelineEventText class="w-4 h-4 shrink-0" v-if="view === 'list'" />
              <IconAlignLeft class="w-4 h-4 shrink-0" v-else />
              <span class="hidden sm:inline">{{ view === 'list' ? 'Timeline' : 'List View' }}</span>
            </button>
          </div>
          <!-- Row 2: Search + Download -->
          <div class="flex items-center gap-2">
            <div class="relative flex-1 min-w-0">
              <IconSearch class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-gray-4 pointer-events-none" />
              <input
                v-model="searchQuery"
                type="search"
                aria-label="Search sessions"
                placeholder="Search sessions..."
                autocomplete="off"
                autocapitalize="off"
                spellcheck="false"
                class="w-full h-8 pl-8 pr-3 border border-outline-gray-2 rounded-lg text-xs bg-surface-gray-1 dark:bg-surface-gray-3 text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none focus:border-outline-gray-4 transition-colors"
              />
            </div>
            <ScheduleDownload :schedule="schedule.data" :event="event.data" />
          </div>
          <!-- Row 3: Halls (list view only — same sticky card as search/days) -->
          <div
            v-if="view === 'list' && !isSearching && halls.length > 0"
            class="overflow-x-auto scrollbar-none -mx-0.5 px-0.5"
          >
            <div class="flex border border-outline-gray-2 rounded-lg overflow-hidden w-max min-w-full">
              <button
                v-for="hall in halls"
                :key="hall"
                type="button"
                class="flex-1 min-w-[94px] h-10 flex items-center justify-center px-3 border-r border-outline-gray-2 last:border-r-0 text-xs font-semibold uppercase tracking-wide transition-colors shrink-0"
                :class="
                  selectedHall === hall
                    ? 'bg-surface-gray-3 dark:bg-surface-gray-4 text-ink-gray-9'
                    : 'text-ink-gray-5 hover:bg-surface-gray-2 dark:hover:bg-surface-gray-3'
                "
                @click="selectedHall = hall"
              >
                {{ hall }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <!-- Fade shadow -->
      <div class="h-2 bg-gradient-to-b from-surface-gray-2 to-transparent pointer-events-none dark:from-surface-gray-1" />
    </div>

    <!-- ── Main content ──────────────────────────────────────────────────── -->
    <template v-if="!isSearching">
      <!-- List view -->
      <div v-if="view === 'list'" class="max-w-[840px] mx-auto px-3 sm:px-4 pb-12 w-full">
        <HallDayView :sessions="selectedHallSessions" />
      </div>
      <!-- Timeline view: expands to full viewport width if halls exceed 840px -->
      <div v-else class="w-full pb-12 px-3 sm:px-4">
        <AllDayGridView :schedule="selectedDaySchedule" />
      </div>
    </template>
    <div v-else class="max-w-[840px] mx-auto px-3 sm:px-4 pb-12 w-full">
      <SearchSession :schedule="schedule.data" :query="searchQuery" />
    </div>
  </div>

  <!-- Loading state -->
  <div v-else class="flex items-center justify-center min-h-[400px]">
    <LoadingText text="Loading schedule..." class="text-ink-gray-5" />
  </div>
</template>

<script setup>
import { ref, computed, watch, provide } from 'vue'
import { createResource, LoadingText, usePageMeta } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { IconTimelineEventText, IconAlignLeft, IconSearch } from '@tabler/icons-vue'
import DOMPurify from 'dompurify'
import dayjs from 'dayjs'

import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/common/EventHeader.vue'
import ScheduleDownload from '@/components/schedule/ScheduleDownload.vue'
import SearchSession from '@/components/schedule/SearchSession.vue'
import HallDayView from '@/components/schedule/HallDayView.vue'
import AllDayGridView from '@/components/schedule/AllDayGridView.vue'

const route = useRoute()

const eventDays = ref([])
const selectedDay = ref(null)
const selectedHall = ref(null)
const view = ref('list') // 'list' | 'allday'
const searchQuery = ref('')
const isSearching = computed(() => searchQuery.value.trim().length > 0)

function toggleView() {
  view.value = view.value === 'list' ? 'allday' : 'list'
}

function formatDateLabel(isoDate) {
  return dayjs(isoDate).format('D MMM')
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
    const todayIdx = eventDays.value.indexOf(today)
    selectedDay.value = todayIdx !== -1 ? eventDays.value[todayIdx] : eventDays.value[0]
  },
})

// Derived data

const selectedDaySchedule = computed(() => {
  if (!selectedDay.value || !schedule.data) return {}
  return schedule.data[selectedDay.value] || {}
})

const halls = computed(() => Object.keys(selectedDaySchedule.value).sort())

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

const sanitizedDesc = computed(() =>
  DOMPurify.sanitize(event.data?.schedule_page_description ?? ''),
)

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
.scrollbar-none {
  scrollbar-width: none;
}
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
