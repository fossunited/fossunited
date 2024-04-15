<template>
<div v-if="chapter.doc" class="p-8 w-full min-h-screen">
    <div class="flex justify-between">
        <div class="flex flex-col gap-3">
            <FossClubBranding v-if="chapter.doc.chapter_type == 'FOSS Club'">{{ chapter.doc.chapter_type }}</FossClubBranding>
            <CityCommunityBranding v-else>{{ chapter.doc.chapter_type.toUpperCase() }}</CityCommunityBranding>
            <div class="text-3xl font-semibold">{{ chapter.doc.chapter_name }}</div>
        </div>
    </div>
    <div class="flex flex-col mt-4 gap-3 w-fit">
        <div class="text-base text-gray-600">
            View and Create events for your chapter.
        </div>
        <Button
            class="w-fit"
            label="Create New Event"
            icon-left="plus"
            size="md"
        />
    </div>
    <div class="flex flex-col gap-8 my-6">
        <div class="flex flex-col gap-3">
            <div class="text-2xl font-semibold">Scheduled Events</div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                <EventCardDashboard v-for="event in upcoming_events.data" :key="event.name" :event="event" />
            </div>
        </div>
        <div class="flex flex-col gap-3">
            <div class="text-2xl font-semibold">Concluded Events</div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                <EventCardDashboard v-for="event in past_events.data" :key="event.name" :event="event" />
            </div>
        </div>
    </div>
</div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, createListResource } from 'frappe-ui'
import CityCommunityBranding from '@/components/CityCommunityBranding.vue'
import FossClubBranding from '@/components/FossClubBranding.vue'
import EventCardDashboard from '@/components/EventCardDashboard.vue'
const route = useRoute();

const chapter = createDocumentResource({
    doctype: 'FOSS Chapter',
    name: `${decodeURI(route.params.id)}`,
    fields: ['*'],
    auto: true,
})

const upcoming_events = createListResource({
    doctype: 'FOSS Chapter Event',
    fields: ['*'],
    filters: [['chapter', '=', `${decodeURI(route.params.id)}`], ['event_start_date', '>', new Date()], ['status', 'in', ['Approved', 'Being Reviewed', 'In Progress']]],
    auto: true,
})

const past_events = createListResource({
    doctype: 'FOSS Chapter Event',
    fields: ['*'],
    filters: [['chapter', '=', `${decodeURI(route.params.id)}`], ['event_start_date', '<', new Date()], ['status', 'in', ['Concluded', 'Cancelled']]],
    auto: true,
})
</script>
