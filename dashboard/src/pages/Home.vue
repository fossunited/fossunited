<template>
  <Header></Header>
  <div class="bg-gray-50 justify-center align-middle flex">
    <div class="flex container py-8 px-4 h-screen">
      <main class="w-full space-y-4">
        <div class="greet-user" v-if="profile.data">
          <div class="text-3xl font-semibold my-2">
            Hello {{ profile.data.full_name.split(' ')[0] }},
          </div>
          <div class="text-gray-600">
            This is the organizer's dashboard. You can manage your chapters,
            events, and more from here.
          </div>
        </div>
        <div>
          <div class="text-lg font-semibold my-2">Your Chapters</div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="chapter in chapters.data"
              :key="chapter.name"
              class="py-2"
            >
              <ChapterCard :chapter="chapter"></ChapterCard>
            </div>
          </div>
        </div>
        <div>
          <div class="text-lg font-semibold my-2">Scheduled Events</div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="event in scheduled_events.data"
              :key="event.name"
              class="py-2"
            >
              <EventCard :event="event" />
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { inject, watch } from 'vue'
import Header from '@/components/Header.vue'
import EventCard from '@/components/EventCard.vue'
import ChapterCard from '@/components/ChapterCard.vue'
import { createResource, createListResource, usePageMeta } from 'frappe-ui'
const session = inject('$session')

const chapters = createListResource({
  doctype: 'FOSS Chapter',
  fields: ['*'],
  filters: [
    ['FOSS Chapter Lead Team Member', 'email', 'like', `%${session.user}%`],
  ],
  auto: true,
  pageLength: 999,
  onSuccess(data) {
    if (!data.length) {
        return
    }
    profile.fetch()
    scheduled_events.update({
      filters: {
        ...scheduled_events.filters,
        chapter: ['in', data.map((d) => d.name)],
      },
    })
    scheduled_events.fetch()
  },
})
const scheduled_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: [
    'name',
    'event_name',
    'event_type',
    'chapter_name',
    'status',
    'event_start_date',
  ],
  filters: {
    status: ['in', ['', 'Draft', 'Approved', 'Live']],
  },
  orderBy: 'event_start_date',
})

const profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
