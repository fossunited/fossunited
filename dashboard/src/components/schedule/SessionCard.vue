<template>
  <div
    class="pt-12 pb-6 px-6 md:p-6 bg-white border border-gray-500 flex flex-col gap-3 w-full"
  >
    <div class="flex justify-between">
      <div class="flex gap-3 md:gap-4">
        <div
          class="px-2 py-1 bg-green-100 text-green-600 text-xs font-medium rounded-[2px]"
        >
          {{
            session.category != 'Other'
              ? session.category
              : session.other_category
          }}
        </div>
        <div
          class="px-2 py-1 bg-gray-100 text-gray-900 text-xs font-medium rounded-[2px]"
        >
          {{ getDuration() }}
        </div>
      </div>
      <!-- add: 'Add to Calender' button -->
      <button
        class="px-2 py-1 bg-gray-900 text-white text-xs font-medium rounded-[2px] flex gap-2 items-center"
        @click="downloadSessionIcs.fetch()"
      >
        <CalenderAddIcon class="w-4 h-4" />
        <span class="hidden md:block uppercase">Add to Calender</span>
      </button>
    </div>
    <h3 class="text-lg font-semibold tracking-[-0.18px]">
      {{ session.title }}
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="speaker in getSpeakers().speakers" v-if="getSpeakers()">
        <div class="flex gap-2 items-start">
          <img
            :src="speaker.image"
            :alt="speaker.name"
            class="w-13 h-13 rounded-[2px] object-cover object-top"
          />
          <div class="flex flex-col gap-1">
            <h4 class="text-base font-medium">{{ speaker.name }}</h4>
            <p class="text-xs text-gray-600">
              {{ speaker.designation }} | {{ speaker.organization }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'
import { defineProps, reactive } from 'vue'
import CalenderAddIcon from '@/components/icons/CalenderAddIcon.vue'
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

const downloadSessionIcs = createResource({
    url: 'fossunited.api.schedule.get_schedule_session_ics',
    makeParams(){
        return {
            schedule: props.session
        }
    },
    onSuccess(data){
        const blob = new Blob([data], { type: 'text/calendar' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${props.session.title}.ics`
        a.click()
        window.URL.revokeObjectURL(url)
    }
})

function getDuration() {
  const startTime = dayjs(`1970-01-01 ${props.session.start_time}`)
  const endTime = dayjs(`1970-01-01 ${props.session.end_time}`)

  const durationInMinutes = endTime.diff(startTime, 'minute')

  return `${durationInMinutes} minutes`
}

function getSpeakers() {
  return JSON.parse(props.session.speakers)
}
</script>
