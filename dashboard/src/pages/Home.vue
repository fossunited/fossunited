<template>
  <Header></Header>
  <div class=" bg-gray-50 justify-center align-middle flex">
    <div class="flex container py-8 h-screen">
      <main class="w-full">
        <div class="greet-user">
          <div class="text-3xl font-semibold my-2">
            Hello <span v-if="profile.data">{{ profile.data.full_name.split(" ")[0] }}</span>,
          </div>
          <div class=" text-gray-600">
            This is the organizer's dashboard. You can manage your chapters, events, and more from here.
          </div>
        </div>
        <div class="py-4">
          <div class="text-lg font-semibold my-2">Your Chapters</div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="chapter in chapter.data"
              :key="chapter.name"
              class="py-2"
            >
              <ChapterCard :chapter="chapter"></ChapterCard>
            </div>
          </div>
        </div>
        <div class="py-4">
          <div class="text-lg font-semibold my-2">Scheduled Events</div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="event in scheduled_events.data"
              :key="event.name"
            >
              <EventCardDashboard :event="event"></EventCardDashboard>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { createResource, createListResource, usePageMeta, ListView, Badge } from 'frappe-ui'
import Header from '@/components/Header.vue'
import ChapterCard from '@/components/ChapterCard.vue'
import { session } from '@/data/session.js'
import { watch, ref } from 'vue'
import EventCardDashboard from '@/components/EventCardDashboard.vue'

let chapter = createListResource({
  doctype: 'FOSS Chapter',
  fields: ['*'],
  filters: [
    [
        "FOSS Chapter Lead Team Member",
        "email",
        "like",
        `%${session.user}%`,
    ]
  ],
  auto: true,
})

let scheduled_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: ['name', 'event_name', 'event_type', 'chapter_name', 'status', 'event_start_date'],
  filters: {
    status: ['in', ['', 'Being Reviewed', 'Approved']],
  },
  // transform the event start date to be 'Date Month' only
  transform: (data) => {
    return data.map(d => {
      return {
        ...d,
        event_start_date: new Date(d.event_start_date).toLocaleDateString('en-IN', { day: 'numeric', month:'long', year: 'numeric'})
      }
    })
  },
  auto: true,
})

watch(chapter, (newChapter) => {
  if (newChapter.data){
    scheduled_events.update({
      filters: {
        chapter: ['in', newChapter.data.map(d => d.name)]
      }
    })
    scheduled_events.fetch()
  }
})


let profile = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS User Profile',
    filters: {
      email: session.user,
    }
  },
  auto: true,
})


usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
