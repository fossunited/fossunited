<template>
  <Header />
  <div v-if="event.data && schedule.data" class="w-full flex flex-col items-center p-4">
    <div class="max-w-screen-xl w-full">
      <Breadcrumb class="mt-2" :items="breadcrumb_items" />
      <EventHeader :event="event.data" class="my-4 border-b border-gray-900 pb-4" />
      <ScheduleHeader :event="event.data" class="py-2" />
      <div
        class="flex justify-between items-end gap-4 flex-wrap"
        :class="{ 'opacity-50 pointer-events-none': isSearching }"
        :aria-disabled="isSearching"
      >
        <ScheduleDateToggle v-model="selectedDay" :dates="eventDays" class="mt-4" />
        <ScheduleViewToggle v-model="selectedScheduleView" class="mt-4 hidden sm:block" />
      </div>
      <div class="flex flex-col sm:flex-row justify-center items-start gap-6 mt-10">
        <input
          v-model="searchQuery"
          type="search"
          aria-label="Search sessions"
          autocomplete="off"
          autocapitalize="off"
          enterkeyhint="search"
          spellcheck="false"
          placeholder="Search sessions..."
          class="border border-gray-700 rounded text-sm px-3 py-2 w-full sm:max-w-sm focus:ring-gray-800 focus:border-gray-900"
        />
        <ScheduleDownload :schedule="schedule.data" :event="event.data" />
      </div>

      <ScheduleView
        v-if="!isSearching"
        :view="selectedScheduleView"
        :schedule="selectedSchedule"
        class="my-6"
      />

      <SearchSession v-else :schedule="schedule.data" :query="searchQuery" />
    </div>
  </div>
  <div v-else>
    <div class="max-w-screen-lg mx-auto mt-8 flex items-center justify-center min-h-[320px]">
      <LoadingText class="text-lg" text="Loading schedules..." />
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/schedule/EventHeader.vue'
import ScheduleHeader from '@/components/schedule/ScheduleHeader.vue'
import ScheduleDateToggle from '@/components/schedule/ScheduleDateToggle.vue'
import ScheduleViewToggle from '@/components/schedule/ScheduleViewToggle.vue'
import ScheduleView from '@/components/schedule/ScheduleView.vue'
import SearchSession from '@/components/schedule/SearchSession.vue'
import { ref, computed, watch, provide } from 'vue'
import { createResource, LoadingText, usePageMeta } from 'frappe-ui'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'

const route = useRoute()

const eventDays = ref([])
const selectedDay = ref(null)
const selectedSchedule = ref(null)
const selectedScheduleView = ref(window.innerWidth >= 1024 ? 'horizontal' : 'vertical')
const searchQuery = ref('')
const isSearching = computed(() => searchQuery.value.trim().length > 0)

const event = createResource({
  url: 'fossunited.api.dashboard.get_event_from_route',
  makeParams() {
    return {
      route: route.params.route,
      fields: ['*'],
    }
  },
  auto: true,
  transform(data) {
    if (!data.schedule_page_description) {
      data.schedule_page_description = `Explore the full schedule for ${data.event_name} to plan your experience. From keynote sessions and workshops to panel discussions and networking breaks, our schedule is designed to offer a balanced mix of learning, inspiration, and collaboration.`
    }
  },
  onSuccess(data) {
    schedule.fetch()
  },
})

provide('event', event)

const schedule = createResource({
  url: 'fossunited.api.schedule.get_event_schedule',
  makeParams() {
    return {
      event_id: event.data.name,
    }
  },
  loading: true,
  onSuccess(data) {
    eventDays.value = Object.keys(data)
    // Set to today's date if it exists, otherwise first date
    // FIXME: use ISO for dates while redesign
    const today = dayjs().format('DD/MM/YYYY')
    const todayIndex = eventDays.value.findIndex((date) => date === today)
    selectedDay.value = todayIndex !== -1 ? eventDays.value[todayIndex] : eventDays.value[0]
  },
})

watch(selectedDay, (newVal) => {
  if (newVal) {
    selectedSchedule.value = schedule.data[newVal]
  }
})

const breadcrumb_items = computed(() => {
  return [
    {
      label: event.data.event_name,
      link: event.data.has_external_webpage
        ? event.data.external_event_url
        : getRedirectRoute(event.data.route),
    },
    {
      label: 'Schedule',
    },
  ]
})

usePageMeta(() => {
  return {
    title: `${event.data.event_name} Schedule`,
  }
})

function getRedirectRoute(route) {
  return window.location.origin + '/' + route
}
</script>
