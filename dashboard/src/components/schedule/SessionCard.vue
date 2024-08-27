<template>
<div class="pt-12 pb-6 px-6 md:p-6 bg-white border border-gray-500 flex flex-col gap-3 w-full">
    <div class="flex justify-between">
        <div class="flex gap-3 md:gap-4">
            <div class="px-2 py-1 bg-green-100 text-green-600 text-xs font-medium rounded-[2px]">{{ session.category }}</div>
            <div class="px-2 py-1 bg-gray-100 text-gray-900 text-xs font-medium rounded-[2px]">{{ getDuration() }}</div>
        </div>
        <!-- add: 'Add to Calender' button -->
    </div>
    <h3 class="text-lg font-semibold tracking-[-0.18px]">{{ session.title }}</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="speaker in getSpeakers().speakers" v-if="getSpeakers()">
            <div class="flex gap-2 items-start">
                <img :src="speaker.image" :alt="speaker.name" class="w-13 h-13 rounded-[2px]">
                <div class="flex flex-col gap-1">
                    <h4 class="text-base font-medium">{{ speaker.name }}</h4>
                    <p class="text-xs text-gray-600">{{ speaker.designation }} | {{ speaker.organization }}</p>
                </div>
            </div>
        </div>
    </div>
</div>
</template>
<script setup>
import { defineProps, reactive } from 'vue'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'

dayjs.extend(duration)

const speakers = reactive({})

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

function getDuration(){
    const startTime = dayjs(`1970-01-01 ${props.session.start_time}`)
    const endTime = dayjs(`1970-01-01 ${props.session.end_time}`)

    const durationInMinutes = endTime.diff(startTime, 'minute');

    return `${durationInMinutes} minutes`
}

function getSpeakers(){
    return JSON.parse(props.session.speakers)
}
</script>
